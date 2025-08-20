from telegram import Update
from telegram.ext import ContextTypes
from interface.display_manager import set_user_display 
from .main import check_user_role, create_and_send_invite_link

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
    if not update.message:
        return
    
    text = update.message.text
    username = update.message.from_user.username if update.message.from_user else None

    if state == "kmk-yar-main":
        if text == "👥 عضویت در گروه":
            await set_user_display(update, context, state="kmk-yar-get-link")
        elif text == "📝 ثبت‌نام":
            await update.message.reply_text("باتشکر از استقبال بی‌نظیر شما دوستان، لینک ثبت‌نام تا اطلاع ثانوی غیرفعال خواهد شد.")
            #await context.bot.forward_message(chat_id=update.message.chat_id,
            #                                  from_chat_id="@cessa_land",
            #                                  message_id=323)
            #await update.message.reply_text("با پرکردن فرم بالا می‌توانید عضوی از خانواده بزرگ انجمن شوید :)")
            #username = update.message.from_user.username
            #if username:
            #    print("@" + username + " wants to become a member of Cessa Community!")
        elif text == "🔙 بازگشت":
            await set_user_display(update, context, state="main-menu")

    elif state == "kmk-yar-get-link":
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="kmk-yar-main")
        else:
            if not update.message.from_user:
                await update.message.reply_text("خطا در دریافت اطلاعات کاربری.")
                return
            username = update.message.from_user.username
            if not username:
                await update.message.reply_text("ابتدا در تنظیمات تلگرام، یک نام کاربری (username) برای خود ثبت کنید.")
                return

            role = text
            if role != "اراک":
                result = check_user_role("@" + username, role)
                if result == "allowed":
                    await create_and_send_invite_link(update, context, role)
                elif result == "already_sent":
                    await update.message.reply_text("شما قبلا لینک عضویت در این حوزه را دریافت کرده‌اید.")
                elif result == "not_registered":
                    await update.message.reply_text("شما برای این حوزه ثبت‌نام نکرده‌اید.")
                else:
                    await update.message.reply_text("نام کاربری شما در سامانه ثبت نشده است.")
            else:
                await create_and_send_invite_link(update, context, role)