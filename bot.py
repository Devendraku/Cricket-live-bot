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
            return "❌ Score abhi nahi mil raha."

        matches = data.get("data", [])
        if not matches:
            return "Abhi koi live match nahi chal raha."

        message = "🏏 *Live Cricket Scores*\n\n"
        for match in matches[:8]:
            name = match.get("name", "Unknown")
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
        return f"Error: {str(e)}"


def get_upcoming_matches():
    url = f"https://api.cricapi.com/v1/matches?apikey={CRIC_API_KEY}&offset=0"
    try:
        response = requests.get(url, timeout=12)
        data = response.json()

        if data.get("status") != "success":
            return "❌ Upcoming matches nahi mil rahe."

        matches = data.get("data", [])
        if not matches:
            return "Koi upcoming match nahi mila."

        message = "📅 *Upcoming Cricket Matches*\n\n"
        count = 0
        for match in matches:
            status = match.get("status", "").lower()
            # Sirf upcoming matches dikhayenge
            if "won" in status or "complete" in status or "finished" in status:
                continue

            name = match.get("name", "Unknown Match")
            date = match.get("date", "Date nahi mili")
            venue = match.get("venue", "")
            match_type = match.get("matchType", "")

            message += f"*{name}*\n"
            message += f"📅 Date: {date}\n"
            if venue:
                message += f"📍 Venue: {venue}\n"
            if match_type:
                message += f"Type: {match_type.upper()}\n"
            message += "────────────────\n"

            count += 1
            if count >= 8:
                break

        if count == 0:
            return "Abhi koi upcoming match nahi dikh raha."

        return message
    except Exception as e:
        return f"Error: {str(e)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste! 🏏\n\n"
        "Available Commands:\n"
        "/score - Live matches ke scores\n"
        "/upcoming - Aane wale matches\n"
        "/help - Help message"
    )

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Score la raha hoon... ⏳")
    result = get_live_scores()
    await update.message.reply_text(result, parse_mode="Markdown")

async def upcoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Upcoming matches la raha hoon... ⏳")
    result = get_upcoming_matches()
    await update.message.reply_text(result, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏏 *Cricket Live Score Bot*\n\n"
        "Commands:\n"
        "/start - Bot start karo\n"
        "/score - Live scores dekho\n"
        "/upcoming - Aane wale matches\n"
        "/help - Yeh message",
        parse_mode="Markdown"
    )

async def main():
    keep_alive()
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("score", score))
    application.add_handler(CommandHandler("upcoming", upcoming))
    application.add_handler(CommandHandler("help", help_command))
    
    print("Bot successfully started...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
