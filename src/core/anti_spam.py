from .access_levels import get_user_access
from collections import defaultdict
from .setting import SALATIN
from telegram import Update
import time
user_message_log = defaultdict(list) # for spam checking
user_blocked_until = {}  # Black-listed users

MAX_MESSAGES_PER_MINUTE = 12 
BLOCK_DURATION = 60  # in second

user_spam_count = defaultdict(int)
last_reset_time = time.time()

last_reset_time = time.time()
def reset_spam_logs_if_needed():
    global last_reset_time
    now = time.time()
    if now - last_reset_time > 2 * 86400:  # 86400 seconds = 24 hours
        user_message_log.clear()
        user_blocked_until.clear()
        user_spam_count.clear()
        last_reset_time = now
        print("✅ Spam logs reset.")

async def is_spamming_globally(update: Update, user_id: int) -> bool:
    reset_spam_logs_if_needed()
    now = time.time()

    if user_id in user_blocked_until:
        if now < user_blocked_until[user_id]:
            return True
        else:
            del user_blocked_until[user_id]

    # check for recent messages
    recent_times = [t for t in user_message_log[user_id] if now - t < 60]
    user_message_log[user_id] = recent_times

    role_const = 1
    if get_user_access(user_id) == "admin":
        role_const = 2
    if user_id in SALATIN:
        role_const = 3

    if len(recent_times) >= (MAX_MESSAGES_PER_MINUTE * role_const):
        user_spam_count[user_id] += 1
        penalty_duration = BLOCK_DURATION * (2 ** (user_spam_count[user_id] - 1))
        user_blocked_until[user_id] = now + penalty_duration

        if update.message:
            await update.message.reply_text(f"شما به دلیل ارسال بیش از حد پیام، به مدت {int(penalty_duration//60)} دقیقه مسدود شدید. ⚠️")
        print(f"user {user_id} is spamming. Blocked for {penalty_duration//60} minutes.")
        return True

    user_message_log[user_id].append(now)
    return False