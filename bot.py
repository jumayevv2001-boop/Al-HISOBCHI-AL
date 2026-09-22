from telegram.ext import Application, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from config import TOKEN

async def handle(update:Update, context:ContextTypes.DEFAULT_TYPE):
    msg=update.message.text or ""
    await update.message.reply_text("AL HISOBCHI AI xabarni qabul qildi. PRO versiyada bu xabar avtomatik tahlil qilinadi.")

app=Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle))
app.run_polling()
