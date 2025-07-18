# رفع مشکل فایل‌های بزرگ

## تغییرات اعمال شده:

### 1. بهبود ارسال فایل در `bot.py`
- حذف شرط بررسی اندازه فایل (50MB)
- استفاده از Client API برای همه فایل‌ها
- اضافه کردن fallback به Bot API در صورت شکست Client API

### 2. بهبود `telegram_client.py`
- اضافه کردن بررسی وجود فایل
- اضافه کردن نمایش پیشرفت ارسال
- بهبود مدیریت خطاها

### 3. تغییرات کلیدی:

#### قبل:
```python
if file_size > 50 * 1024 * 1024:  # 50MB
    # استفاده از Client API
else:
    # استفاده از Bot API
```

#### بعد:
```python
# برای همه فایل‌ها از Client API استفاده کن
success = await send_file_with_client_api(...)
if not success:
    # fallback به Bot API
```

## نحوه تست:

1. فایل تست را اجرا کنید:
```bash
python test_large_file.py
```

2. یا مستقیماً ربات را اجرا کنید:
```bash
python bot.py
```

## نکات مهم:

- اطمینان حاصل کنید که `API_ID` و `API_HASH` در فایل `config.py` تنظیم شده‌اند
- فایل `bot_session.session` پس از اولین اجرا ایجاد می‌شود
- برای فایل‌های بسیار بزرگ (>2GB) ممکن است نیاز به تقسیم فایل باشد

## محدودیت‌ها:

- حداکثر اندازه فایل در تلگرام: 2GB
- برای فایل‌های بزرگتر از 2GB، فایل به صورت خودکار تقسیم می‌شود 