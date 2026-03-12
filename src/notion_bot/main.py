from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, BackgroundTasks
from notion_bot.telegram.tools import process_telegram_update

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/webhook")
async def telegram_webhook_handler(request: Request, background_tasks: BackgroundTasks):
    try:
        # Extract the JSON sent by Telegram
        update = await request.json()
        
        # Filter only text messages (ignore edits, events, etc.)
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"]
            
            # Delegate the heavy task to the background to respond quickly
            background_tasks.add_task(process_telegram_update, chat_id, text)
            
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error receiving webhook: {str(e)}")
        # Always return 200 to Telegram so it doesn't retry indefinitely
        return {"status": "error", "detail": str(e)}