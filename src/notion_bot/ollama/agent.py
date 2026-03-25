import json
import logging
from toon import encode
from pathlib import Path
from ollama import Client
from notion_bot.config.credentials import ollama_api_key
from notion_bot.config.prompt import system_prompt
from notion_bot.config.paths import HISTORY_FILE
from notion_bot.tools.crud import (
    add_expense,
    update_expense,
    delete_expense,
    search_expenses
)
logger = logging.getLogger(__name__)

MAX_ITERATIONS = 8

client = Client(
    host="https://ollama.com",
    headers={'Authorization': 'Bearer ' + ollama_api_key}
)

available_tools = {
    "add_expense": add_expense,
    "update_expense": update_expense,
    "delete_expense": delete_expense,
    "search_expenses": search_expenses
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


def answer(query: str) -> str | None:
    """
    Process a user query through an LLM agent loop that can
    call tools iteratively until a final response is produced.
    """
    history = load_history()
    windowed_history = apply_window(history)

    messages = [
        {"role": "system", "content": encode(system_prompt)},
        *windowed_history,
        {"role": "user", "content": query},
    ]

    assistant_reply = None

    for iteration in range(MAX_ITERATIONS):
        logger.debug("Iteration %d/%d", iteration + 1, MAX_ITERATIONS)

        try:
            response = client.chat(
                model="qwen3.5:397b-cloud",
                messages=messages,
                tools=[add_expense, update_expense, delete_expense, search_expenses],
            )
        except Exception as e:
            logger.error("Error calling the model: %s", e)
            break

        # No tool calls → final answer
        if not response.message.tool_calls:
            assistant_reply = response.message.content
            break

        # Append assistant message with tool calls to context
        messages.append(response.message)

        # Execute each tool call
        for tool_call in response.message.tool_calls:
            func_name = tool_call.function.name
            arguments = tool_call.function.arguments

            tool_fn = available_tools.get(func_name)

            if tool_fn is None:
                logger.warning("Tool not found: '%s'", func_name)
                tool_result = f"Error: tool '{func_name}' is not available."
            else:
                try:
                    logger.info("Calling %s(%s)", func_name, arguments)
                    tool_result = tool_fn(**arguments)
                except Exception as e:
                    logger.error("Error executing %s: %s", func_name, e)
                    tool_result = f"Error executing '{func_name}': {e}"

            messages.append({
                "role": "tool",
                "content": str(tool_result),
            })
    else:
        # Exhausted all iterations without a final response
        logger.warning(
            "Reached the limit of %d iterations without a final response.",
            MAX_ITERATIONS,
        )
        # Force a final response without tools
        try:
            fallback = client.chat(
                model="qwen3.5:397b-cloud",
                messages=[
                    *messages,
                    {
                        "role": "user",
                        "content": (
                            "Summarize what you have done so far "
                            "and provide a final answer to the user."
                        ),
                    },
                ],
            )
            assistant_reply = fallback.message.content
        except Exception as e:
            logger.error("Error during fallback: %s", e)
            assistant_reply = "Sorry, an error occurred while processing your request."

    # Only persist history if we got a valid response
    if assistant_reply:
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": assistant_reply})
        save_history(history)

    return assistant_reply