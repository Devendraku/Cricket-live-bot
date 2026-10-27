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
    url = "https://api.cricwix.com/ext/v1/fixtures?status=live"
    headers = {"X-Api-Key": CRICWIX_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()

        if not data.get("success"):
            return "❌ Score abhi nahi mil raha."

        fixtures = data.get("data", {}).get("fixtures", []) or data.get("data", [])
        
        if not fixtures:
            return "Abhi koi live match nahi chal raha."

        message = "🏏 *Live Cricket Scores*\n\n"

        for match in fixtures[:6]:
            # Different possible structures handle kar rahe hain
            name = match.get("name") or match.get("match_title") or match.get("title") or "Match"
            
            local = match.get("localteam") or match.get("team1") or {}
            visitor = match.get("visitorteam") or match.get("team2") or {}
            
            if isinstance(local, dict):
                local_name = local.get("team_name") or local.get("name") or "Team 1"
            else:
                local_name = str(local)
                
            if isinstance(visitor, dict):
                visitor_name = visitor.get("team_name") or visitor.get("name") or "Team 2"
            else:
                visitor_name = str(visitor)

            local_score = match.get("localteam_score") or match.get("team1_score") or match.get("score1") or ""
            visitor_score = match.get("visitorteam_score") or match.get("team2_score") or match.get("score2") or ""
            
            status = match.get("status") or match.get("match_status") or "Live"

            message += f"*{name}*\n"
            message += f"• {local_name}: {local_score}\n"
            message += f"• {visitor_name}: {visitor_score}\n"
            message += f"Status: {status}\n"
            message += "────────────────\n"

        return message

    except Exception as e:
        return f"Error: {str(e)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste! 🏏\n\n"
        "Commands:\n"
        "/score - Live scores\n"
        "/help - Help"
    )

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Score la raha hoon... ⏳")
    result = get_live_scores()
    await update.message.reply_text(result, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏏 Live Cricket Score Bot\n\n"
        "/score - Live matches\n"
        "/help - Yeh message"
    )

async def main():
    keep_alive()
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("score", score))
    application.add_handler(CommandHandler("help", help_command))
    
    print("Bot started with Cricwix...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
