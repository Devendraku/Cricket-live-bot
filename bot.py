import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CRIC_API_KEY = os.getenv("CRIC_API_KEY")

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

            message += f"*{name}*\n"
            message += f"{score_text}"
            message += f"Status: {status}\n"
            message += "────────────────\n"

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

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("score", score))
    print("Bot successfully started...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
