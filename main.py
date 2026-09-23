import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
        "Assalomu alaykum! Men AI Hisobchingizman.\n\n"
        "**Buyruqlar va misollar:**\n"
        "• *Yuk qo'shish:* `Ali 500 kg bug'doy oldi` yoki `Vali 200 kg yem oldi`\n"
        "• *Qarz/To'lov:* `Ali 1000000 som berdi`\n"
        "• *Mijoz hisobi:* `Ali` (mijoz nomini yozing)\n"
        "• *Barcha mijozlar:* /klientlar\n"
        "• *Oylik hisobot:* /hisobot"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    data = load_data()
    clients = data.setdefault("clients", {})

    words = msg.split()
    first_word = words[0].capitalize()

    # Agar shunchaki mijoz ismi yozilsa
    if len(words) == 1 and first_word in clients:
        c = clients[first_word]
        res = f"👤 **Mijoz:** {first_word}\n"
        res += f"📦 **Jami olingan yuk:** {c.get('total_qty', 0)} kg\n"
        res += f"💳 **Umumiy qarz/balans:** {c.get('balance', 0):,} so'm\n\n"
        res += "**So'nggi operatsiyalar:**\n"
        for h in c.get("history", [])[-5:]:
            res += f"• {h}\n"
        await update.message.reply_text(res, parse_mode="Markdown")
        return

    # Yuk yoki to'lov kiritish sodda mantig'i
    if len(words) >= 3:
        name = first_word
        if name not in clients:
            clients[name] = {"total_qty": 0, "balance": 0, "history": []}

        clients[name]["history"].append(msg)
        save_data(data)

        await update.message.reply_text(f"✅ **{name}** bo'yicha ma'lumot saqlandi!\n\nTo'liq ko'rish uchun `{name}` deb yozing.")
    else:
        await update.message.reply_text("Tushunmadim. Misol: `Ali 500 kg korma oldi` yoki `Ali` deb ismini yozing.")

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

