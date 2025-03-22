import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from pymongo import MongoClient
import rarfile

from config import TOKEN, MONGO_URI, DOWNLOAD_DIR, EXTRACT_DIR

# راه‌اندازی logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# اتصال به دیتابیس MongoDB
client = MongoClient(MONGO_URI)
db = client["telegram_bot"]
files_collection = db["files"]

async def start(update: Update, context):
    await update.message.reply_text("سلام! من بات تلگرام شما هستم.")

# ذخیره فایل‌ها در دیتابیس
async def handle_file(update: Update, context):
    file = update.message.document
    file_name = file.file_name
    file_path = os.path.join(DOWNLOAD_DIR, file_name)
    file_id = file.file_id

    # ذخیره فایل در دیتابیس
    file_info = {"file_id": file_id, "file_name": file_name, "path": file_path}
    files_collection.insert_one(file_info)

    # دانلود فایل
    new_file = await update.message.document.get_file()
    print(f"دریافت فایل: {file_name}")
    await new_file.download_to_drive(file_path)
    await update.message.reply_text(f"فایل {file_name} با موفقیت دانلود شد.")

# استخراج فایل فشرده
async def check_and_extract(update: Update, file_name: str):
    base_name = file_name.split(".part")[0] if ".part" in file_name else file_name.split(".")[0]
    all_parts = list(files_collection.find({"file_name": {"$regex": f"^{base_name}"}}))

    if all_parts and all_parts[0]["file_name"].endswith(".part1.rar"):
        part_numbers = sorted([int(f["file_name"].split(".part")[-1].split(".rar")[0]) for f in all_parts])
        expected_parts = list(range(1, max(part_numbers) + 1))

        if part_numbers == expected_parts:
            input_path = os.path.join(DOWNLOAD_DIR, all_parts[0]["file_name"])
            extract_path = os.path.join(EXTRACT_DIR, base_name)

            os.makedirs(extract_path, exist_ok=True)
            try:
                with rarfile.RarFile(input_path) as rarf:
                    rarf.extractall(extract_path)
                await update.message.reply_text(f"استخراج کامل شد: {extract_path}")

            except rarfile.BadRarFile:
                await update.message.reply_text("فایل مشکل دارد یا خراب است!")
            except rarfile.RarCannotExec:
                await update.message.reply_text("لطفاً `unrar` را نصب کنید!")
            except rarfile.PasswordRequired:
                await update.message.reply_text("این فایل فشرده دارای رمز عبور است. لطفاً رمز را ارسال کنید.")
                context.user_data["extract_file"] = input_path

async def receive_password(update: Update, context):
    if "extract_file" not in context.user_data:
        await update.message.reply_text("هیچ فایلی برای رمزگذاری در انتظار نیست!")
        return

    password = update.message.text
    input_path = context.user_data["extract_file"]
    extract_path = os.path.join(EXTRACT_DIR, os.path.basename(input_path))

    try:
        with rarfile.RarFile(input_path) as rarf:
            rarf.extractall(extract_path, pwd=password)
        await update.message.reply_text(f"استخراج با موفقیت انجام شد: {extract_path}")

    except rarfile.BadRarFile:
        await update.message.reply_text("فایل مشکل دارد یا خراب است!")
    except rarfile.PasswordRequired:
        await update.message.reply_text("رمز نادرست است! دوباره امتحان کنید.")

    del context.user_data["extract_file"]

# راه‌اندازی بات
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password))

    application.run_polling()

if __name__ == "__main__":
    main()
