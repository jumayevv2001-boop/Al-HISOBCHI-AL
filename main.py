import os
import json
import logging
import asyncio
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Web Server Render talabi uchun
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot status: Running 24/7"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# OpenAI API client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"clients": {}}
    return {"clients": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Assalomu alaykum! Men sizning **AI Hisobchingizman**.\n\n"
        "🎙 **Ovozli xabar** yuborishingiz yoki matn ko'rinishida yozishingiz mumkin.\n\n"
        "**Misollar:**\n"
        "• *'Ali 500 kg korma oldi'*\n"
        "• *'Ali 1000000 so'm berdi'*\n"
        "• *'Ali qancha yuk oldi va qancha qarzi bor?'*\n\n"
        "📋 Barcha mijozlar ro'yxati: /klientlar"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def process_text_with_ai(user_text: str):
    data = load_data()
    system_prompt = f"""
    Siz ombor va mijozlar hisobini yurituvchi aqlli AI hisobchisiz.
    Hozirgi mijozlar bazasi (JSON):
    {json.dumps(data, ensure_ascii=False)}

    Foydalanuvchi xabari: "{user_text}"

    Vazifangiz:
    1. Agar yangi yuk kelsa yoki to'lov bo'lsa, ma'lumotni tushunib, bazani qanday yangilash kerakligini hamda foydalanuvchiga tasdiq javobini bering.
    2. Mijozlar qarzi va yuklari so'ralsa, aniq hisob-kitob qilib javob bering.
    3. Javob qisqa va aniq o'zbek tilida bo'lsin.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}]
    )
    return response.choices[0].message.content

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    ai_response = await process_text_with_ai(user_text)
    await update.message.reply_text(ai_response, parse_mode="Markdown")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🎙 Ovozli xabar eshitilmoqda...")
    
    voice_file = await update.message.voice.get_file()
    file_path = "voice.ogg"
    await voice_file.download_to_drive(file_path)

    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                language="uz"
            )
        
        recognized_text = transcript.text
        await msg.edit_text(f"📝 **Tushunilgan matn:**\n_{recognized_text}_", parse_mode="Markdown")

        ai_response = await process_text_with_ai(recognized_text)
        await update.message.reply_text(ai_response, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Xatolik yuz berdi: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

async def clients_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    clients = data.get("clients", {})
    if not clients:
        await update.message.reply_text("Hozircha hech qanday mijoz kiritilmagan.")
        return

    res = "📋 **Mijozlar ro'yxati:**\n\n"
    for name, info in clients.items():
        res += f"• **{name}**: {info.get('total_qty', 0)} kg yuk | Qarz: {info.get('balance', 0):,} so'm\n"
    await update.message.reply_text(res, parse_mode="Markdown")

def main():
    # Flask veb serverini orqa fonda ishga tushirish
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("BOT_TOKEN topilmadi!")
        return

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("klientlar", clients_list))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.run_polling()

if __name__ == '__main__':
    main()




