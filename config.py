import os
from typing import List

# تنظیمات ربات
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# تنظیمات Telegram Client API (برای فایل‌های بزرگ)
API_ID = os.getenv("API_ID", "YOUR_API_ID_HERE")
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH_HERE")

ADMIN_IDS: List[int] = [
    # آی‌دی ادمین‌ها رو اینجا اضافه کنید
    108587157 #,مثال: 123456789
]

# تنظیمات فایل
DOWNLOAD_DIR = "downloads"
EXTRACTED_DIR = "extracted"
TEMP_DIR = "temp"
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB در بایت
TELEGRAM_MAX_FILE_SIZE = 1.9 * 1024 * 1024 * 1024  # 1.9GB محدودیت جدید
CHUNK_SIZE = 1024 * 1024  # 1MB chunks

# تنظیمات آرشیو
SUPPORTED_ARCHIVE_FORMATS = ['.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tar.bz2']
DEFAULT_COMPRESSION_LEVEL = 6

# پیام‌ها
MESSAGES = {
    'not_admin': "⛔ شما مجاز به استفاده از این ربات نیستید!",
    'start': "🤖 سلام! من ربات مدیریت فایل هستم.\n\n📁 فایل‌هایتان را ارسال کنید تا آن‌ها را مدیریت کنم.",
    'file_received': "✅ فایل دریافت شد: {filename}\n📊 تعداد فایل‌ها: {count}\n💾 حجم کل: {size}",
    'waiting_for_files': "📂 منتظر دریافت فایل‌های بیشتر...",
    'processing': "⚙️ در حال پردازش...",
    'error': "❌ خطا: {error}",
    'success': "✅ عملیات با موفقیت انجام شد!",
    'password_request': "🔐 رمز عبور را وارد کنید:",
    'rename_request': "✏️ نام جدید برای فایل‌ها را وارد کنید:",
    'archive_name_request': "📦 نام آرشیو را وارد کنید:",
    'extracting': "📤 در حال استخراج فایل‌ها...",
    'compressing': "📥 در حال فشرده‌سازی...",
    'uploading': "📤 در حال ارسال فایل‌ها...",
    'large_file_warning': "⚠️ فایل شما بزرگ است و ممکن است زمان بیشتری طول بکشد.",
}

# ایموجی‌های نمایش پیشرفت
PROGRESS_EMOJIS = ["▫️", "▪️", "⬛"]
