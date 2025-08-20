# Telegram Packages
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Bot's Core Parts
from core.state_levels import (get_user_state, set_user_state, load_user_state, save_user_state)
from core.access_levels import (load_user_access, save_user_access, get_user_access)
from core.anti_spam import is_spamming_globally
from core.command_functions import IDCheck, github_repo_send, tldr, qdc, ask
from core.setting import BOT_TOKEN, SALATIN

# Interface Parts
from interface.display_manager import set_user_display
from interface.dispatcher import dispatch

# Tech-Stack Parts
from techstack.main import handle_payment_receipt
from techstack.db_interact import (load_registered_users, export_users, import_users)

# Others
import threading
import signal
import time
import os

base_dir = os.path.dirname(__file__)

def graceful_shutdown(signum, frame):
    save_user_states_and_access()
    exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

def save_user_states_and_access():
    save_user_state()
    save_user_access()

async def save_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SALATIN or update.effective_chat.type != "private":
        return
    save_user_states_and_access()
    print("Saved the currnet state/access-level for users in database")
    if update.message:
        await update.message.reply_text("اطلاعات وضعیت کاربرها در دیتابیس ثبت شد")

def load_user_states():
    load_user_state()
    load_user_access()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.effective_chat.type != "private":
        return
    if await is_spamming_globally(update, user_id):
        return

    set_user_state(user_id, "main-menu", update)
    keyboard = [["🎓 طرح کمک‌یار", "🛠️ تک‌استک"],
                ["📞 تماس با ما", "❓ درباره ما"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    if update.message:
        await update.message.reply_text(
            "به ربات انجمن علمی کامپیوتر دانشگاه صنعتی اصفهان خوش‌آمدید!",
            reply_markup=reply_markup
        )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SALATIN or update.effective_chat.type != "private":
        return

    save_user_states_and_access()
    print("Saved the currnet state/access-level for users in database")
    print("Robot will go offline")
    if update.message:
        await update.message.reply_text("اطلاعات وضعیت کاربرها در دیتابیس ثبت شد")
        await update.message.reply_text("ربات خاموش خواهد شد")

    os._exit(0)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.effective_chat.type != "private":
        return

    if not user_id or not update.message:
        return

    if await is_spamming_globally(update, user_id):
        return

    state = get_user_state(user_id)
    found = await dispatch(update, context, state)
    if found:
        return

    text = update.message.text
    username = update.message.from_user.username

    if state == "main-menu":
        if text == "📞 تماس با ما":
            await update.message.reply_text("برای ارتباط با انجمن می‌توانید به روابط عمومی با آیدی @CESSA_Contacts پیام دهید." + "\n" +
                                            "برای گزارش هرگونه مشکل و یا ثبت پیشنهاد نسبت به ربات به آیدی @AmirHoseinGhiasi مراجعه کنید.")
        elif text == "❓ درباره ما":
            await update.message.reply_text("انجمن علمی دانشجویی کامپیوتر صنعتی اصفهان از سال 1384 فعالیت خود را با هدف ایجاد بستری برای رشد علمی، تقویت مهارت‌های تخصصی و گسترش همکاری‌های گروهی میان دانشجویان آغاز کرده است. این انجمن با تکیه بر توانمندی دانشجویان فعال و علاقه‌مند، در طول این سال‌ها تلاش کرده‌ است فضای پویا و خلاقی را برای یادگیری، نوآوری و تجربه‌ورزی فراهم کند." + "\n\n" +
            "📌 کانال رسمی انجمن علمی کامپیوتر:" + "\n" +
            "@iutcessa" + "\n" +
            "📌کانال اطلاع رسانی داخلی:" + "\n" +
            "@cessa_land" + "\n" +
            "📌نشریه فرامتن:" + "\n" +
            "@faramatn" + "\n" +
            "📌عکس‌های انجمن:" + "\n" +
            "@iutcessa_pics")
        elif text == "🎓 طرح کمک‌یار":
            await set_user_display(update, context, state="kmk-yar-main")
        elif text == "🛠️ تک‌استک":
            await set_user_display(update, context, state="tech-stack-main")
        elif text in ["Backdoor", "backdoor", "BackDoor", "BACKDOOR", "back door", "Back door", "Back Door", "BACK DOOR", "بکدور", "بک دور", "در پشتی"]:
            if (user_id in SALATIN):
                await set_user_display(update, context, state="backdoor-panel-head")
            elif(get_user_access(user_id) == "admin"):
                await set_user_display(update, context, state="backdoor-panel")
            elif(get_user_access(user_id) == "user"):
                await set_user_display(update, context, state="backdoor-access-denied")
        elif text == "🔙 بازگشت":
            await set_user_display(update, context, state="main-menu")

    elif text == "🔙 بازگشت":
        await set_user_display(update, context, state="main-menu")

async def enter_uploading_phase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user_id = update.effective_user.id
    if user_id not in SALATIN:
        return

    context.user_data['uploading_stage'] = True

'''
HEARTBEAT_FILE_PATH = (os.path.join(base_dir, "mysite", "heartbeat.txt"))
def update_heartbeat():
    i = 0
    while True:
        i = 1 - i
        if i == 0:
            save_user_states_and_access()
        with open(HEARTBEAT_FILE_PATH, "w") as f:
            f.write(str(int(time.time())))
        time.sleep(300)

heartbeat_thread = threading.Thread(target=update_heartbeat, daemon=True)
heartbeat_thread.start()
'''

def backup_users():
    i = 0
    while True:
        i = 1 - i
        if i == 0:
            save_user_states_and_access()
        time.sleep(300)

heartbeat_thread = threading.Thread(target=backup_users, daemon=True)
heartbeat_thread.start()

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # basic commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("save", save_command))
    app.add_handler(CommandHandler('bot', github_repo_send))
    app.add_handler(CommandHandler("IDCheck", IDCheck))

    # basic response
    app.add_handler(CommandHandler("qdc", qdc))

    # techstack database related commands
    app.add_handler(CommandHandler('db', export_users))
    app.add_handler(CommandHandler('bd', enter_uploading_phase))

    # ai related commands
    app.add_handler(CommandHandler("tldr", tldr))
    app.add_handler(CommandHandler("ask", ask))

    app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_payment_receipt))
    app.add_handler(MessageHandler(filters.Document.ALL & ~filters.COMMAND, import_users))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("The bot is currently running...")
    load_user_states()
    load_registered_users()
    app.run_polling()