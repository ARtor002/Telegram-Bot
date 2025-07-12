import os
import asyncio
from telethon import TelegramClient
from telethon.tl.types import InputPeerUser
from config import API_ID, API_HASH, BOT_TOKEN

class TelegramClientManager:
    def __init__(self):
        self.client = None
        
    async def initialize(self):
        """راه‌اندازی کلاینت تلگرام"""
        if not self.client:
            self.client = TelegramClient('bot_session', API_ID, API_HASH)
            await self.client.start(bot_token=BOT_TOKEN)
    
    async def send_large_file(self, chat_id: int, file_path: str, caption: str = ""):
        """ارسال فایل بزرگ با استفاده از Telegram Client API"""
        try:
            await self.initialize()
            
            # بررسی وجود فایل
            if not os.path.exists(file_path):
                print(f"فایل وجود ندارد: {file_path}")
                return False
            
            # بررسی اندازه فایل
            file_size = os.path.getsize(file_path)
            print(f"ارسال فایل: {file_path}, اندازه: {file_size} bytes")
            
            # ارسال فایل
            await self.client.send_file(
                entity=chat_id,
                file=file_path,
                caption=caption,
                supports_streaming=True,
                progress_callback=self._progress_callback
            )
            return True
            
        except Exception as e:
            print(f"خطا در ارسال فایل: {e}")
            return False
    
    def _progress_callback(self, current, total):
        """نمایش پیشرفت ارسال فایل"""
        if total > 0:
            percentage = (current / total) * 100
            print(f"پیشرفت ارسال: {percentage:.1f}% ({current}/{total} bytes)")
    
    async def close(self):
        """بستن کلاینت"""
        if self.client:
            await self.client.disconnect()

# نمونه استفاده
telegram_client = TelegramClientManager() 