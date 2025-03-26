import os
import logging
import asyncio
import zipfile
import py7zr
from pathlib import Path
from time import time
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# تنظیمات اولیه
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = set(map(int, os.getenv("ADMIN_IDS", "").split(",")))
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
COMPRESSED_DIR = BASE_DIR / "compressed"
EXTRACTED_DIR = BASE_DIR / "extracted"

# حالت‌های مکالمه
WAITING_PARTS, WAITING_PASSWORD, WAITING_RENAME, WAITING_ACTION = range(4)

# ایجاد دایرکتوری‌ها
for dir in [DOWNLOAD_DIR, COMPRESSED_DIR, EXTRACTED_DIR]:
    dir.mkdir(exist_ok=True)

# تنظیمات لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class UserState:
    def __init__(self):
        self.files = []
        self.current_file = None
        self.password = None
        self.rename_pattern = None


# --- توابع کمکی ---
def is_admin(user_id):
    return user_id in ADMINS


def get_user_plan(user_id):
    return "premium" if is_admin(user_id) else "normal"


def can_perform_action(user_id):
    if is_admin(user_id):
        return True
    # منطق چک کردن زمان برای کاربران عادی
    return True  # پیاده‌سازی کامل نیاز به دیتابیس دارد


async def send_progress(context, chat_id, text):
    return await context.bot.send_message(chat_id, f"⏳ {text}...")


# --- هندلرهای بات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 به بات مدیریت فایل خوش آمدید!")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not can_perform_action(user_id):
        await update.message.reply_text("⏳ لطفا 30 دقیقه بعد دوباره امتحان کنید!")
        return

    file = await get_file(update)
    if not file:
        return

    context.user_data["state"] = UserState()
    state = context.user_data["state"]

    # دریافت و ذخیره فایل
    file_path = DOWNLOAD_DIR / file.file_name
    await (await file.get_file()).download_to_drive(file_path)
    state.files.append(file_path)

    # نمایش منوی اقدامات
    keyboard = [
        [InlineKeyboardButton("✏️ تغییر نام", callback_data="rename")],
        [InlineKeyboardButton("📦 استخراج", callback_data="extract")],
    ]
    await update.message.reply_text(
        "عملیات مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAITING_ACTION


async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data
    state = context.user_data["state"]

    if action == "rename":
        await query.message.reply_text("نام جدید را وارد کنید:")
        return WAITING_RENAME
    elif action == "extract":
        return await extract_files(update, context)


async def rename_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_name = update.message.text
    state = context.user_data["state"]

    try:
        old_path = state.files[-1]
        new_path = old_path.parent / new_name
        old_path.rename(new_path)
        state.files[-1] = new_path
        await update.message.reply_text(f"✅ نام تغییر یافت به: {new_name}")
        return await handle_file(update, context)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")
        return ConversationHandler.END


async def extract_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data["state"]
    file_path = state.files[-1]

    try:
        if file_path.suffix == ".zip":
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(EXTRACTED_DIR)
        elif file_path.suffix == ".7z":
            with py7zr.SevenZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(EXTRACTED_DIR)

        # نمایش فایل‌های استخراج شده
        extracted_files = list(EXTRACTED_DIR.glob("*"))
        keyboard = [
            [InlineKeyboardButton(f.name, callback_data=f"send_{f.name}")]
            for f in extracted_files
        ]
        await update.message.reply_text(
            "فایل‌های استخراج شده:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_ACTION
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در استخراج: {str(e)}")
        return ConversationHandler.END


# --- تنظیمات و راه‌اندازی ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Document.ALL, handle_file)],
        states={
            WAITING_ACTION: [CallbackQueryHandler(handle_action)],
            WAITING_RENAME: [MessageHandler(filters.TEXT, rename_file)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(handle_action))

    app.run_polling()

if __name__ == "__main__":
    main()