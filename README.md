# AI Customer Support Agent

A conversational AI customer support agent for an e-commerce store.

---

## Setup Instructions

### 1. Clone / download the project

```
CS_agent_bot/
├── app.py
├── agent.py
├── memory.py
├── tools.py
├── requirements.txt
└── templates/
    └── index.html
```

### 2. Install dependencies

```bash
cd .\cs_agent-main\
cd .\CS_agent_bot\
pip install -r requirements.txt
```

### 3. Get a free Groq API key

1. Go to https://console.groq.com
2. Sign up for a free account
3. Navigate to **API Keys** and create a new key
4. Remember to copy the API keys immediately because API key only generate once

### 4. Set your API key

**Windows:**
## Environment Setup

Create a new `.env` file in your path:
Paste your API keys from groq into "your_key_here"

GROQ_API_KEY = "your_key_here"

### 5. Run the app

```bash
python app.py
```

Then open your browser at **http://localhost:5000**

---

## Example Conversations

**Thread A — Placing an order:**
```
You:  I want to order a washing machine
Bot:  Sure! Which model are you looking for?
You:  X27
Bot:  Got it! May I have your name to proceed?
You:  It's Tom
Bot:  Okay Tom, your order for item X27 has been registered!
```

**Thread B — Checking order (memory persists):**
```
You:  Is my order here yet?
Bot:  Hi Tom, there is a small shortage of item X27, so delivery may take a few more days.
```

**Policy questions:**
```
You:  What is your return policy?
Bot:  You can return items within 30 days of delivery...
```

---

## System Design

### Architecture

```
User (Browser)
     │  HTTP POST /chat
     ▼
Flask App (app.py)
     │  loads user memory + history
     ▼
Agent (agent.py)  ◄──── Groq API (LLaMA 3 70B)
     │                        │
     │   tool_calls ──────────┘
     ▼
Tools (tools.py)
  ├── policy_tool()        → returns company policy text
  ├── order_tool()         → looks up order status by item number
  └── register_order_tool()→ registers a new order

Memory (memory.py)
  └── memory_store.json    → persists name, orders, chat history per user
```

### Key Design Decisions

| Decision | Reason |
|---|---|
| **Groq + LLaMA system** | Free, fast, supports native tool/function calling |
| **Tool calling (not keywords)** | The AI decides when to call tools naturally — no brittle if/else matching |
| **Persistent JSON memory** | Customer name, orders, and conversation history survive across threads |
| **Stable `user_id` in localStorage** | Ensures the same customer is recognised across Thread A and Thread B |
| **Agentic loop** | Agent keeps calling tools until it has enough info to reply — handles multi-step flows automatically |
| **System prompt with memory** | Customer name and order history injected into every request so the AI always knows who it's talking to |