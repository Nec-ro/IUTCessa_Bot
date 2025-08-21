from telegram import Update
from telegram.ext import ContextTypes
from .validations import (is_valid_persian, is_valid_phone_number, 
                          is_valid_student_id, is_valid_entry_year,
                          extract_forward_info)
from .db_interact import load_registered_users, load_backup_course
from core.setting import PAYCHECK_GROUP_ID
from core.anti_spam import is_spamming_globally
from core.state_levels import get_user_state

OPS = {
    '==': lambda a, b: a == b,
    '!=': lambda a, b: a != b,
    '>':  lambda a, b: a > b,
    '<':  lambda a, b: a < b,
    '>=': lambda a, b: a >= b,
    '<=': lambda a, b: a <= b,
    'in': lambda a, b: a in b,
    'not in': lambda a, b: a not in b,
    'contains': lambda a, b: b in a,
    'not contains': lambda a, b: b not in a
}
ALLOWED_FIELDS = {'id', 'username', 'name', 'surname', 'city', 'phone', 'student_id', 'entry_year', 'course', 'is_passed', 'has_paid', 'interests', 'priorities', 'got_link'}
USERS_PER_MSG = 40

registered_users = {} # tech stack users info

MAX_RECEIPT_UPLOADS = 2

def parse_filter_line(line: str):
    line = line.strip()
    if not line:
        raise ValueError("خط خالی")

    parts = line.split()
    if len(parts) < 3:
        raise ValueError("فرمت باید: field op value باشه")

    field = parts[0].lower()

    if field not in ALLOWED_FIELDS:
        raise ValueError(f"فیلد '{field}' مجاز نیست.")

    possible_ops = ['not contains', 'contains', 'is not', 'not in', '>=', '<=', '==', '!=', '>', '<', 'in', 'is']

    for op in possible_ops:
        op_words = op.split()
        if parts[1:1+len(op_words)] == op_words:
            value = ' '.join(parts[1+len(op_words):])
            if not value:
                raise ValueError("مقدار (value) وجود ندارد.")

            raw = value.strip().replace('،', ',')
            raw_lower = raw.lower()

            if op == 'is':
                op = '=='
            elif op == 'is not':
                op = '!='

            if op in ('in', 'not in'): 
                value_parsed = [v.strip() for v in raw.split(',')]
                value_parsed = [None if v.lower() in ('null', 'none') else v for v in value_parsed]
            elif op in ('contains', 'not contains'):
                value_parsed = raw
            elif raw_lower in ('null', 'none'):
                value_parsed = None
            elif raw_lower == 'true':
                value_parsed = True
            elif raw_lower == 'false':
                value_parsed = False
            elif raw_lower == 'empty':
                value_parsed = '[]'
            elif raw.isdigit():
                value_parsed = int(raw)
            else:
                value_parsed = raw.strip('"')

            return field, op, value_parsed

    raise ValueError("اپراتور معتبر نیست یا فرمت نادرست است.")

def user_matches(info, filters, uid):
    if uid is not None:
        info = {**info, 'id': int(uid)}

    for field, op, val in filters:
        actual = info.get(field)
  
        if actual is None and op not in ('==', '!=', 'is', 'is not', 'in', 'not in'):
            return False

        if actual is None:
            actual_cast = None
        elif isinstance(val, bool):
            if isinstance(actual, bool):
                actual_cast = actual
            elif str(actual).lower() in ('true', 'false'):
                actual_cast = str(actual).lower() == 'true'
            else:
                actual_cast = None
        elif isinstance(val, int):
            try:
                actual_cast = int(actual)
            except:
                return False
        else:
            actual_cast = str(actual)

        if not OPS[op](actual_cast, val):
            return False

    return True

def parse_edit_input(text):
    EDITABLE_FIELDS = {'username', 'name', 'surname', 'city', 'phone', 'student_id', 'entry_year', 'course', 'got_link'}
    VALID_COURSES = {"Back-End", "Front-End", "DevOps", "Graphic Design", "AI", "Game", "Blockchain"}

    updates = {}
    lines = text.strip().split('\n')

    for line in lines:
        if '>' not in line:
            raise ValueError(f"فرمت نادرست: {line}")

        key, value = map(str.strip, line.split('>', 1))

        if key not in EDITABLE_FIELDS:
            raise ValueError(f"فیلد نامعتبر یا غیرقابل ویرایش: {key}")

        v_lower = value.lower()

        if key == 'course':
            if v_lower in ('null', 'none'):
                updates[key] = None
            elif value not in VALID_COURSES:
                raise ValueError(f"مقدار '{value}' برای فیلد course مجاز نیست.")
            else:
                updates[key] = value
            continue

        if v_lower in ('null', 'none'):
            raise ValueError(f"مقدار فیلد '{key}' نمی‌تواند null باشد.")

        if key in ('name', 'surname', 'city'):
            if not is_valid_persian(value):
                raise ValueError(f"مقدار واردشده برای '{key}' معتبر نیست (باید فارسی و حداقل ۲ حرف باشد).")
        elif key == 'phone':
            if not is_valid_phone_number(value):
                raise ValueError(f"شماره تلفن '{value}' نامعتبر است.")
        elif key == 'student_id':
            if not is_valid_student_id(value):
                raise ValueError(f"شماره دانشجویی '{value}' نامعتبر است.")
        elif key == 'entry_year':
            if not is_valid_entry_year(value):
                raise ValueError(f"سال ورودی '{value}' مجاز نیست.")

        updates[key] = value

    return updates

def render_user_summary(uid, user):
    interview_raw = user.get('is_passed', '')

    if interview_raw == True:
        interview = "Interview: Accepted ✅"
    elif interview_raw == False:
        interview = "Interview: Rejected ❌"
    else:
        interview = "Interview: Unknown ⚠️"

    return (
        f"🆔 <code>{uid}</code> | 👤 {user.get('name', '---')} {user.get('surname', '---')} | 🔗 {user.get('username', '---') or '---'}\n"
        f"📘 {user.get('course', '---')} | 📅 {user.get('entry_year', '---')} | 🗣️ {interview}"
    )

def start_filter(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
    context.user_data['filters'] = []
    context.user_data['filter-mode'] = mode

async def filter_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    lines = text.splitlines()
    stripped_lines = [line.strip() for line in lines if line.strip()]
    for mini_texts in stripped_lines:
        try:
            flt = parse_filter_line(mini_texts)
            context.user_data.setdefault('filters', []).append(flt)
            await update.message.reply_text(f"✅ شرط ثبت شد: {flt[0]} {flt[1]} {flt[2]}")
        except Exception as e:
            await update.message.reply_text(f"خطا: {e}")

async def message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if msg.text:
        text = msg.text.strip()
        channel, msg_id = extract_forward_info(text)
        if channel and msg_id:
            context.user_data['broadcast_type'] = 'forward'
            context.user_data['from_chat_id'] = f"@{channel}"
            context.user_data['from_message_id'] = msg_id
        else:
            context.user_data['broadcast_type'] = 'text'
            context.user_data['template'] = text

    else:
        await msg.reply_text("❌ نوع پیام پشتیبانی نمی‌شود. فقط متن یا لینک از کانال مجاز است.")
        return False

    registered_users = load_registered_users()
    filtered = {
        uid: info for uid, info in registered_users.items()
        if user_matches(info, context.user_data.get('filters', []), uid)
    }
    await msg.reply_text(f"✅ پیام ذخیره شد. تعداد کاربران انتخاب‌شده: {len(filtered)}")
    return True

async def handle_payment_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    if update.effective_chat.type != "private":
        return

    if (await is_spamming_globally(update, user.id)) or get_user_state(user.id) != "tech-stack-pay":
        return

    count = context.user_data.get("payment_receipt_count", 0)
    if count >= MAX_RECEIPT_UPLOADS:
        await update.message.reply_text("❌ شما قبلاً فیش خود را ارسال کرده‌اید. امکان ارسال مجدد وجود ندارد.")
        return

    # only photos are accepted
    if not update.message.photo:
        await update.message.reply_text("❌ لطفاً فقط عکس فیش واریزی را ارسال کنید.")
        return

    context.user_data["payment_receipt_count"] = count + 1

    # forwarding to the group
    await context.bot.forward_message(
        chat_id=PAYCHECK_GROUP_ID,
        from_chat_id=chat_id,
        message_id=update.message.message_id
    )

    registered_users = load_registered_users()
    data = registered_users.get(str(user.id))

    dcourse = data["course"]
    if dcourse == None:
        dcourse = "انتخاب نشده"

    # sending the needed info along
    text = (
        "🧾 فیش واریزی جدید دریافت شد\n\n" +
        f"🔖 آیدی عددی: <code>{user.id}</code>\n"
        "نام: " + data["name"] + "\n" +
        "نام خانوادگی: " + data["surname"] + "\n" +
        "آیدی تلگرام: " + data["username"] + "\n" +
        "شماره تلفن: " + data["phone"] + "\n" +
        "شهر محل زندگی: " + data["city"] + "\n" +
        "شماره دانشجویی: " + data["student_id"] + "\n" +
        "سال ورودی: " + data["entry_year"] + "\n" +
        "دوره انتخاب شده: " + dcourse + "\n"
    )

    await context.bot.send_message(
        chat_id=PAYCHECK_GROUP_ID,
        text=text,
        parse_mode='HTML'
    )

    # response
    await update.message.reply_text("✅ فیش شما با موفقیت ثبت شد. منتظر بررسی باشید.")

async def show_user_priorities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    registered_users = load_registered_users()
    user_id = str(update.effective_user.id)

    if user_id in registered_users:
       user_info = registered_users[user_id]

    if "priorities" not in user_info or not isinstance(user_info["priorities"], list):
        user_info["priorities"] = []

    if not user_info["priorities"]:
        await update.message.reply_text("⁉️ شما هنوز هیچ اولویتی برای خود تنظیم نکردید")
    else:
        reply_text = "📌 <b>در حال حاضر اولویت‌های شما بصورت زیر است</b>\n\n"
        emoji_map = {
        1: "🥇 ",
        2: "🥈 ",
        3: "🥉 "
        }
        for i, priority in enumerate(user_info["priorities"], start=1):
            reply_text += f"{emoji_map.get(i, '')}{priority}\n"
        await update.message.reply_text(reply_text, parse_mode='HTML')

async def show_user_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    registered_users = load_registered_users()
    user_id = str(update.effective_user.id)

    if user_id in registered_users:
        user_info = registered_users[user_id]

    if "interests" not in user_info or not isinstance(user_info["interests"], list):
        user_info["interests"] = []

    if not user_info["interests"]:
        await update.message.reply_text("⁉️ شما هنوز هیچ دوره‌ای را برای یادآوری انتخاب نکردید")
    else:
        reply_text = "🔔 <b>دوره‌های انتخاب شده جهت یادآوری:</b>\n\n"
        for interest in user_info["interests"]:
            reply_text += f"• {interest}\n"
        await update.message.reply_text(reply_text, parse_mode='HTML')