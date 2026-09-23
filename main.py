import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from config import TOKEN

# Web Service o'chib qolmasligi uchun Flask server
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot ishlamoqda!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# Flask'ni alohida potokda ishga tushirish
threading.Thread(target=run_flask).start()

# Telegram bot xabarlarni qayta ishlash
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text or ""
    await update.message.reply_text(f"AL HISOBCHI AI xabaringizni qabul qildi: {msg}")

# Botni sozlash va ishga tushirish
app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle))

if __name__ == "__main__":
    app.run_polling()

