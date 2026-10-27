import os
import requests
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CRICWIX_API_KEY = os.getenv("CRICWIX_API_KEY")

# ---------- Keep Alive ----------
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Cricket Live Score Bot is Running with Cricwix!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()
# --------------------------------

def get_live_scores():
    url = "https://api.cricwix.com/ext/v1/fixtures?status=live"
    headers = {
        "X-Api-Key": CRICWIX_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        data = response.json()

        if not data.get("success"):
            return "❌ Score abhi nahi mil raha. Thodi der baad try karo."

        fixtures = data.get("data", {}).get("fixtures", [])
        if not fixtures:
            return "Abhi koi live match nahi chal raha."

        message = "🏏 *Live Cricket Scores*\n\n"

        for match in fixtures[:8]:
            local = match.get("localteam", {})
            visitor = match.get("visitorteam", {})
            
            local_name = local.get("team_name", "Team 1") if isinstance(local, dict) else str(local)
            visitor_name = visitor.get("team_name", "Team 2") if isinstance(visitor, dict) else str(visitor)
            
            local_score = match.get("localteam_score", "")
            visitor_score = match.get("visitorteam_score", "")
            status = match.get("status", "Live")
            match_name = match.get("name") or f"{local_name} vs {visitor_name}"

            message += f"*{match_name}*\n"
            if local_score:
                message += f"• {local_name}: {local_score}\n"
            if visitor_score:
                message += f"• {visitor_name}: {visitor_score}\n"
            message += f"Status: {status}\n"
            message += "────────────────\n"

        return message

    except Exception as e:
        return f"Error aaya: {str(e)}"


def get_upcoming_matches():
    url = "https://api.cricwix.com/ext/v1/fixtures?status=upcoming"
    headers = {
        "X-Api-Key": CRICWIX_API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        data = response.json()

        if not data.get("success"):
            return "❌ Upcoming matches nahi mil rahe."

        fixtures = data.get("data", {}).get("fixtures", [])
        if not fixtures:
            return "Koi upcoming match nahi mila."

        message = "📅 *Upcoming Cricket Matches*\n\n"
        count = 0
        
        for match in fixtures:
            local = match.get("localteam", {})
            visitor = match.get("visitorteam", {})
            
            local_name = local.get("team_name", "Team 1") if isinstance(local, dict) else str(local)
            visitor_name = visitor.get("team_name", "Team 2") if isinstance(visitor, dict) else str(visitor)
            
            date = match.get("starting_at") or match.get("date", "Date nahi mili")
            match_name = match.get("name") or f"{local_name} vs {visitor_name}"

            message += f"*{match_name}*\n"
            message += f"📅 {date}\n"
            message += "────────────────\n"

            count += 1
            if count >= 8:
                break

        return message if count > 0 else "Abhi koi upcoming match nahi dikh raha."

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
        "/start - Bot start\n"
        "/score - Live scores\n"
        "/upcoming - Upcoming matches\n"
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
    
    print("Bot successfully started with Cricwix...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
