import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------------------------------------------------
# সরাসরি আপনার API Keys এখানে বসিয়ে দিন
TELEGRAM_TOKEN = "8428210900:AAGWef3x9zIpuzasi6aj5FhGuSQIcb2B2tc"
GEMINI_API_KEY = "AQ.Ab8RN6L4rBZT9oFZjE-FT22eDBqEaFgeSgpvV5xRDfIc6KUKfg"
# ---------------------------------------------------------

# Main Menu Keyboards
def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 নির্বাচন তথ্য ও সহায়তা", callback_data="btn_info"),
            InlineKeyboardButton("🎯 ক্যাম্পেইন স্ট্র্যাটেজি", callback_data="btn_strategy")
        ],
        [
            InlineKeyboardButton("📝 পোল/সার্ভে তৈরি", callback_data="btn_poll"),
            InlineKeyboardButton("💳 প্রিমিয়াম সেবা", callback_data="btn_premium")
        ],
        [
            InlineKeyboardButton("📞 আমাদের সাথে যোগাযোগ", callback_data="btn_contact")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🗳️ **AI Election & Campaign Assistant-এ স্বাগতম!**\n\n"
        "আমি আপনার কৃত্রিম বুদ্ধিমত্তা চালিত নির্বাচনী সহকারী। নিচের মেনু থেকে অপশন বেছে নিন অথবা সরাসরি প্রশ্ন লিখে পাঠান:"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# Inline Button Response Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "btn_info":
        text = "ℹ️ **নির্বাচন তথ্য:** নির্বাচনী আচরণবিধি, ভোটার নিয়মাবলী বা নির্বাচনী এলাকা সংক্রান্ত যেকোনো প্রশ্ন লিখে পাঠান।"
    elif query.data == "btn_strategy":
        text = "🎯 **ক্যাম্পেইন স্ট্র্যাটেজি:** এলাকাভিত্তিক প্রচারণার কৌশল, ডিজিটাল মার্কেটিং ও স্লোগান তৈরির জন্য আপনার ধারণা লিখে পাঠান।"
    elif query.data == "btn_poll":
        text = "📝 **পোল/সার্ভে:** জনমত জরিপ বা দ্রুত সার্ভে তৈরি করতে আমাদের সাথে যোগাযোগ করুন।"
    elif query.data == "btn_premium":
        text = "💳 **প্রিমিয়াম সেবা:**\n- কাস্টম এআই ক্যাম্পেইন প্যানেল\n- অ্যাডভান্সড এনালিটিক্স রিপোর্ট\n- ২৪/৭ ভিআইপি সাপোর্ট"
    elif query.data == "btn_contact":
        text = "📞 **যোগাযোগ:** যেকোনো প্রয়োজনে আমাদের সাথে কথা বলতে মেসেজ টাইপ করুন।"
    else:
        text = "অনুরোধটি প্রক্রিয়া করা সম্ভব হচ্ছে না।"

    await query.message.reply_text(text, parse_mode="Markdown")

# AI Text Message Handler (Gemini API)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Gemini REST API Endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"You are a professional Political Campaign & Election Advisor. Respond accurately, clearly, and politely in Bengali language to this input: {user_text}"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        
        if response.status_code == 200:
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = "দুঃখিত, এআই রেসপন্স তৈরিতে সাময়িক সমস্যা হচ্ছে।"
            logging.error(f"API Error: {res_data}")
            
    except Exception as e:
        logging.error(f"Request Exception: {e}")
        reply = "নেটওয়ার্ক ত্রুটি দেখা দিয়েছে। কিছুক্ষণ পর আবার চেষ্টা করুন।"

    await update.message.reply_text(reply, reply_markup=get_main_keyboard())

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers Registration
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
