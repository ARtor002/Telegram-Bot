#!/usr/bin/env python3
"""
تست محدودیت جدید 1.9GB
"""

import os
from config import TELEGRAM_MAX_FILE_SIZE
from utils import format_bytes

def test_new_limit():
    """تست محدودیت جدید"""
    print("🔧 تست محدودیت جدید تقسیم فایل")
    print(f"محدودیت قبلی: 50MB")
    print(f"محدودیت جدید: {format_bytes(TELEGRAM_MAX_FILE_SIZE)}")
    
    # تست فایل‌های مختلف
    test_sizes = [
        50 * 1024 * 1024,      # 50MB
        100 * 1024 * 1024,     # 100MB
        500 * 1024 * 1024,     # 500MB
        1024 * 1024 * 1024,    # 1GB
        1.5 * 1024 * 1024 * 1024,  # 1.5GB
        1.9 * 1024 * 1024 * 1024,  # 1.9GB
        2 * 1024 * 1024 * 1024,    # 2GB
    ]
    
    print("\n📊 نتایج تست:")
    for size in test_sizes:
        will_split = size > TELEGRAM_MAX_FILE_SIZE
        status = "✅ تقسیم می‌شود" if will_split else "❌ تقسیم نمی‌شود"
        print(f"فایل {format_bytes(size)}: {status}")
    
    print(f"\n🎯 نتیجه:")
    print(f"فایل‌های کوچک‌تر از {format_bytes(TELEGRAM_MAX_FILE_SIZE)} تقسیم نمی‌شوند")
    print(f"فایل‌های بزرگتر از {format_bytes(TELEGRAM_MAX_FILE_SIZE)} تقسیم می‌شوند")

if __name__ == "__main__":
    test_new_limit() 