import os
import re
import json
from groq import Groq
from dotenv import load_dotenv
from tools import policy_tool, order_tool, register_order_tool

load_dotenv() # read .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key = GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

# tool definition (send to groq handle)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "policy_tool",
            "description": "Answers questions about company shipping, return, and refund policies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The customer's question about policy."
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "order_tool",
            "description": "Checks the status of an existing order by item number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_number": {
                        "type": "string",
                        "description": "The item/model number to check, e.g. X27."
                    }
                },
                "required": ["item_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "register_order_tool",
            "description": "Registers a new order for a customer once their name and item number are known.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The customer's full name."
                    },
                    "item_number": {
                        "type": "string",
                        "description": "The item/model number the customer wants to order, e.g. X27."
                    }
                },
                "required": ["name", "item_number"]
            }
        }
    }
]


def _call_tool(name, args):
    """Dispatch a tool call and return the result as a string."""
    if name == "policy_tool":
        return policy_tool(args.get("question", ""))
    elif name == "order_tool":
        return order_tool(args.get("item_number", ""))
    elif name == "register_order_tool":
        return register_order_tool(args.get("name", ""), args.get("item_number", ""))
    return "Tool not found."


def _clean_output(text: str) -> str:
    """
    Strip any leaked tool/function call syntax from the model's text response.
    Handles: full tags with content, empty tags, partial/malformed tags, JSON blobs.
    """
    if not text:
        return ""

    text = re.sub(r"<[a-zA-Z_]+>\s*\{.*?\}\s*</[a-zA-Z_]+>", "", text, flags=re.DOTALL)

    text = re.sub(r"<function[^>]*>.*?</function>", "", text, flags=re.DOTALL)
    text = re.sub(r"<tool[^>]*>.*?</tool>", "", text, flags=re.DOTALL)

    text = re.sub(r"<[a-zA-Z_]+\s*/>", "", text)

    text = re.sub(r"\b[a-zA-Z_]+>\s*</[a-zA-Z_]+>", "", text)

    text = re.sub(r"</?[a-zA-Z_]*tool[a-zA-Z_]*>", "", text)
    text = re.sub(r"</?[a-zA-Z_]*function[a-zA-Z_]*>", "", text)

    text = re.sub(r"\{[^{}]*\"item_number\"[^{}]*\}", "", text)
    text = re.sub(r"\{[^{}]*\"question\"[^{}]*\}", "", text)
    text = re.sub(r"\{[^{}]*\"name\"[^{}]*\}", "", text)

    bad_patterns = [
        "item_number=", "function=",
        "tool_call", "tool_use",
        "```json", "```",
    ]
    for p in bad_patterns:
        text = text.replace(p, "")

    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _build_system_prompt(user):
    """Build a system prompt that includes everything the agent knows about the customer."""
    name_info = f"The customer's name is {user['name']}." if user.get("name") else "The customer's name is not yet known."

    if user.get("orders"):
        orders_info = "The customer has the following registered orders: " + \
            ", ".join([o["item"] for o in user["orders"]]) + "."
    else:
        orders_info = "The customer has no registered orders yet."

    return f"""You are a helpful and friendly AI customer support agent for an e-commerce store that sells home appliances.

CUSTOMER MEMORY:
- {name_info}
- {orders_info}

YOUR BEHAVIOUR:
- Always greet the customer by name if you know it.
- If the customer wants to place an order, first ask which model/item they want (if not mentioned), then ask for their name (if not known), then call register_order_tool.
- If the customer asks about order status, call order_tool with their item number.
- If the customer asks about shipping, returns, or refunds, call policy_tool and answer based on its response.
- Be concise, warm, and professional.
- Never make up order statuses or policies — always use the tools.
- If you learn the customer's name during the conversation, remember to use it going forward.

VERY IMPORTANT — OUTPUT FORMAT:
- Your replies must be plain, natural conversational text only.
- NEVER output JSON, XML tags, function names, code blocks, or anything that looks like a tool call.
- NEVER write things like: <order_tool>{{"item_number": "X27"}}</order_tool> or item_number="X27" or any similar syntax.
- Tool calls happen automatically in the background. You only write what the customer sees.
- If you feel the urge to show a tool call, stop — just write a normal sentence instead.
"""


def run_agent(user, message):
    """
    Run the Groq-powered agent with tool calling.
    Handles multi-step tool use in a loop.
    """
    system_prompt = _build_system_prompt(user)

    messages = [{"role": "system", "content": system_prompt}] + user["history"]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024
        )

        choice = response.choices[0]

        if choice.finish_reason == "stop" or not choice.message.tool_calls:
            return _clean_output(choice.message.content)

        assistant_text = choice.message.content or ""

        tool_calls = choice.message.tool_calls

        messages.append({
            "role": "assistant",
            "content": assistant_text,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in tool_calls
            ]
        })

        for tc in tool_calls:
            tool_name = tc.function.name
            tool_args = json.loads(tc.function.arguments)
            tool_result = _call_tool(tool_name, tool_args)

            if tool_name == "register_order_tool":
                result_data = json.loads(tool_result)
                if result_data.get("success"):
                    item = tool_args.get("item_number", "").upper().strip()
                    user["orders"].append({"item": item, "status": "processing"})

            if tool_name == "register_order_tool" and tool_args.get("name"):
                user["name"] = tool_args["name"].strip().title()

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_result
            })