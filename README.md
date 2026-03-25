# 🤖 Notion Expense Agent (with Ollama & Telegram)

An intelligent personal finance assistant powered by Large Language Models (LLMs),
running locally or in the cloud. It leverages *Function Calling* (Tools) to process
natural language, classify expenses, and execute CRUD operations (Create, Read, Update,
Delete) directly on a Notion database.

## 🚀 Architecture

* **Brain:** Ollama (qwen3.5 or multimodal models) with *Tool Calling* support.
* **Data Destination:** Official Notion API.
* **Structured Prompts:** Uses `python-toon` for lightweight and effective system instruction formatting.
* **Environment Management:** `uv` for fast dependency resolution.

## 📋 Prerequisites

1. Install [uv](https://github.com/astral-sh/uv) as the package manager.
2. Have Python 3.13+ installed.
3. Create an **Internal Integration** in Notion and connect it to your database.
4. (Optional) A running Ollama server or instance.

## 🛠️ Setup

1. Clone the repository and install dependencies:
   ```bash
   uv venv
   uv pip install -e .
   uv sync
   ```
2. Set up your credentials in .env using .env.example:
   ```
   OLLAMA_API_KEY=""
   NOTION_INTEGRATION_TOKEN=""
   NOTION_PAGE_TOKEN=""
   NOTION_DB_KEY=""
   TELEGRAM_BOT_TOKEN=""
   ```

## Project Structure

```
notion_bot/
├── config/
│   ├── credentials.py    # API keys & tokens
|   └── paths.py	  # Paths of files 
│   └── prompt.py         # System prompt for Noti
├── tools/
│   └── crud.py           # add, update, delete expense functions
├── ollama/
│   └── agent.py 	  # Main answer() function & tool execution loop
└── main.py
data/
└── chat_history.json	  # Conversation's history
```

## How it works

```
User message
     ↓
Load history JSON  →  Apply sliding window (last 10 pairs)
     ↓
[system] + [history] + [query]  →  First call to the model
     ↓
   Tool calls?
  Yes          No
  ↓             ↓
Execute       Direct
the tools     response ✅
  ↓
Append tool result to context ("role": "tool")
  ↓
Second call to the model  →  Final natural response ✅
  ↓
Save pair to JSON
  ↓
Return response
```

## 🗂️ Expense Categories

| Category            | Examples                    |
| ------------------- | --------------------------- |
| Dining & Snacks     | Coffee, burger, gum, soda   |
| Shopping            | Clothes, electronics        |
| Groceries           | Supermarket, weekly shop    |
| Education           | Courses, books              |
| Health & Wellness   | Gym, pharmacy               |
| Transport           | Uber, gas, bus              |
| Travel & Lodging    | Hotels, flights             |
| Housing & Utilities | Rent, electricity, internet |
