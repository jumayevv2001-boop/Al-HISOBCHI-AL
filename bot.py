from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TOKEN


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text or ""
    await update.message.reply_text(f"AL HISOBCHI AI xabar oldi:\n\n{msg}")


app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.ALL, handle))

if __name__ == "__main__":
    app.run_polling()
