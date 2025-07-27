import os
import shutil
import zipfile
import rarfile
import py7zr
import tarfile
import math
from typing import List, Optional, Tuple
from pathlib import Path
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from config import SUPPORTED_ARCHIVE_FORMATS, MAX_FILE_SIZE, PROGRESS_EMOJIS
from telegram_client import telegram_client

# --- توابع کمکی برای نمایش و مدیریت فایل‌ها ---
def format_bytes(bytes_count: int) -> str:
    """تبدیل بایت به واحد قابل فهم (مثلاً 1.2 MB)"""
    if bytes_count == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(bytes_count, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_count / p, 2)
    return f"{s} {size_names[i]}"

def is_archive_file(filename: str) -> bool:
    """بررسی اینکه فایل آرشیو است یا نه (بر اساس پسوند)"""
    return any(filename.lower().endswith(ext) for ext in SUPPORTED_ARCHIVE_FORMATS)

def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """ایجاد نوار پیشرفت متنی برای نمایش درصد پیشرفت"""
    if total == 0:
        return "▫️" * length
    filled_length = int(length * current // total)
    bar = "▪️" * filled_length + "▫️" * (length - filled_length)
    percentage = round(100 * current / total, 1)
    return f"{bar} {percentage}%"

def get_custom_keyboard_for_files():
    """کیبورد کاستوم برای مدیریت فایل‌ها (اتمام/لغو)"""
    keyboard = [
        [KeyboardButton("✅ اتمام ارسال فایل‌ها")],
        [KeyboardButton("❌ لغو عملیات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_archive_format_keyboard():
    """کیبورد انتخاب فرمت آرشیو (ZIP/RAR)"""
    keyboard = [
        [InlineKeyboardButton("📦 ZIP", callback_data="format_zip")],
        [InlineKeyboardButton("📦 RAR", callback_data="format_rar")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_skip_keyboard():
    """کیبورد اسکیپ (رد کردن)"""
    keyboard = [[InlineKeyboardButton("⏭️ رد کردن", callback_data="skip")]]
    return InlineKeyboardMarkup(keyboard)

def get_action_keyboard():
    """کیبورد انتخاب عملیات برای فایل‌های فشرده (استخراج یا فشرده‌سازی مجدد)"""
    keyboard = [
        [InlineKeyboardButton("📤 ارسال غیر فشرده", callback_data="action_extract")],
        [InlineKeyboardButton("📦 تغییر آرشیو", callback_data="action_recompress")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_archive_action_keyboard():
    """کیبورد انتخاب عملیات برای فایل‌های فشرده (جدید)"""
    keyboard = [
        [InlineKeyboardButton("📤 استخراج و ارسال", callback_data="archive_action_extract")],
        [InlineKeyboardButton("📦 فشرده‌سازی مجدد", callback_data="archive_action_compress")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_continue_keyboard():
    """کیبورد ادامه کار (ارسال فایل بیشتر/اتمام/لغو)"""
    keyboard = [
        [KeyboardButton("📁 ارسال فایل بیشتر")],
        [KeyboardButton("✅ اتمام ارسال فایل‌ها")],
        [KeyboardButton("❌ لغو عملیات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def create_directories():
    """ایجاد دایرکتوری‌های مورد نیاز برای ذخیره فایل‌ها"""
    from config import DOWNLOAD_DIR, EXTRACTED_DIR, TEMP_DIR
    for directory in [DOWNLOAD_DIR, EXTRACTED_DIR, TEMP_DIR]:
        os.makedirs(directory, exist_ok=True)

def cleanup_temp_files(directory: str):
    """پاک کردن فایل‌های موقت و دایرکتوری‌های موقت"""
    if os.path.exists(directory):
        shutil.rmtree(directory)

# --- توابع اصلی پردازش فایل‌ها ---
async def send_file_with_client_api(chat_id: int, file_path: str, caption: str = "") -> bool:
    """ارسال فایل بزرگ با استفاده از Telegram Client API"""
    try:
        return await telegram_client.send_large_file(chat_id, file_path, caption)
    except Exception as e:
        print(f"خطا در ارسال فایل با Client API: {e}")
        return False

async def extract_archive(archive_path: str, extract_path: str, password: Optional[str] = None) -> bool:
    """استخراج فایل آرشیو با پشتیبانی از رمز و فرمت‌های مختلف"""
    try:
        if archive_path.lower().endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                if password:
                    zip_ref.setpassword(password.encode())
                zip_ref.extractall(extract_path)
        elif archive_path.lower().endswith('.rar'):
            with rarfile.RarFile(archive_path) as rar_ref:
                rar_ref.extractall(extract_path, pwd=password)
        elif archive_path.lower().endswith('.7z'):
            with py7zr.SevenZipFile(archive_path, mode='r', password=password) as seven_ref:
                seven_ref.extractall(extract_path)
        elif archive_path.lower().endswith(('.tar', '.tar.gz', '.tar.bz2')):
            mode = 'r'
            if archive_path.lower().endswith('.tar.gz'):
                mode = 'r:gz'
            elif archive_path.lower().endswith('.tar.bz2'):
                mode = 'r:bz2'
            with tarfile.open(archive_path, mode) as tar_ref:
                tar_ref.extractall(extract_path)
        return True
    except Exception as e:
        print(f"خطا در استخراج: {e}")
        return False

async def create_archive(source_path: str, archive_path: str, format_type: str, password: Optional[str] = None) -> bool:
    """ایجاد فایل آرشیو با فرمت و رمز دلخواه"""
    try:
        if format_type.lower() == 'zip':
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                if os.path.isdir(source_path):
                    for root, dirs, files in os.walk(source_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, source_path)
                            zip_ref.write(file_path, arcname)
                else:
                    zip_ref.write(source_path, os.path.basename(source_path))
                if password:
                    zip_ref.setpassword(password.encode())
        elif format_type.lower() == 'rar':
            # برای RAR از patoolib استفاده می‌کنیم
            import patoolib
            if password:
                # RAR با رمز نیاز به ابزار خاص دارد
                cmd = f'rar a -p{password} "{archive_path}" "{source_path}"'
                os.system(cmd)
            else:
                patoolib.create_archive(archive_path, [source_path])
        return True
    except Exception as e:
        print(f"خطا در ایجاد آرشیو: {e}")
        return False

def split_large_file(file_path: str, max_size: int = MAX_FILE_SIZE) -> List[str]:
    """تقسیم فایل بزرگ به قسمت‌های کوچک‌تر برای ارسال در تلگرام"""
    file_size = os.path.getsize(file_path)
    if file_size <= max_size:
        return [file_path]
    parts = []
    part_num = 1
    with open(file_path, 'rb') as source:
        while True:
            chunk = source.read(max_size)
            if not chunk:
                break
            part_path = f"{file_path}.part{part_num:03d}"
            with open(part_path, 'wb') as part_file:
                part_file.write(chunk)
            parts.append(part_path)
            part_num += 1
    return parts

def combine_parts(part_files: List[str], output_path: str) -> bool:
    """ترکیب قسمت‌های فایل به یک فایل واحد"""
    try:
        with open(output_path, 'wb') as output:
            for part_file in sorted(part_files):
                with open(part_file, 'rb') as part:
                    shutil.copyfileobj(part, output)
        return True
    except Exception as e:
        print(f"خطا در ترکیب فایل‌ها: {e}")
        return False

def rename_files_with_numbers(file_paths: List[str], base_name: str) -> List[Tuple[str, str]]:
    """تغییر نام فایل‌ها با شماره‌گذاری"""
    renamed_files = []
    for i, file_path in enumerate(file_paths, 1):
        file_ext = os.path.splitext(file_path)[1]
        new_name = f"{base_name}_{i:03d}{file_ext}"
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        try:
            os.rename(file_path, new_path)
            renamed_files.append((file_path, new_path))
        except Exception as e:
            print(f"خطا در تغییر نام {file_path}: {e}")
            renamed_files.append((file_path, file_path))
    return renamed_files

def get_total_size(file_paths: List[str]) -> int:
    """محاسبه حجم کل فایل‌های ارسالی"""
    total_size = 0
    for file_path in file_paths:
        if os.path.exists(file_path):
            total_size += os.path.getsize(file_path)
    return total_size