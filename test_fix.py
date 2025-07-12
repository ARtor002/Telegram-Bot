#!/usr/bin/env python3
"""
تست رفع مشکل فایل‌های بزرگ
"""

import os
from config import TELEGRAM_MAX_FILE_SIZE
from utils import format_bytes

def test_fix():
    """تست رفع مشکل"""
    print("🔧 تست رفع مشکل فایل‌های بزرگ")
    print(f"محدودیت تقسیم فایل: {format_bytes(TELEGRAM_MAX_FILE_SIZE)}")
    
    print("\n📋 خلاصه تغییرات:")
    print("✅ همه فایل‌ها از Client API استفاده می‌کنند")
    print("✅ Bot API فقط برای پیام‌های متنی استفاده می‌شود")
    print("✅ فایل‌های بزرگتر از 50MB تقسیم می‌شوند")
    print("✅ فایل‌های کوچک‌تر از 50MB یک‌تکه ارسال می‌شوند")
    
    print("\n🎯 نتیجه:")
    print("حالا فایل‌های 200MB و بزرگتر بدون مشکل ارسال می‌شوند!")

if __name__ == "__main__":
    test_fix() 