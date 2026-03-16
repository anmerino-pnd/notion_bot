import json
from pathlib import Path
from toon import encode
from ollama import Client
from notion_bot.config.credentials import ollama_api_key
from notion_bot.config.prompt import system_prompt
from notion_bot.config.paths import HISTORY_FILE
from notion_bot.tools.crud import (
    add_expense,
    update_expense,
    delete_expense
)

client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + ollama_api_key}
)

available_tools = {
    "add_expense": add_expense,
    "update_expense": update_expense,
    "delete_expense": delete_expense
}


MAX_PAIRS = 10  

def load_history() -> list:
    """Loads the chat history from the JSON file."""
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(history: list) -> None:
    """Saves the chat history to the JSON file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def apply_window(history: list, max_pairs: int = MAX_PAIRS) -> list:
    """
    Applies a sliding window to the history.
    Each pair = 1 user message + 1 assistant message = 2 items.
    """
    max_messages = max_pairs * 2
    return history[-max_messages:] if len(history) > max_messages else history


def answer(query: str) -> str | None :
    history = load_history()
    windowed_history = apply_window(history)

    messages = [
        {
            "role": "system",
            "content": encode(system_prompt)
        },
        *windowed_history,  
        {
            "role": "user",
            "content": query
        }
    ]

    response = client.chat(
        model="qwen3.5:397b-cloud",
        messages=messages,
        tools=[add_expense, update_expense, delete_expense]
    )

    if response.message.tool_calls:
        messages.append(response.message)

        for tool_call in response.message.tool_calls:
            func_name = tool_call.function.name
            arguments = tool_call.function.arguments

            if func_name in available_tools:
                tool_result = available_tools[func_name](**arguments)

                messages.append({
                    "role": "tool",
                    "content": tool_result
                })

        final_response = client.chat(
            model="qwen3.5:397b-cloud",
            messages=messages,
        )
        assistant_reply = final_response.message.content

    else:
        assistant_reply = response.message.content 

    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": assistant_reply})
    save_history(history)

    return assistant_reply