import os
import requests
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CRICWIX_API_KEY = os.getenv("CRICWIX_API_KEY")

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

def get_live_scores():
    url = "https://api.cricwix.com/ext/v1/fixtures?status=live"
    headers = {"X-Api-Key": CRICWIX_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()

        if not data.get("success"):
            return "❌ Score abhi nahi mil raha."

        fixtures = data.get("data", {}).get("fixtures", [])
        
        if not fixtures:
            return "Abhi koi live match nahi chal raha."

        message = "🏏 *Live Cricket Scores*\n\n"

        for match in fixtures[:6]:
            home = match.get("home_team", {})
            away = match.get("away_team", {})
            
            home_name = home.get("team_name", "Team 1")
            away_name = away.get("team_name", "Team 2")
            home_score = home.get("score", "-")
            away_score = away.get("score", "-")
            
            status = match.get("fixture_status", "Live")
            league = match.get("league", {}).get("name", "")

            message += f"*{home_name} vs {away_name}*\n"
            if league:
                message += f"🏆 {league}\n"
            message += f"• {home_name}: {home_score}\n"
            message += f"• {away_name}: {away_score}\n"
            message += f"Status: {status}\n"
            message += "────────────────\n"

        return message

    except Exception as e:
        return f"Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Namaste! 🏏\n\n"
        "Commands:\n"
        "/score - Live scores dekho\n"
        "/help - Help"
    )
    
    if update.message:
        await update.message.reply_text(text)
    elif update.channel_post:
        await update.channel_post.reply_text(text)

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Score la raha hoon... ⏳")
        result = get_live_scores()
        await update.message.reply_text(result, parse_mode="Markdown")
    elif update.channel_post:
        await update.channel_post.reply_text("Score la raha hoon... ⏳")
        result = get_live_scores()
        await update.channel_post.reply_text(result, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🏏 *Live Cricket Score Bot*\n\n"
        "/score - Live matches\n"
        "/help - Yeh message"
    )
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")
    elif update.channel_post:
        await update.channel_post.reply_text(text, parse_mode="Markdown")

async def main():
    keep_alive()
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("score", score))
    application.add_handler(CommandHandler("help", help_command))
    
    print("Bot started successfully with Channel support...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
