# استفاده از Python 3.9 تصویر رسمی
FROM python:3.9-slim

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y \
    unrar \
    rar \
    p7zip-full \
    && rm -rf /var/lib/apt/lists/*

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های requirements
COPY requirements.txt .

# نصب وابستگی‌های Python
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد اپلیکیشن
COPY . .

# ایجاد دایرکتوری‌های مورد نیاز
RUN mkdir -p downloads extracted temp

# اجرای ربات
CMD ["python", "bot.py"]