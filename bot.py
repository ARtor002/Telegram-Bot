import os
import zipfile
import patoolib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! فایل خود را ارسال کنید تا پردازش شود.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.video
    if not file:
        return
    
    file_path = os.path.join(DOWNLOAD_PATH, file.file_name)
    new_file = await file.get_file()
    await new_file.download_to_drive(file_path)
    
    keyboard = [
        [InlineKeyboardButton("📂 استخراج فایل", callback_data=f"extract_{file.file_name}")],
        [InlineKeyboardButton("📝 تغییر نام", callback_data=f"rename_{file.file_name}")],
        [InlineKeyboardButton("🗜️ فشرده‌سازی", callback_data=f"compress_{file.file_name}")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"✅ فایل `{file.file_name}` با موفقیت دانلود شد. \nلطفاً عملیات مورد نظر را انتخاب کنید:", reply_markup=reply_markup)

async def extract_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    file_name = query.data.split("_", 1)[1]
    file_path = os.path.join(DOWNLOAD_PATH, file_name)
    extract_path = os.path.join(DOWNLOAD_PATH, file_name + "_extracted")
    os.makedirs(extract_path, exist_ok=True)
    
    try:
        if file_name.endswith(".rar"):
            patoolib.extract_archive(file_path, outdir=extract_path)
        elif file_name.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        await query.message.reply_text(f"✅ فایل `{file_name}` استخراج شد و در `{extract_path}` ذخیره شد.")
    except Exception as e:
        await query.message.reply_text(f"❌ خطا در استخراج فایل: {str(e)}")

async def rename_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    file_name = query.data.split("_", 1)[1]
    file_path = os.path.join(DOWNLOAD_PATH, file_name)
    new_name = "renamed_" + file_name
    new_path = os.path.join(DOWNLOAD_PATH, new_name)
    os.rename(file_path, new_path)
    await query.message.reply_text(f"✅ فایل `{file_name}` به `{new_name}` تغییر نام یافت.")

async def compress_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    file_name = query.data.split("_", 1)[1]
    file_path = os.path.join(DOWNLOAD_PATH, file_name)
    compressed_path = file_path + ".zip"
    
    try:
        with zipfile.ZipFile(compressed_path, 'w') as zipf:
            zipf.write(file_path, arcname=file_name)
        await query.message.reply_text(f"✅ فایل `{file_name}` فشرده شد و در `{compressed_path}` ذخیره شد.")
    except Exception as e:
        await query.message.reply_text(f"❌ خطا در فشرده‌سازی فایل: {str(e)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data.startswith("extract_"):
        await extract_file(update, context)
    elif query.data.startswith("rename_"):
        await rename_file(update, context)
    elif query.data.startswith("compress_"):
        await compress_file(update, context)

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL, handle_file))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 بات در حال اجراست...")
    app.run_polling()
