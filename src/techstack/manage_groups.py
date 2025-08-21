from telegram.ext import ContextTypes
from telegram import Update
from .db_interact import load_registered_users, save_registered_users

COURSE_LISTS = ["Back-End", "Front-End", "DevOps", "AI", "Blockchain", "Game", "Graphic Design"]
GROUP_IDS = {
    "Back-End": -1002313120506,
    "Front-End": -1002709555857,
    "DevOps": -1002715297571,
    "AI": -1002550307832,
    "Blockchain": -1002858376146,
    "Game": -1002806435959,
    "Graphic Design": -1002877143590
}

async def create_and_send_invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username
    registered_users = load_registered_users()

    if user_id not in registered_users:
        await update.message.reply_text("شما در دوره تک‌استک ثبت‌نام نکرده‌اید.")
        return

    user_data = registered_users[user_id]
    course = user_data.get('course', '')
    if course not in COURSE_LISTS or user_data.get('is_passed', False) != True:
        await update.message.reply_text("شما در حال حاضر در هیچ دوره‌ای قبول نشده‌اید.")
        return

    if user_data.get('has_paid', False) != True:
        await update.message.reply_text("شما هنوز هزینه دوره را پرداخت نکرده‌اید، و یا وضعیت پرداختتان هنوز تایید نشده است.")
        return

    if user_data.get('got_link', False):
        await update.message.reply_text("شما قبلاً لینک گروه دوره خود را دریافت کرده‌اید.")
        return

    if 'got_link' not in user_data:
        user_data['got_link'] = False

    group_id = GROUP_IDS.get(course)
    if group_id is None:
        await update.message.reply_text("خطا در یافتن گروه مربوطه.")
        return

    try:
        # creating the invite link
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=group_id,
            name= f"@{username}",
            member_limit=1,
            creates_join_request=False,
            expire_date=None
        )

        await update.message.reply_text(f"لینک عضویت شما در گروه دوره {course}:\n{invite_link.invite_link}\nاین لینک تنها برای شما معتبر است.")
        print(f"@{username} got their invite link for the \"{course}\" course.")

        user_data['got_link'] = True
        registered_users[user_id] = user_data
        save_registered_users(registered_users)

    except Exception as e:
        if update.message:
            await update.message.reply_text("خطا در ایجاد لینک عضویت. لطفاً بعداً تلاش کنید.")
        print(f"Error creating invite link: {e}")
