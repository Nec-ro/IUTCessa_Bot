from telegram.ext import ContextTypes
from telegram import Update
import json
import os

GROUP_IDS = {
    "توسعه و هم‌افزایی": -1002505422485,
    "امور علمی و پژوهشی": -1002672324730,
    "امور فنی": -1002633895189,
    "مستندات": -1002261561218,
    "اراک": -1002594376990
}
base_dir = os.path.dirname(__file__)

# reading the data file
KMKYAR_FILE_DIRECTORY = (os.path.join(base_dir, "kmkyardata.json"))

def load_kmkyar_data():
    try:
        with open(KMKYAR_FILE_DIRECTORY, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_kmkyar_data(data):
    with open(KMKYAR_FILE_DIRECTORY, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def create_and_send_invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE, role: str):
    if update.message is None:
        return
    username = update.message.from_user.username
    if not username:
        return
    full_username = f"@{username}"

    if role == "اراک":
        await update.message.reply_text("شما یک Easter Egg یافتید!" + "\n" +
                                        "جایزه شما: لینک گروه اراک" + "\n" +
                                        "https://t.me/+gSJ3LihB_j5kMTM0")
        print(full_username + " got their invite link for the \"" + "ARAK" + "\" section.")
        return

    group_id = GROUP_IDS.get(role)
    if group_id is None:
        await update.message.reply_text("خطا در یافتن گروه مربوطه.")
        return

    try:
        # creating the invite link
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=group_id,
            name=full_username,
            member_limit=1,
            creates_join_request=False,
            expire_date=None
        )

        await update.message.reply_text(f"لینک عضویت شما در گروه {role}:\n{invite_link.invite_link}\nاین لینک تنها برای شما معتبر است.")
        role_map = {
            "توسعه و هم‌افزایی": "exp",
            "امور علمی و پژوهشی": "sci",
            "امور فنی": "tec",
            "مستندات": "doc"
            #,"اراک": "ARAK"
        }
        print("@" + username + " got their invite link for the \"" + role_map[role] + "\" section.")

        # changing the value in the excel file
        #if role != "اراک":
        user_data = load_kmkyar_data()
        
        if full_username in user_data:
            user_data[full_username][role] = 1
            save_kmkyar_data(user_data)
        else:
            pass

    except Exception as e:
        await update.message.reply_text("خطا در ایجاد لینک عضویت. لطفاً بعداً تلاش کنید.")
        print(f"Error creating invite link: {e}")

def check_user_role(username, role):
    if not username:
        return

    user_data = load_kmkyar_data()
    search_username = f"@{username}".lower() if not username.startswith("@") else username.lower()

    for key in user_data:
        if key.lower() == search_username:
            user_info = user_data[key]
            value = user_info.get(role)
            if value == 2:
                return "allowed"
            elif value == 1:
                return "already_sent"
            elif value == 0:
                return "not_registered"
            else:
                return "unknown"
    return "not_found"