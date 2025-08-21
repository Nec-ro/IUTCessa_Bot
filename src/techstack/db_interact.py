from telegram import Update, InputFile
from telegram.ext import ContextTypes
import json
import os
from core.setting import SALATIN

base_dir = os.path.dirname(__file__)
REGISTERED_USERS_FILE = (os.path.join(base_dir, "registered_users.json")) #tech-stack data
TASKLINKS_FILE = (os.path.join(base_dir, "tasklinks.json")) #task links data
BACKUP_COURSE_FILE = (os.path.join(base_dir, "backup_course.json")) #backup course data

def load_registered_users():
    try:
        with open(REGISTERED_USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_registered_users(data):
    with open(REGISTERED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_tasklinks():
    try:
        with open(TASKLINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    
def save_tasklinks(data):
    with open(TASKLINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_backup_course():
    try:
        with open(BACKUP_COURSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    
def save_backup_course(data):
    with open(BACKUP_COURSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def export_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user_id = update.effective_user.id
    if user_id not in SALATIN:
        return

    try:
        with open(REGISTERED_USERS_FILE, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=InputFile(f, filename="registered_users.json"),
                caption="📄 فایل کاربران"
            )
        print("database exported by " + str(user_id))
    except Exception as e:
        await update.message.reply_text(f"خطا در ارسال فایل: {e}")

async def import_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    on_upload_state = context.user_data.get('uploading_stage', False)
    user_id = update.effective_user.id
    if user_id not in SALATIN or not on_upload_state:
        return

    document = update.message.document if update.message else None
    if not document:
        if update.message:
            await update.message.reply_text("لطفاً یک فایل ارسال کنید.")
        return

    filename = document.file_name
    if filename != "registered_users.json":
        if update.message:
            await update.message.reply_text("❌ فقط فایل 'registered_users.json' مجاز است.")
        return

    try:
        with open(REGISTERED_USERS_FILE, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=InputFile(f, filename="registered_users.json"),
                caption="📄 فایل قبلی جهت بک‌آپ"
            )
        print("database exported by " + str(user_id) + " as backup")

        telegram_file = await document.get_file()
        await telegram_file.download_to_drive(custom_path=REGISTERED_USERS_FILE)

        if update.message:
            await update.message.reply_text("✅ فایل با موفقیت ذخیره و جایگزین شد.")
        print("database imported by " + str(user_id))
    except Exception as e:
        await update.message.reply_text(f"خطا در پردازش: {e}")
