import os
import requests
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CRIC_API_KEY = os.getenv("CRIC_API_KEY")

# ---------- Keep Alive ----------
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Cricket Live Score Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()
# --------------------------------

def get_live_scores():
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={CRIC_API_KEY}&offset=0"
    try:
        response = requests.get(url, timeout=12)
        data = response.json()

        if data.get("status") != "success":
            return "❌ Score abhi nahi mil raha. Thodi der baad try karo."

        matches = data.get("data", [])
        if not matches:
            return "Abhi koi live match nahi chal raha."

        message = "🏏 *Live Cricket Scores*\n\n"

        for match in matches[:8]:
            name = match.get("name", "Unknown Match")
            status = match.get("status", "")
            scores = match.get("score", [])

            score_text = ""
            for s in scores:
                team = s.get("team", "")
                runs = s.get("r", 0)
                wickets = s.get("w", 0)
                overs = s.get("o", 0)
                score_text += f"• {team}: {runs}/{wickets} ({overs} ov)\n"

            message += f"*{name}*\n{score_text}Status: {status}\n────────────────\n"

        return message

    except Exception as e:
        return f"Error aaya: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste! 🏏\n\n"
        "Main live cricket scores dikhata hoon.\n\n"
        "Command:\n"
        "/score - Live matches ke scores dekho"
    )

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Score fetch kar raha hoon... ⏳")
    result = get_live_scores()
    await update.message.reply_text(result, parse_mode="Markdown")

async def main():
    keep_alive()
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("score", score))
    
    print("Bot successfully started...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Bot ko continuously chalane ke liye
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
