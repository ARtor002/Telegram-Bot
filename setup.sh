#!/bin/bash

echo "🤖 نصب و راه‌اندازی ربات تلگرامی مدیریت فایل"
echo "=================================================="

# بررسی Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 نصب نیست. لطفاً Python3 را نصب کنید."
    exit 1
fi

echo "✅ Python3 موجود است."

# بررسی pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 نصب نیست. لطفاً pip3 را نصب کنید."
    exit 1
fi

echo "✅ pip3 موجود است."

# نصب وابستگی‌ها
echo "📦 نصب وابستگی‌های Python..."
pip3 install -r requirements.txt

# نصب ابزارهای سیستمی
echo "🔧 نصب ابزارهای سیستمی..."

if command -v apt-get &> /dev/null; then
    echo "🐧 سیستم‌عامل Ubuntu/Debian تشخیص داده شد."
    sudo apt-get update
    sudo apt-get install -y unrar rar p7zip-full
elif command -v yum &> /dev/null; then
    echo "🔴 سیستم‌عامل CentOS/RHEL تشخیص داده شد."
    sudo yum install -y unrar rar p7zip
elif command -v brew &> /dev/null; then
    echo "🍎 macOS تشخیص داده شد."
    brew install unrar p7zip
else
    echo "⚠️  سیستم‌عامل تشخیص داده نشد. لطفاً ابزارهای فشرده‌سازی را دستی نصب کنید."
fi

# ایجاد دایرکتوری‌ها
echo "📁 ایجاد دایرکتوری‌ها..."
mkdir -p downloads extracted temp

# کپی فایل نمونه env
if [ ! -f .env ]; then
    echo "⚙️  ایجاد فایل .env..."
    cp .env.example .env
    echo "📝 لطفاً فایل .env را ویرایش کرده و توکن ربات خود را وارد کنید."
fi

echo ""
echo "✅ نصب کامل شد!"
echo ""
echo "📋 مراحل بعدی:"
echo "1. توکن ربات خود را از @BotFather دریافت کنید"
echo "2. فایل config.py را ویرایش کرده و آی‌دی خود را در ADMIN_IDS اضافه کنید"
echo "3. متغیر BOT_TOKEN را تنظیم کنید:"
echo "   export BOT_TOKEN='YOUR_BOT_TOKEN'"
echo "4. ربات را اجرا کنید:"
echo "   python3 bot.py"
echo ""
echo "🔗 برای راهنمای کامل، فایل README.md را مطالعه کنید."
echo ""
echo "🚀 موفق باشید!"