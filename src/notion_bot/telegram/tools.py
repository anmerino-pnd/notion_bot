import requests
from notion_bot.ollama.agent import answer
from notion_bot.config.credentials import telegram_bot_token 

def process_telegram_update(chat_id: int, text: str):
    """
    This function runs in the background. It calls Ollama and Notion,
    and once it's done, it sends a message back to the user on Telegram.
    """
    try:
        # 1. Your agent processes the message (this is where the ~20 seconds happen)
        bot_reply = answer(text)
    except Exception as e:
        print(f"Agent error: {e}")
        bot_reply = "There was an error processing your expense. Please try again."
        
    # 2. Send the response back to Telegram
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": bot_reply
    }
    requests.post(url, json=payload)