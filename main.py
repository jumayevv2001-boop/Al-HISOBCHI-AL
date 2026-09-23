import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# OpenAI API kalitini olish
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"clients": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Assalomu alaykum! Men sizning **AI Hisobchingizman**.\n\n"
        "🎙 **Ovozli xabar** yuborishingiz yoki matn ko'rinishida yozishingiz mumkin.\n\n"
        "**Misollar:**\n"
        "• *'Ali 500 kg korma oldi'* (Yuk kiritish)\n"
        "• *'Ali 1000000 so'm pul berdi'* (To'lov kiritish)\n"
        "• *'Ali bir oyda qancha yuk oldi va qancha qarzi bor?'* (AI tahlili va ma'lumot olish)\n\n"
        "📋 Barcha mijozlar: /klientlar"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def process_text_with_ai(user_text: str):
    data = load_data()
    system_prompt = f"""
    Siz ombor va mijozlar hisobini yurituvchi aqlli AI hisobchisiz.
    Mavjud mijozlar va ombor bazasi (JSON):
    {json.dumps(data, ensure_ascii=False)}

    Foydalanuvchi matni: "{user_text}"

    Vazifangiz:
    1. Agar foydalanuvchi yangi yuk yoki to'lov haqida yozgan bo'lsa, ma'lumotni saqlang va tasdiqlang.
    2. Agar mijozning qarzi, olgan yuklari yoki bir oylik hisoboti haqida so'ralsa, bazadan aniq hisoblab javob bering.
    3. Javobingiz aniq, xushmuomala va o'zbek tilida bo'lsin.
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
    await update.message.reply_text("🎙 Ovozli xabar qabul qilindi, eshitilyapti...")
    
    # Ovozli faylni yuklab olish
    voice_file = await update.message.voice.get_file()
    file_path = "voice.ogg"
    await voice_file.download_to_drive(file_path)

    # Whisper AI orqali ovozni matnga o'girish
    with open(file_path, "rb") as audio_file:
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            language="uz"
        )
    
    recognized_text = transcript.text
    await update.message.reply_text(f"📝 **Tushunilgan matn:**\n_{recognized_text}_", parse_mode="Markdown")

    # Matnni AI orqali tahlil qilish
    ai_response = await process_text_with_ai(recognized_text)
    await update.message.reply_text(ai_response, parse_mode="Markdown")

    # Vaqtinchalik faylni o'chirish
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
        res += f"• **{name}**: {info.get('total_qty', 0)} kg yuk, Qarz: {info.get('balance', 0):,} so'm\n"
    await update.message.reply_text(res, parse_mode="Markdown")

if __name__ == '__main__':
    token = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("klientlar", clients_list))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    app.run_polling()



