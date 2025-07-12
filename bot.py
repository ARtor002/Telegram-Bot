import os
import shutil
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update, ReplyKeyboardRemove, Message
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)

from config import BOT_TOKEN, ADMIN_IDS, DOWNLOAD_DIR, EXTRACTED_DIR, TEMP_DIR, MESSAGES
from utils import (
    format_bytes, is_archive_file, create_progress_bar,
    get_custom_keyboard_for_files, get_archive_format_keyboard, 
    get_skip_keyboard, get_action_keyboard, get_archive_action_keyboard,
    get_continue_keyboard, create_directories,
    cleanup_temp_files, extract_archive, create_archive,
    split_large_file, rename_files_with_numbers, get_total_size,
    send_file_with_client_api
)

# راه‌اندازی logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# تعریف state ها برای ConversationHandler
(
    WAITING_FILES, WAITING_RENAME, WAITING_ARCHIVE_NAME, 
    WAITING_PASSWORD, WAITING_EXTRACT_PASSWORD, WAITING_NEW_ARCHIVE_NAME,
    WAITING_NEW_PASSWORD, CHOOSING_ACTION, WAITING_ARCHIVE_ACTION
) = range(9)

class FileManager:
    """
    مدیریت session هر کاربر برای ذخیره وضعیت فعلی عملیات
    """
    def __init__(self):
        self.user_sessions: Dict[int, Dict] = {}
        
    def get_session(self, user_id: int) -> Dict:
        """
        دریافت یا ایجاد session جدید برای هر کاربر
        """
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'files': [],
                'current_stage': None,
                'archive_format': 'zip',
                'archive_name': None,
                'password': None,
                'rename_pattern': None,
                'action': None
            }
        return self.user_sessions[user_id]
    
    def clear_session(self, user_id: int):
        """
        پاک کردن session کاربر (پس از اتمام یا لغو عملیات)
        """
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

file_manager = FileManager()

def admin_required(func):
    """
    دکوراتور برای محدود کردن دسترسی فقط به ادمین‌ها
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text(MESSAGES['not_admin'])
            return ConversationHandler.END
        return await func(update, context)
    return wrapper

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    شروع ربات و پاک‌سازی session قبلی کاربر
    """
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text(MESSAGES['not_admin'])
        return
    
    create_directories()  # اطمینان از وجود دایرکتوری‌های مورد نیاز
    file_manager.clear_session(user_id)
    await update.message.reply_text(MESSAGES['start'])

@admin_required
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    مدیریت فایل‌های دریافتی از کاربر (چه فشرده چه غیر فشرده)
    """
    user_id = update.effective_user.id
    session = file_manager.get_session(user_id)
    
    try:
        # دانلود فایل ارسالی
        file = update.message.document
        file_path = os.path.join(DOWNLOAD_DIR, file.file_name)
        
        # نمایش پیام پیشرفت دانلود
        progress_msg = await update.message.reply_text("📥 در حال دانلود...")
        
        # دانلود فایل به صورت محلی
        downloaded_file = await file.get_file()
        await downloaded_file.download_to_drive(file_path)
        
        # اضافه کردن فایل به session
        session['files'].append(file_path)
        
        # محاسبه تعداد و حجم کل فایل‌ها
        file_count = len(session['files'])
        total_size = get_total_size(session['files'])
        
        # بروزرسانی پیام پیشرفت
        await progress_msg.edit_text(
            MESSAGES['file_received'].format(
                filename=file.file_name,
                count=file_count,
                size=format_bytes(total_size)
            )
        )
        
        # اگر اولین فایل است، بررسی نوع فایل و نمایش کیبورد مناسب
        if file_count == 1:
            if is_archive_file(file.file_name):
                # اگر فایل فشرده است، از کاربر نوع عملیات را می‌پرسیم
                await update.message.reply_text(
                    "📦 فایل فشرده دریافت شد. چه عملیاتی می‌خواهید انجام دهید؟",
                    reply_markup=get_archive_action_keyboard()
                )
                session['current_stage'] = 'archive_action'
                return WAITING_ARCHIVE_ACTION
            else:
                # اگر فایل غیر فشرده است، کیبورد ارسال فایل بیشتر نمایش داده می‌شود
                await update.message.reply_text(
                    MESSAGES['waiting_for_files'],
                    reply_markup=get_custom_keyboard_for_files()
                )
                return WAITING_FILES
        else:
            # اگر فایل‌های بیشتری ارسال شد
            if session.get('current_stage') == 'archive_action':
                # اگر در مرحله انتخاب عملیات آرشیو هستیم
                await update.message.reply_text(
                    "📁 فایل اضافی دریافت شد. لطفاً ابتدا عملیات فایل قبلی را انتخاب کنید.",
                    reply_markup=get_archive_action_keyboard()
                )
                return WAITING_ARCHIVE_ACTION
            else:
                await update.message.reply_text(
                    MESSAGES['waiting_for_files'],
                    reply_markup=get_custom_keyboard_for_files()
                )
                return WAITING_FILES
            
    except Exception as e:
        await update.message.reply_text(MESSAGES['error'].format(error=str(e)))
        return ConversationHandler.END

async def handle_archive_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
    """مدیریت فایل‌های فشرده دریافتی"""
    await update.message.reply_text(
        "📦 فایل فشرده دریافت شد. آیا فایل‌های بیشتری دارید؟",
        reply_markup=get_custom_keyboard_for_files()
    )

async def finish_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اتمام دریافت فایل‌ها"""
    user_id = update.effective_user.id
    session = file_manager.get_session(user_id)
    
    if not session['files']:
        await update.message.reply_text("❌ هیچ فایلی دریافت نشده است!")
        return ConversationHandler.END
    
    # بررسی نوع فایل اول
    first_file = session['files'][0]
    
    if is_archive_file(os.path.basename(first_file)):
        # اگر در مرحله انتخاب عملیات آرشیو هستیم
        if session.get('current_stage') == 'archive_action':
            await update.message.reply_text(
                "📦 لطفاً ابتدا نوع عملیات را انتخاب کنید:",
                reply_markup=get_archive_action_keyboard()
            )
            return WAITING_ARCHIVE_ACTION
        else:
            # فایل فشرده - درخواست رمز
            await update.message.reply_text(
                MESSAGES['password_request'],
                reply_markup=ReplyKeyboardRemove()
            )
            await update.message.reply_text(
                "یا اگر رمز ندارد:",
                reply_markup=get_skip_keyboard()
            )
            return WAITING_EXTRACT_PASSWORD
    else:
        # فایل‌های غیر فشرده - درخواست تغییر نام
        await update.message.reply_text(
            MESSAGES['rename_request'],
            reply_markup=ReplyKeyboardRemove()
        )
        await update.message.reply_text(
            "یا اگر نمی‌خواهید نام عوض شود:",
            reply_markup=get_skip_keyboard()
        )
        return WAITING_RENAME

async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو عملیات"""
    user_id = update.effective_user.id
    session = file_manager.get_session(user_id)
    
    # پاک کردن فایل‌های دانلود شده
    for file_path in session.get('files', []):
        if os.path.exists(file_path):
            os.remove(file_path)
    
    file_manager.clear_session(user_id)
    await update.message.reply_text(
        "❌ عملیات لغو شد و فایل‌ها پاک شدند.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def handle_rename_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت ورودی تغییر نام"""
    user_id = update.effective_user.id
    session = file_manager.get_session(user_id)
    
    rename_pattern = update.message.text.strip()
    session['rename_pattern'] = rename_pattern
    
    await update.message.reply_text(MESSAGES['archive_name_request'])
    return WAITING_ARCHIVE_NAME

async def handle_archive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت نام آرشیو"""
    user_id = update.effective_user.id
    session = file_manager.get_session(user_id)
    
    archive_name = update.message.text.strip()
    session['archive_name'] = archive_name
    
    await update.message.reply_text(
        MESSAGES['password_request'],
        reply_markup=get_skip_keyboard()
    )
    return WAITING_PASSWORD

async def handle_password_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت ورودی رمز"""
    user_id = update.effective_user.id
    session = file_manager.get_session(user_id)
    
    password = update.message.text.strip()
    session['password'] = password
    
    await update.message.reply_text(
        "📦 فرمت فشرده‌سازی را انتخاب کنید:",
        reply_markup=get_archive_format_keyboard()
    )
    return WAITING_ARCHIVE_NAME

async def handle_extract_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت رمز فایل‌های فشرده"""
    user_id = update.effective_user.id
    session = file_manager.get_session(user_id)
    
    password = update.message.text.strip()
    session['password'] = password
    
    await update.message.reply_text(
        "🔄 انتخاب کنید:",
        reply_markup=get_action_keyboard()
    )
    return CHOOSING_ACTION

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت callback query ها"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = file_manager.get_session(user_id)
    
    if query.data == "skip":
        if session.get('current_stage') == 'rename':
            await query.edit_message_text(MESSAGES['archive_name_request'])
            return WAITING_ARCHIVE_NAME
        elif session.get('current_stage') == 'password':
            session['password'] = None
            await query.edit_message_text(
                "📦 فرمت فشرده‌سازی را انتخاب کنید:",
                reply_markup=get_archive_format_keyboard()
            )
            return WAITING_ARCHIVE_NAME
        elif session.get('current_stage') == 'extract_password':
            session['password'] = None
            await query.edit_message_text(
                "🔄 انتخاب کنید:",
                reply_markup=get_action_keyboard()
            )
            return CHOOSING_ACTION
    
    elif query.data.startswith("archive_action_"):
        action = query.data.split("_")[2]
        session['archive_action'] = action
        
        if action == "extract":
            # استخراج فایل فشرده
            await query.edit_message_text(
                MESSAGES['password_request'],
                reply_markup=get_skip_keyboard()
            )
            session['current_stage'] = 'extract_password'
            return WAITING_EXTRACT_PASSWORD
        elif action == "compress":
            # فشرده‌سازی مجدد
            await query.edit_message_text(
                MESSAGES['rename_request'],
                reply_markup=get_skip_keyboard()
            )
            session['current_stage'] = 'rename'
            return WAITING_RENAME
    
    elif query.data.startswith("format_"):
        format_type = query.data.split("_")[1]
        session['archive_format'] = format_type
        await start_compression(query, context, user_id)
        return ConversationHandler.END
    
    elif query.data.startswith("action_"):
        action = query.data.split("_")[1]
        session['action'] = action
        
        if action == "extract":
            await start_extraction(query, context, user_id)
        else:
            await query.edit_message_text("📦 نام جدید آرشیو را وارد کنید:")
            return WAITING_NEW_ARCHIVE_NAME
    
    return ConversationHandler.END

async def start_compression(query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """شروع فشرده‌سازی فایل‌ها"""
    session = file_manager.get_session(user_id)
    
    try:
        await query.edit_message_text(MESSAGES['processing'])
        
        # تغییر نام فایل‌ها اگر نیاز باشد
        files_to_compress = session['files']
        if session.get('rename_pattern'):
            renamed_files = rename_files_with_numbers(
                session['files'], 
                session['rename_pattern']
            )
            files_to_compress = [new_path for _, new_path in renamed_files]
        
        # ایجاد دایرکتوری موقت
        temp_dir = os.path.join(TEMP_DIR, f"compress_{user_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        # کپی فایل‌ها به دایرکتوری موقت
        for file_path in files_to_compress:
            if os.path.exists(file_path):
                shutil.copy2(file_path, temp_dir)
        
        # ایجاد آرشیو
        archive_name = session.get('archive_name', 'archive')
        archive_path = os.path.join(TEMP_DIR, f"{archive_name}.{session['archive_format']}")
        
        await query.edit_message_text(MESSAGES['compressing'])
        
        success = await create_archive(
            temp_dir, 
            archive_path, 
            session['archive_format'],
            session.get('password')
        )
        
        if success:
            # تقسیم فایل در صورت نیاز
            parts = split_large_file(archive_path)
            
            await query.edit_message_text(MESSAGES['uploading'])
            
            # ارسال فایل‌ها
            for i, part_path in enumerate(parts):
                file_size = os.path.getsize(part_path)
                
                # برای همه فایل‌ها از Client API استفاده کن (Bot API محدودیت 50MB دارد)
                success = await send_file_with_client_api(
                    user_id, 
                    part_path, 
                    f"📦 بخش {i+1} از {len(parts)}"
                )
                if not success:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"❌ خطا در ارسال بخش {i+1}"
                    )
            
            await context.bot.send_message(
                chat_id=user_id,
                text=MESSAGES['success']
            )
        else:
                    await context.bot.send_message(
            chat_id=user_id,
            text="❌ خطا در فشرده‌سازی فایل‌ها",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # پاک کردن فایل‌های موقت
        cleanup_temp_files(temp_dir)
        for file_path in session['files']:
            if os.path.exists(file_path):
                os.remove(file_path)
        
    except Exception as e:
        await context.bot.send_message(
            chat_id=user_id,
            text=MESSAGES['error'].format(error=str(e)),
            reply_markup=ReplyKeyboardRemove()
        )
    
    finally:
        file_manager.clear_session(user_id)

async def start_extraction(query, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """شروع استخراج فایل‌ها"""
    session = file_manager.get_session(user_id)
    
    try:
        await query.edit_message_text(MESSAGES['extracting'])
        
        # ترکیب پارت‌ها اگر نیاز باشد
        archive_files = session['files']
        
        # استخراج هر فایل
        extract_dir = os.path.join(EXTRACTED_DIR, f"extract_{user_id}")
        os.makedirs(extract_dir, exist_ok=True)
        
        for archive_path in archive_files:
            success = await extract_archive(
                archive_path, 
                extract_dir, 
                session.get('password')
            )
            
            if not success:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"❌ خطا در استخراج فایل: {os.path.basename(archive_path)}"
                )
                continue
        
        # ارسال فایل‌های استخراج شده
        await query.edit_message_text(MESSAGES['uploading'])
        
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # تقسیم فایل در صورت نیاز
                parts = split_large_file(file_path)
                
                for i, part_path in enumerate(parts):
                    file_size = os.path.getsize(part_path)
                    
                    # برای همه فایل‌ها از Client API استفاده کن (Bot API محدودیت 50MB دارد)
                    success = await send_file_with_client_api(
                        user_id, 
                        part_path, 
                        f"📤 {file}" + (f" - بخش {i+1}" if len(parts) > 1 else "")
                    )
                    if not success:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"❌ خطا در ارسال {file} - بخش {i+1}"
                        )
        
        await context.bot.send_message(
            chat_id=user_id,
            text=MESSAGES['success'],
            reply_markup=ReplyKeyboardRemove()
        )
        
        # پاک کردن فایل‌های موقت
        cleanup_temp_files(extract_dir)
        for file_path in session['files']:
            if os.path.exists(file_path):
                os.remove(file_path)
        
    except Exception as e:
        await context.bot.send_message(
            chat_id=user_id,
            text=MESSAGES['error'].format(error=str(e)),
            reply_markup=ReplyKeyboardRemove()
        )
    
    finally:
        file_manager.clear_session(user_id)

def main():
    """تابع اصلی اجرای ربات"""
    # ایجاد دایرکتوری‌ها
    create_directories()
    
    # ایجاد application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ConversationHandler اصلی
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Document.ALL, handle_document),
            CommandHandler("start", start)
        ],
        states={
            WAITING_FILES: [
                MessageHandler(filters.Document.ALL, handle_document),
                MessageHandler(filters.Regex("^✅ اتمام ارسال فایل‌ها$"), finish_files),
                MessageHandler(filters.Regex("^❌ لغو عملیات$"), cancel_operation),
            ],
            WAITING_RENAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rename_input),
                CallbackQueryHandler(handle_callback_query),
            ],
            WAITING_ARCHIVE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_archive_name),
            ],
            WAITING_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password_input),
                CallbackQueryHandler(handle_callback_query),
            ],
            WAITING_EXTRACT_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_extract_password),
                CallbackQueryHandler(handle_callback_query),
            ],
            CHOOSING_ACTION: [
                CallbackQueryHandler(handle_callback_query),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_operation),
            MessageHandler(filters.Regex("^❌ لغو عملیات$"), cancel_operation),
        ],
    )
    
    # اضافه کردن handler ها
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # شروع ربات
    print("🤖 ربات شروع شد...")
    application.run_polling()

if __name__ == "__main__":
    main()