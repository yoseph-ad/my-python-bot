from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['1', '2', '3', '4', '5']]
    await update.message.reply_text(
        "Rate today's food (1-5):",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {}

    if text in ['1','2','3','4','5']:
        user_data[user_id]['rating'] = text
        await update.message.reply_text("Write complaint or type 'skip'")
    else:
        complaint = text if text.lower() != 'skip' else ''
        rating = user_data[user_id].get('rating', '')

        print("User:", user_id, "Rating:", rating, "Complaint:", complaint)

        await update.message.reply_text("✅ Saved!")
        user_data[user_id] = {}

app = ApplicationBuilder().token("8778871682:AAFCy2u1ZMt7ZdgtAqgv11GlR769AzMOJNE").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.run_polling()
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Setup the connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Paste your JSON key details here or use a variable
creds = ServiceAccountCredentials.from_json_keyfile_name('your_key_file.json', scope)
client = gspread.authorize(creds)

# 2. Open the sheet
sheet = client.open("Cafe Feedback").sheet1

# 3. Use this function whenever a student submits a rating
def save_to_sheet(name, food, score, text):
    sheet.append_row([str(datetime.now()), name, food, score, text])

