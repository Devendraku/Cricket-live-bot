import os
import requests
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import json

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CRICWIX_API_KEY = os.getenv("CRICWIX_API_KEY")

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot chal raha hai.\n/score bhejo raw data dekhne ke liye.")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("API se data la raha hoon...")
    
    url = "https://api.cricwix.com/ext/v1/fixtures?status=live"
    headers = {"X-Api-Key": CRICWIX_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        
        # Pehle 1500 characters bhej rahe hain
        raw_text = json.dumps(data, indent=2)
        
        if len(raw_text) > 3500:
            raw_text = raw_text[:3500] + "\n\n... (baaki data cut ho gaya)"
        
        await update.message.reply_text(f"```\n{raw_text}\n```", parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def main():
    keep_alive()
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("score", score))
    
    print("Temporary bot started...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
