# AI Customer Support Agent

A conversational AI customer support agent for an e-commerce store, powered by **Groq** with real tool calling, persistent memory, and a clean web interface.

---

## Setup Instructions

### 1. Clone / download the project

```
cs_agent_bot/
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
pip install -r requirements.txt
```

### 3. Run the app

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
Agent (agent.py)  ◄──── Groq API (LLaMA)
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
