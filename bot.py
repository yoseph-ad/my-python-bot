# bot.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['cafe_feedback']
collection = db['feedbacks']

# Store user progress temporarily
user_data = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {}
    await update.message.reply_text("Welcome to Cafe Feedback Bot!\nPlease enter today's date (YYYY-MM-DD):")

# Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id not in user_data:
        user_data[user_id] = {}

    step = user_data[user_id].get("step", "date")

    if step == "date":
        user_data[user_id]["date"] = text
        user_data[user_id]["step"] = "food"
        await update.message.reply_text("Enter the food type:")
    elif step == "food":
        user_data[user_id]["food"] = text
        user_data[user_id]["step"] = "rating"
        keyboard = [['1', '2', '3', '4', '5']]
        await update.message.reply_text(
            "Rate today's food (1-5):",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        )
    elif step == "rating":
        if text not in ['1','2','3','4','5']:
            await update.message.reply_text("Please enter a number between 1 and 5.")
            return
        user_data[user_id]["rating"] = int(text)
        user_data[user_id]["step"] = "feedback"
        await update.message.reply_text("Any additional feedback? Type 'skip' to skip.")
    elif step == "feedback":
        feedback_text = "" if text.lower() == "skip" else text
        user_data[user_id]["feedback"] = feedback_text

        # Save to MongoDB
        collection.insert_one({
            "user_id": user_id,
            "date": user_data[user_id]["date"],
            "food": user_data[user_id]["food"],
            "rating": user_data[user_id]["rating"],
            "feedback": user_data[user_id]["feedback"],
            "submitted_at": datetime.now()
        })

        await update.message.reply_text("✅ Thank you! Your feedback has been saved.")
        user_data[user_id] = {}  # reset user data

# Set up the bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    print("Bot is running...")
    app.run_polling()
