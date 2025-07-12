#!/usr/bin/env python3
"""
تست عملکرد ارسال فایل‌های بزرگ
"""

import os
import asyncio
from telegram_client import telegram_client

async def test_large_file_sending():
    """تست ارسال فایل بزرگ"""
    try:
        # ایجاد فایل تست بزرگ (100MB)
        test_file = "test_large_file.bin"
        file_size = 100 * 1024 * 1024  # 100MB
        
        print(f"ایجاد فایل تست: {test_file} ({file_size} bytes)")
        
        with open(test_file, 'wb') as f:
            # نوشتن داده‌های تصادفی
            chunk_size = 1024 * 1024  # 1MB
            for i in range(file_size // chunk_size):
                f.write(os.urandom(chunk_size))
        
        print("فایل تست ایجاد شد. شروع تست ارسال...")
        
        # تست ارسال فایل
        chat_id = 108587157  # آی‌دی شما
        success = await telegram_client.send_large_file(
            chat_id, 
            test_file, 
            "🧪 فایل تست بزرگ (100MB)"
        )
        
        if success:
            print("✅ تست موفقیت‌آمیز بود!")
        else:
            print("❌ تست ناموفق بود!")
            
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
    
    finally:
        # پاک کردن فایل تست
        if os.path.exists(test_file):
            os.remove(test_file)
            print("فایل تست پاک شد.")
        
        # بستن کلاینت
        await telegram_client.close()

if __name__ == "__main__":
    asyncio.run(test_large_file_sending()) 