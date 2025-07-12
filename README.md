# 🤖 ربات تلگرامی مدیریت فایل

ربات تلگرامی پیشرفته برای مدیریت، فشرده‌سازی و استخراج فایل‌ها با قابلیت‌های زیر:

## 🔥 ویژگی‌ها

### 📁 بخش مدیریت فایل‌های غیر فشرده:
- ✅ دریافت چندین فایل با کاستوم کیبورد
- 📊 نمایش تعداد و حجم کل فایل‌ها
- ✏️ تغییر نام فایل‌ها به صورت شماره‌دار (اختیاری)
- 📦 انتخاب نام آرشیو و رمز عبور (اختیاری)
- 🗜️ فشرده‌سازی با فرمت ZIP یا RAR
- ⚡ تقسیم فایل‌های بزرگ به پارت‌های کمتر از 2GB

### 📦 بخش مدیریت فایل‌های فشرده:
- 📥 دریافت فایل‌های فشرده در فرمت‌های مختلف
- 🔓 پشتیبانی از رمز عبور
- 🔄 انتخاب بین استخراج یا تغییر آرشیو
- 📤 ارسال فایل‌های استخراج شده یا آرشیو جدید

### 🔒 امنیت و مدیریت:
- 👤 دسترسی فقط برای ادمین‌ها
- 🗑️ پاک‌سازی خودکار فایل‌های موقت
- ❌ مدیریت خطاها و لغو عملیات
- 📊 نمایش گرافیکی پیشرفت

## 🚀 نصب و راه‌اندازی

### 1. دریافت کد

```bash
git clone https://github.com/your-username/telegram-file-manager-bot
cd telegram-file-manager-bot
```

### 2. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 3. نصب ابزارهای سیستمی (اختیاری برای RAR)

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install unrar rar p7zip-full
```

#### CentOS/RHEL:
```bash
sudo yum install unrar rar p7zip
```

#### Windows:
- دانلود WinRAR از [اینجا](https://www.win-rar.com/)
- دانلود 7-Zip از [اینجا](https://www.7-zip.org/)

### 4. تنظیمات

#### ایجاد ربات در BotFather:
1. به [@BotFather](https://t.me/BotFather) پیام دهید
2. دستور `/newbot` را ارسال کنید
3. نام و username ربات را وارد کنید
4. توکن دریافتی را کپی کنید

#### دریافت API ID و API Hash (برای فایل‌های بزرگ):
1. به [my.telegram.org](https://my.telegram.org) بروید
2. وارد حساب کاربری خود شوید
3. به بخش "API development tools" بروید
4. یک اپلیکیشن جدید ایجاد کنید
5. `API ID` و `API Hash` را کپی کنید

#### تنظیم متغیرهای محیطی:
فایل `env_example.txt` را کپی کرده و به `.env` تغییر نام دهید:

```bash
cp env_example.txt .env
```

سپس مقادیر را در فایل `.env` وارد کنید:

```env
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
```

یا در فایل `config.py` توکن خود را جایگزین کنید.

#### تنظیم آی‌دی ادمین‌ها:
در فایل `config.py`، آی‌دی تلگرام خود را اضافه کنید:

```python
ADMIN_IDS: List[int] = [
    123456789,  # آی‌دی شما
    987654321,  # آی‌دی ادمین دیگر
]
```

برای دریافت آی‌دی خود، به [@userinfobot](https://t.me/userinfobot) پیام دهید.

### 5. اجرای ربات

```bash
python bot.py
```

## 📱 نحوه استفاده

### شروع کار:
1. دستور `/start` را ارسال کنید
2. فایل‌های خود را ارسال کنید

## 📁 پشتیبانی از فایل‌های بزرگ

### مشکل اصلی:
Telegram Bot API محدودیت 50MB برای فایل‌های ارسالی دارد. برای حل این مشکل، ربات از دو روش استفاده می‌کند:

### روش‌های ارسال:
- **فایل‌های کوچک (کمتر از 50MB)**: استفاده از Telegram Bot API
- **فایل‌های بزرگ (بیشتر از 50MB)**: استفاده از Telegram Client API

### محدودیت‌ها:
- حداکثر حجم فایل: 2GB
- تقسیم خودکار فایل‌های بزرگ
- پشتیبانی از فایل‌های تا 2GB

برای اطلاعات بیشتر، فایل `SETUP_LARGE_FILES.md` را مطالعه کنید.

### برای فایل‌های غیر فشرده:
1. 📁 فایل‌ها را ارسال کنید
2. ✅ "اتمام ارسال فایل‌ها" را بزنید
3. 📝 نام جدید فایل‌ها را وارد کنید (یا Skip)
4. 📦 نام آرشیو را وارد کنید
5. 🔒 رمز عبور وارد کنید (یا Skip)
6. 📦 فرمت فشردگی (ZIP/RAR) را انتخاب کنید

### برای فایل‌های فشرده:
1. 📦 فایل فشرده را ارسال کنید
2. ✅ "اتمام ارسال فایل‌ها" را بزنید
3. 🔑 رمز فایل را وارد کنید (یا Skip)
4. 🔄 روش مورد نظر را انتخاب کنید:
   - **📤 ارسال غیر فشرده**: استخراج و ارسال فایل‌ها
   - **📦 تغییر آرشیو**: ایجاد آرشیو جدید

## 🌐 سرورهای رایگان برای اجرای ربات

### 1. Heroku (توصیه شده) 
🆓 **رایگان تا 1000 ساعت در ماه**

#### راه‌اندازی:
```bash
# نصب Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# لاگین
heroku login

# ایجاد اپ
heroku create your-bot-name

# تنظیم متغیر محیطی
heroku config:set BOT_TOKEN="YOUR_BOT_TOKEN"

# ایجاد Procfile
echo "worker: python bot.py" > Procfile

# دیپلوی
git add .
git commit -m "Deploy bot"
git push heroku main

# راه‌اندازی worker
heroku ps:scale worker=1
```

### 2. Railway
🆓 **رایگان تا $5 اعتبار ماهانه**

1. به [Railway.app](https://railway.app) بروید
2. از GitHub متصل شوید
3. پروژه را وارد کنید
4. متغیر `BOT_TOKEN` را تنظیم کنید
5. دیپلوی کنید

### 3. Render
🆓 **رایگان با محدودیت**

1. به [Render.com](https://render.com) بروید
2. Web Service جدید ایجاد کنید
3. مخزن GitHub را متصل کنید
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python bot.py`

### 4. PythonAnywhere
🆓 **رایگان با محدودیت روزانه**

```bash
# آپلود فایل‌ها
# در کنسول PythonAnywhere:
cd ~
git clone https://github.com/your-username/telegram-file-manager-bot
cd telegram-file-manager-bot
pip3.10 install --user -r requirements.txt

# ایجاد Always-On Task
python3.10 bot.py
```

### 5. Google Cloud Platform
🆓 **$300 اعتبار رایگان**

```bash
# نصب gcloud CLI
# ایجاد پروژه جدید
gcloud projects create your-project-id

# فعال‌سازی App Engine
gcloud app deploy
```

### 6. Oracle Cloud (پیشنهاد ویژه)
🆓 **Forever Free Tier**

```bash
# ایجاد VM رایگان
# نصب Python و وابستگی‌ها
sudo yum install python3 pip
pip3 install -r requirements.txt

# اجرا با systemd برای Always-On
sudo nano /etc/systemd/system/telegram-bot.service
```

## 🔧 تنظیمات پیشرفته

### تغییر حداکثر اندازه فایل:
```python
# در config.py
MAX_FILE_SIZE = 1.5 * 1024 * 1024 * 1024  # 1.5GB
```

### اضافه کردن فرمت‌های آرشیو جدید:
```python
# در config.py
SUPPORTED_ARCHIVE_FORMATS = ['.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz']
```

## 🐛 رفع مشکلات

### خطای "unrar not found":
```bash
sudo apt-get install unrar
```

### خطای "rar not found":
```bash
sudo apt-get install rar
```

### خطای حافظه کم:
- اندازه فایل‌ها را کاهش دهید
- `MAX_FILE_SIZE` را کمتر کنید

### خطای توکن نامعتبر:
- توکن ربات را مجدداً بررسی کنید
- متغیر محیطی `BOT_TOKEN` را تنظیم کنید

## 📁 ساختار پروژه

```
telegram-file-manager-bot/
├── bot.py              # فایل اصلی ربات
├── config.py           # تنظیمات
├── utils.py            # توابع کمکی
├── requirements.txt    # وابستگی‌ها
├── README.md          # راهنما
├── downloads/         # فایل‌های دانلود شده
├── extracted/         # فایل‌های استخراج شده
└── temp/              # فایل‌های موقت
```

## 🤝 مشارکت

برای مشارکت در پروژه:
1. Fork کنید
2. تغییرات خود را اعمال کنید
3. Pull Request ارسال کنید

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

## 💡 ایده‌های بهبود

- [ ] پشتیبانی از فایل‌های ویدیویی و صوتی
- [ ] رمزگذاری پیشرفته AES
- [ ] پایگاه داده برای ذخیره تاریخچه
- [ ] ربات چند زبانه
- [ ] API برای اتصال خارجی
- [ ] پشتیبانی از Cloud Storage

## 📞 پشتیبانی

اگر مشکلی داشتید:
1. Issues در GitHub ایجاد کنید
2. مستندات را مطالعه کنید
3. کد نمونه‌ها را بررسی کنید

---

💎 **ساخته شده با ❤️ برای جامعه توسعه‌دهندگان ایرانی**