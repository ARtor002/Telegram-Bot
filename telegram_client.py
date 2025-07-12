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
            
            # ارسال فایل
            await self.client.send_file(
                entity=chat_id,
                file=file_path,
                caption=caption,
                supports_streaming=True
            )
            return True
            
        except Exception as e:
            print(f"خطا در ارسال فایل: {e}")
            return False
    
    async def close(self):
        """بستن کلاینت"""
        if self.client:
            await self.client.disconnect()

# نمونه استفاده
telegram_client = TelegramClientManager() 