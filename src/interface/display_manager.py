from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Optional

from techstack.user_displays import get_state_keyboard as techstack_user_keyboard, get_state_text as techstack_user_text
from techstack.admin_displays import get_state_keyboard as techstack_admin_keyboard, get_state_text as techstack_admin_text
from kmkyar.displays import get_state_keyboard as kmkyar_keyboard, get_state_text as kmkyar_text
from core.state_levels import *

def get_state_keyboard(state: str):
    if state in TECH_STACK_USER_PANEL:
        return techstack_user_keyboard(state)
    elif state in TECH_STACK_ADMIN_PANEL:
        return techstack_admin_keyboard(state)
    elif state in KMKYAR_MENUS:
        return kmkyar_keyboard(state)
    elif state == "main-menu":
        return [["🎓 طرح کمک‌یار", "🛠️ تک‌استک"],
                ["📞 تماس با ما", "❓ درباره ما"]]
    
    return []

def get_state_text(state: str) -> str:
    if state in TECH_STACK_USER_PANEL:
        return techstack_user_text(state)
    elif state in TECH_STACK_ADMIN_PANEL:
        return techstack_admin_text(state)
    elif state in KMKYAR_MENUS:
        return kmkyar_text(state)
    elif state == "main-menu":
        return "بازگشت به منوی اصلی"
    
    return ""

async def set_user_display(update: Update, context: ContextTypes.DEFAULT_TYPE,
                     state: str, text: Optional[str] = None):
    # extract data
    if update.effective_user is None:
        return
    user_id = update.effective_user.id
    set_user_state(user_id, state, update)

    # set the keyboard along with the right message
    keyboard = get_state_keyboard(state)
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) if keyboard else None
    message = text if text is not None else get_state_text(state)
    if not message:
        message = "ORIGINAL TEXT WAS NULL (MAYBE SOMETHING HAS GONE WRONG)"
    # send the message
    if update.message is None:
        return
    if state == "tech-stack-pay":
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=markup)
        return
    await update.message.reply_text(message, reply_markup=markup)
