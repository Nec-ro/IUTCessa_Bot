import random
from telegram import Update
from telegram.ext import ContextTypes
from .anti_spam import is_spamming_globally
from .ai import ai_summarize, ai_opinion
from .setting import SALATIN
import time
import re

def clean_backslashes(text: str) -> str:
    return text.replace('\\', '')

def escape_usernames_and_links(text: str) -> str:
    links = re.findall(r'\[.*?\]\(https?://[^\s]+\)', text)

    for i, link in enumerate(links):
        text = text.replace(link, f"__LINK{i}__")

    text = re.sub(
        r'@([A-Za-z0-9]+(?:_(?<!\\)[A-Za-z0-9]+)*)',
        lambda m: '@' + re.sub(r'(?<!\\)_', r'\\_', m.group(1)),
        text
    )
    text = re.sub(
        r'(https?://[^\s]+)',
        lambda m: re.sub(r'(?<!\\)_', r'\\_', m.group(1)),
        text
    )

    for i, link in enumerate(links):
        text = text.replace(f"__LINK{i}__", link)

    return text

async def IDCheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    chat_admins = await context.bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in chat_admins]

    if user_id in SALATIN or user_id in admin_ids:
        if update.message:
            await update.message.reply_text(chat_id)
    
async def github_repo_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_spamming_globally(update, user_id):
        return
    
    repo_link = "https://github.com/Nec-ro/IUTCessa_Bot"
    if update.message:
        await update.message.reply_text(
            f"🚀 <b>لینک مخزن گیت‌هاب ربات:</b>\n\n🔗 <a href='{repo_link}'>{repo_link}</a>",
            parse_mode="HTML",
            disable_web_page_preview=False
        )

async def qdc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    GIF_SOURCE_CHANNEL = -1002635821987
    GIF_MESSAGE_ID = 53

    if update.effective_chat.type == "private":
        return
    if not update.message.reply_to_message:
        try:
            response = await update.message.reply_text("لطفا این دستور را روی یک پیام ریپلای بزنید.")
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.effective_message.id)
            time.sleep(5)
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=response.message_id)
        except:
            pass
        return
    try:
        target = f"@{update.effective_user.username}" if update.effective_user.username else str(update.effective_user.id)    
        await context.bot.copy_message(
            chat_id=update.message.chat_id,                         # where to send
            from_chat_id=GIF_SOURCE_CHANNEL,                        # source chat
            message_id=GIF_MESSAGE_ID,                              # message ID to forward
            disable_notification=True,                              # (optional) send silently
            reply_to_message_id=update.message.reply_to_message.id, # reply to what
            caption= f"Sent by {target}"                            # say what
        )
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.effective_message.id)

    except Exception as e:
        if update.message:
            try:
                response = await update.message.reply_text(f"Failed to forward or delete message: {e}")
                time.sleep(5)
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=response.message_id)
            except:
                pass

# -------------------- AI FUNCTIONS --------------------

ALLOWED_GROUPS = [
    -1001694787846,
    -1002678431127,
    -1002727773269,
    -1002594376990
]

async def tldr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.effective_chat.type == "private":
        return
    if update.effective_chat.id not in ALLOWED_GROUPS:
        return
    if await is_spamming_globally(update, user_id):
        return
    
    if update.message.reply_to_message and update.message.reply_to_message.text:
        original_text = update.message.reply_to_message.text

        if len(original_text) <= 600:
            try:
                response = await update.message.reply_text("متن مشخص شده هم‌اکنون هم طولانی نیست!")
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.effective_message.id)
                time.sleep(5)
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=response.message_id)
            except:
                pass
            return
        
        original_username = update.message.reply_to_message.from_user.username
        bot_username = context.bot.username
        is_this_bot_the_target = (original_username == bot_username) 

        summary = ai_summarize(text=original_text, is_bot_being_summarized=is_this_bot_the_target)
        if update.message:
            await update.message.reply_text(summary)
    else:
        try:
            response = await update.message.reply_text("لطفا این دستور را روی یک پیام ریپلای بزنید.")
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.effective_message.id)
            time.sleep(5)
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=response.message_id)
        except:
            pass

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.effective_chat.type == "private":
        return
    if update.effective_chat.id not in ALLOWED_GROUPS:
        return
    if await is_spamming_globally(update, user_id):
        return
    
    if update.message.reply_to_message and update.message.reply_to_message.text:
        original_text = update.message.reply_to_message.text
        original_username = update.message.reply_to_message.from_user.username
        requester_username = update.effective_user.username
        bot_username = context.bot.username

        full_text = update.message.text or ""
        command_prefix = f"/ask@{bot_username}"

        requester_note = None
        if full_text.startswith(command_prefix):
            requester_note = full_text[len(command_prefix):].strip()

        opinion = ai_opinion(text= original_text, requester_note= requester_note,
                             original_username= original_username, requester_username= requester_username, 
                             bot_username= bot_username)
        #print(f"original:\n{opinion}")
        opinion = clean_backslashes(opinion)
        #print(f"after clean:\n{opinion}")
        try:
            opinionMK = escape_usernames_and_links(opinion)
            #print(f"MK try:\n{opinion}")
            if update.message:
                await update.message.reply_text(text=opinionMK, parse_mode='Markdown')
        except Exception as e:
            #print(f"ERROR!: {e}")
            #print(f"MK failed, now no parse:\n{opinion}")
            if update.message:
                await update.message.reply_text(text=opinion)
    else:
        original_username = update.effective_user.username
        bot_username = context.bot.username

        full_text = update.message.text or ""
        command_prefix = f"/ask@{bot_username}"

        original_text = None
        if full_text.startswith(command_prefix):
            original_text = full_text[len(command_prefix):].strip()

        if original_text in ["", None]:
            try:
                response = await update.message.reply_text("لطفا این دستور را روی یک پیام ریپلای بزنید، و یا درخواست خود را جلوی دستور بنویسید.")
                time.sleep(1)
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.effective_message.id)
                time.sleep(4)
                await context.bot.delete_message(chat_id=update.message.chat_id, message_id=response.message_id)
            except:
                pass
            return

        opinion = ai_opinion(text= original_text, requester_note= None,
                             original_username= original_username, requester_username= original_username, 
                             bot_username= bot_username)
        #print(f"original:\n{opinion}")
        opinion = clean_backslashes(opinion)
        #print(f"after clean:\n{opinion}")
        try:
            opinionMK = escape_usernames_and_links(opinion)
            #print(f"MK try:\n{opinion}")
            if update.message:
                await update.message.reply_text(text=opinionMK, parse_mode='Markdown')
        except Exception as e:
            #print(f"ERROR!: {e}")
            #print(f"MK failed, now no parse:\n{opinion}")
            if update.message:
                await update.message.reply_text(text=opinion)


FACE_EMOJIS = [
    "🤔",
    "😊",
    "😂",
    "😍",
    "😘",
    "😡",
    "😭",
    "😡",
]


async def random_face_emoji(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    if update.effective_chat.type == "private":
        return
    if update.effective_chat.id not in ALLOWED_GROUPS:
        return
    if await is_spamming_globally(update, user_id):
        return

    emoji = random.choice(FACE_EMOJIS)

    if update.message.reply_to_message:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.effective_message.message_id,
            )
        except Exception:
            pass

        sent = await update.message.reply_text(
            emoji,
            reply_to_message_id=update.message.reply_to_message.message_id,
        )
    else:
        await update.message.reply_text(emoji)

