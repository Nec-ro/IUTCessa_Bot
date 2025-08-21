from telegram import Update
from telegram.ext import ContextTypes
from interface.display_manager import set_user_display
from .db_interact import load_registered_users, save_registered_users
from .validations import is_valid_positive_integer
from core.access_levels import (save_user_access, user_access_keys,
                                get_user_access, set_user_access)
from .main import (parse_edit_input, filter_input, message_input, start_filter, user_matches,
                            render_user_summary, USERS_PER_MSG)
from core.setting import SALATIN

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
    text = update.message.text
    user_id = update.effective_user.id
    username = update.message.from_user.username

    if state == "backdoor-panel-head":
        if user_id not in SALATIN:
            await set_user_display(update, context, state="main-menu")
            return

        if text == "👥 تنظیمات ادمین‌ها":
            await set_user_display(update, context, state="admin-list")
        elif text == "📩 ویرایش ثبت‌نامی‌ها":
            await set_user_display(update, context, state="registrant-panel")
        elif text == "💸 لیست پرداختی‌ها":
            await set_user_display(update, context, state="pay-panel")
        elif text == "🗨️ لیست مصاحبه‌ای‌ها":
            await set_user_display(update, context, state="interview-panel")
        elif text == "📢 ارسال پیام همگانی":
            start_filter(update, context, "broadcast")
            await set_user_display(update, context, state="filter-panel")
        elif text == "🔎 جستجو در دیتابیس":
            await set_user_display(update, context, state="search-choose")
        elif text == "🔙 بازگشت":
            await set_user_display(update, context, state="main-menu")

    elif state == "backdoor-panel":
        if get_user_access(user_id) != "admin" and user_id not in SALATIN:
            await set_user_display(update, context, state="main-menu")
            return

        if text == "💸 لیست پرداختی‌ها":
            await set_user_display(update, context, state="pay-panel")
        elif text == "📊 آمار تا این لحظه":
            await set_user_display(update, context, state="stats-panel")
        #elif text == "🗨️ لیست مصاحبه‌ای‌ها":
        #    await set_user_display(update, context, state="interview-panel")
        #elif text == "📢 ارسال پیام همگانی":
        #    start_filter(update, context, "broadcast")
        #    await set_user_display(update, context, state="filter-panel")
        #elif text == "🔎 جستجو در دیتابیس":
        #    await set_user_display(update, context, state="search-choose")
        elif text == "🔙 بازگشت":
            await set_user_display(update, context, state="main-menu")

    elif state == "backdoor-access-denied":
        if text == "🔢 دریافت آیدی عددی":
            await update.message.reply_text("آیدی عددی شما:")
            await update.message.reply_text(user_id)
            await set_user_display(update, context, state="main-menu")
        elif text == "🔙 بازگشت":
            await set_user_display(update, context, state="main-menu")

    elif state == "registrant-panel":
        if text == "✍️ ویرایش کردن":
            await set_user_display(update, context, state="registrant-edit")
        elif text == "❌ حذف کردن":
            await set_user_display(update, context, state="registrant-remove")
        elif text == "🔙 بازگشت":
            if user_id in SALATIN:
                await set_user_display(update, context, state="backdoor-panel-head")
            else:
                await set_user_display(update, context, state="backdoor-panel")

    elif state == "registrant-edit":
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="registrant-panel")
        elif is_valid_positive_integer(text):
            target_id = str(int(text))
            registered_users = load_registered_users()
            if target_id not in registered_users:
                await update.message.reply_text("❌ کاربری با این آیدی یافت نشد.")
            else:
                data = registered_users.get(target_id)
                context.user_data["temp-id-slot"] = target_id

                dcourse = data.get("course", "انتخاب نشده")
                if dcourse is None:
                    dcourse = "انتخاب نشده"
                dresult = data["is_passed"]
                if dresult == True:
                    dresult = "قبول شده"
                    dpay = "پرداخت شده" if data.get("has_paid", False) else "پرداخت نشده"
                    if dpay == False:
                        dpay = "پرداخت نشده"
                    elif dpay == True:
                        dpay = "پرداخت شده"
                    await update.message.reply_text(
                                                    f"📄 <b>اطلاعات هدف: (شناسه کاربری \"</b><code>{target_id}</code><b>\")</b> 🆔\n\n"
                                                    f"👤 <b>نام:</b> {data['name']}\n"
                                                    f"👥 <b>نام خانوادگی:</b> {data['surname']}\n"
                                                    f"🔗 <b>آیدی تلگرام:</b> {data['username']}\n"
                                                    f"📞 <b>شماره تلفن:</b> {data['phone']}\n"
                                                    f"🏙️ <b>شهر محل زندگی:</b> {data['city']}\n"
                                                    f"🎓 <b>شماره دانشجویی:</b> {data['student_id']}\n"
                                                    f"📅 <b>سال ورودی:</b> {data['entry_year']}\n"
                                                    #f"🔔 <b>دوره‌های انتخاب شده جهت یادآوری:</b> {data['interests']}\n"
                                                    f"🗣️ <b>نتیجه مصاحبه:</b> {dresult}\n"
                                                    f"📘 <b>دوره اصلی:</b> {dcourse}\n"
                                                    f"💰 <b>وضعیت شهریه:</b> {dpay}\n"
                                                    ,parse_mode='HTML'
                                                )
                else:
                    if dresult == None:
                        dresult = "نامشخص"
                    elif dresult == False:
                        dresult = "رد شده"
                    await update.message.reply_text(
                                                    f"📄 <b>اطلاعات هدف: (شناسه کاربری \"</b><code>{target_id}</code><b>\")</b> 🆔\n\n"
                                                    f"👤 <b>نام:</b> {data['name']}\n"
                                                    f"👥 <b>نام خانوادگی:</b> {data['surname']}\n"
                                                    f"🔗 <b>آیدی تلگرام:</b> {data['username']}\n"
                                                    f"📞 <b>شماره تلفن:</b> {data['phone']}\n"
                                                    f"🏙️ <b>شهر محل زندگی:</b> {data['city']}\n"
                                                    f"🎓 <b>شماره دانشجویی:</b> {data['student_id']}\n"
                                                    f"📅 <b>سال ورودی:</b> {data['entry_year']}\n"
                                                    #f"🔔 <b>دوره‌های انتخاب شده جهت یادآوری:</b> {data['interests']}\n"
                                                    f"🗣️ <b>نتیجه مصاحبه:</b> {dresult}\n"
                                                    #f"📘 <b>دوره اصلی:</b> {dcourse}\n"
                                                    ,parse_mode='HTML'
                                                )
                await set_user_display(update, context, state="registrant-edit-input")
        else:
            await update.message.reply_text("❌ لطفاً یک عدد صحیح مثبت وارد کنید.")

    elif state == "registrant-edit-input":
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="registrant-panel")
        else:
            try:
                updates = parse_edit_input(text)
                registered_users = load_registered_users()
                target_id = context.user_data["temp-id-slot"]
                context.user_data.pop("temp-id-slot", None)

                if target_id not in registered_users:
                    await update.message.reply_text("❌ کاربر موردنظر یافت نشد.")
                else:
                    registered_users[target_id].update(updates)
                    save_registered_users(registered_users)
                    await update.message.reply_text("✅ اطلاعات با موفقیت به‌روزرسانی شد.")
                    await set_user_display(update, context, state="registrant-panel")

            except ValueError as e:
                await update.message.reply_text(f"❌ خطا: {str(e)}")

    elif state == "registrant-remove":
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="registrant-panel")
        elif is_valid_positive_integer(text):
            target_id = str(int(text))
            registered_users = load_registered_users()
            if target_id not in registered_users:
                await update.message.reply_text("❌ کاربری با این آیدی یافت نشد.")
                await set_user_display(update, context, state="registrant-panel")
            else:
                data = registered_users.get(target_id)
                context.user_data["temp-id-slot"] = target_id
                await update.message.reply_text(
                                                f"📄 <b>اطلاعات هدف: (شناسه کاربری \"</b><code>{target_id}</code><b>\")</b> 🆔\n\n"
                                                f"👤 <b>نام:</b> {data['name']}\n"
                                                f"👥 <b>نام خانوادگی:</b> {data['surname']}\n"
                                                f"🔗 <b>آیدی تلگرام:</b> {data['username']}\n"
                                                ,parse_mode='HTML'
                                            )
                await set_user_display(update, context, state="registrant-remove-confirm")
        else:
            await update.message.reply_text("❌ لطفاً یک عدد صحیح مثبت وارد کنید.")

    elif state == "registrant-remove-confirm":
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="registrant-panel")
        elif text == "YES YES YES I AM 100 PERCANT POSETIVE JUST DELETE THIS POOR PERSON":
            if user_id not in SALATIN:
                await update.message.reply_text("شرمنده گلم ولی همچین اجازه‌ای نمیتونم به شما :)")
            else:
                registered_users = load_registered_users()
                target_id = context.user_data["temp-id-slot"]
                context.user_data.pop("temp-id-slot", None)

            if target_id in registered_users:
                del registered_users[target_id]
                save_registered_users(registered_users)
                await update.message.reply_text("✅ اطلاعات کاربر با موفقیت از لیست حذف شد.")
            else:
                await update.message.reply_text("❌ کاربر مورد نظر در لیست وجود نداشت.")

                await set_user_display(update, context, state="interview-panel")

    elif state == "interview-panel":
        if text == "✅ قبول کردن":
            await set_user_display(update, context, state="interviewee-accept")
        elif text == "🕳️ حذف کردن":
            await set_user_display(update, context, state="interviewee-remove")
        elif text == "❌ رد کردن":
            await set_user_display(update, context, state="interviewee-reject")
        elif text == "🔙 بازگشت":
            if user_id in SALATIN:
                await set_user_display(update, context, state="backdoor-panel-head")
            else:
                await set_user_display(update, context, state="backdoor-panel")

    elif state == "interviewee-accept":
        registered_users = load_registered_users()

        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="interview-panel")
        elif is_valid_positive_integer(text):
            target_id = str(int(text))
            if target_id not in registered_users:
                await update.message.reply_text("❌ کاربری با این آیدی یافت نشد.")
            elif registered_users[target_id].get("is_passed") is True:
                await update.message.reply_text("❇️ قبولی این کاربر قبلا ثبت شده است.")
            else:
                registered_users[target_id]["is_passed"] = True
                save_registered_users(registered_users)
                await update.message.reply_text(f"✅ وضعیت قبولی کاربر {target_id} ثبت شد.")
            await set_user_display(update, context, state="interview-panel")
        else:
            await update.message.reply_text("❌ لطفاً یک عدد صحیح مثبت وارد کنید.")

    elif state == "interviewee-remove":
        registered_users = load_registered_users()

        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="interview-panel")
        elif text == "DELETE THE WHOLE DATABASE FOR THOSE POOR SOULS WHO DID OR DID NOT PASS THE INTERVIEW":
            if user_id not in SALATIN:
                await update.message.reply_text("شرمنده گلم ولی همچین اجازه‌ای نمیتونم به شما :)")
            else:
                removed = 0
                for uid, info in registered_users.items():
                    if info.get("is_passed") is not None:
                        info["is_passed"] = None
                        removed += 1
                save_registered_users(registered_users)
                await update.message.reply_text(f"✅ وضعیت مصاحبه {removed} کاربر پاک شد.")
                await set_user_display(update, context, state="interview-panel")
        elif is_valid_positive_integer(text):
            target_id = str(int(text))
            if target_id not in registered_users:
                await update.message.reply_text("❌ کاربری با این آیدی یافت نشد.")
            elif registered_users[target_id].get("is_passed") is None:
                await update.message.reply_text("❌ این کاربر وضعیت مصحابه ندارد.")
            else:
                registered_users[target_id]["is_passed"] = None
                save_registered_users(registered_users)
                await update.message.reply_text(f"✅ وضعیت مصاحبه کاربر {target_id} حذف شد.")
            await set_user_display(update, context, state="interview-panel")
        else:
            await update.message.reply_text("❌ لطفاً یک عدد صحیح مثبت وارد کنید.")

    elif state == "interviewee-reject":
        registered_users = load_registered_users()

        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="interview-panel")
        elif is_valid_positive_integer(text):
            target_id = str(int(text))
            if target_id not in registered_users:
                await update.message.reply_text("❌ کاربری با این آیدی یافت نشد.")
            elif registered_users[target_id].get("is_passed") is False:
                await update.message.reply_text("❇️ ردی این کاربر قبلا ثبت شده است.")
            else:
                registered_users[target_id]["is_passed"] = False
                save_registered_users(registered_users)
                await update.message.reply_text(f"✅ وضعیت ردی کاربر {target_id} ثبت شد.")
            await set_user_display(update, context, state="interview-panel")
        else:
            await update.message.reply_text("❌ لطفاً یک عدد صحیح مثبت وارد کنید.")

    elif state == "pay-panel":
        if text == "👁️ مشاهده لیست":
            await set_user_display(update, context, state="pay-list")
        elif text == "✅ اضافه کردن":
            await set_user_display(update, context, state="payer-add")
        elif text == "❌ حذف کردن":
            await set_user_display(update, context, state="payer-remove")
        elif text == "🔙 بازگشت":
            if user_id in SALATIN:
                await set_user_display(update, context, state="backdoor-panel-head")
            else:
                await set_user_display(update, context, state="backdoor-panel")

    elif state == "pay-list":
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="pay-panel")
            return

        registered_users = load_registered_users()

        paid_text = ""
        not_paid_txt = ""

        paid_count = 0
        not_paid_count = 0

        for uid, info in registered_users.items():
            course = info.get("course", "-")
            if (text != "همه" and course != text) or info.get("is_passed") is not True:
                continue

            full_name = f"{info.get('name', '')} {info.get('surname', '')}"
            username = info.get('username', 'نامشخص')

            base_info = f"• {full_name}\n{username}\n<code>{uid}</code>"
            if text == "همه":
                base_info += f"\n({course})"

            match info.get("has_paid", False):
                case True:
                    paid_text += base_info + "\n\n"
                    paid_count += 1
                case False:
                    not_paid_txt += base_info + "\n\n"
                    not_paid_count += 1

        total_sent = False
        if paid_count > 0:
            await update.message.reply_text(
                f"✅ لیست پرداخت‌کنندگان ({text}) - تعداد: {paid_count} نفر:\n\n{paid_text}",
                parse_mode='HTML'
            )
            total_sent = True

        if not_paid_count > 0:
            await update.message.reply_text(
                f"❌ لیست افرادی که هنوز پرداخت نکرده‌اند ({text}) - تعداد: {not_paid_count} نفر:\n\n{not_paid_txt}",
                parse_mode='HTML'
            )
            total_sent = True

        if not total_sent:
            await update.message.reply_text("❌ هیچ کاربری برای این دسته‌بندی یافت نشد.")

    elif state == "payer-add":
        registered_users = load_registered_users()

        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="pay-panel")
        else:
            lines = text.splitlines()
            stripped_lines = [line.strip() for line in lines if line.strip()]
            for mini_text in stripped_lines:
                if is_valid_positive_integer(mini_text):
                    target_id = str(int(mini_text))
                    if target_id not in registered_users:
                        await update.message.reply_text(f"❌ کاربری با آیدی {target_id} یافت نشد.")
                    elif registered_users[target_id].get("is_passed") is not True:
                        await update.message.reply_text(f"❌ کاربر {target_id} مصاحبه را قبول نشده.")
                    elif registered_users[target_id].get("has_paid") is True:
                        await update.message.reply_text(f"❇️ پرداخت کاربر {target_id} قبلا ثبت شده است.")
                    else:
                        registered_users[target_id]["has_paid"] = True
                        save_registered_users(registered_users)
                        await update.message.reply_text(f"✅ وضعیت پرداخت کاربر {target_id} ثبت شد.")
                else:
                    await update.message.reply_text("❌ لطفاً یک عدد صحیح مثبت وارد کنید.")

    elif state == "payer-remove":
        registered_users = load_registered_users()

        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="pay-panel")
        elif text == "DELETE THE WHOLE DATABASE FOR THOSE POOR SOULS WHO HAVE PAID":
            if user_id not in SALATIN:
                await update.message.reply_text("شرمنده گلم ولی همچین اجازه‌ای نمیتونم به شما :)")
            else:
                removed = 0
                for uid, info in registered_users.items():
                    if info.get("has_paid") is True:
                        info["has_paid"] = False
                        removed += 1
                save_registered_users(registered_users)
                await update.message.reply_text(f"✅ وضعیت پرداخت {removed} کاربر پاک شد.")
        else:
            lines = text.splitlines()
            stripped_lines = [line.strip() for line in lines if line.strip()]
            for mini_text in stripped_lines:
                if is_valid_positive_integer(mini_text):
                    target_id = str(int(mini_text))
                    if target_id not in registered_users:
                        await update.message.reply_text(f"❌ کاربری با آیدی {target_id} یافت نشد.")
                    elif registered_users[target_id].get("has_paid") is not True:
                        await update.message.reply_text(f"❌ کاربر {target_id} وضعیت پرداخت ندارد.")
                    else:
                        registered_users[target_id]["has_paid"] = False
                        save_registered_users(registered_users)
                        await update.message.reply_text(f"✅ پرداخت کاربر {target_id} حذف شد.")
            else:
                await update.message.reply_text("❌ لطفاً یک عدد صحیح مثبت وارد کنید.")

    elif state == "admin-list":
        if text == "✅ اضافه کردن":
            await set_user_display(update, context, state="admin-add")
        elif text == "❌ حذف کردن":
            await set_user_display(update, context, state="admin-remove")
        elif text == "🔙 بازگشت":
            await set_user_display(update, context, state="backdoor-panel-head")

    elif state == "admin-add":
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="admin-list")
        elif is_valid_positive_integer(text):
            target_id = int(text)
            if get_user_access(target_id) == "admin":
                await update.message.reply_text("❇️ این کاربر هم‌اکنون ادمین است.")
            else:
                set_user_access(user_id= target_id, access= "admin", update= update)
                save_user_access()
                await update.message.reply_text(f"✅ کاربر با آیدی {target_id} با موفقیت به ادمین‌ها اضافه شد.")
            await set_user_display(update, context, state="admin-list")
        else:
            await update.message.reply_text("❌ لطفاً یک عدد صحیح مثبت وارد کنید.")

    elif state == "admin-remove":
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="admin-list")
        elif text in ["ALL", "All", "all", "همه"]:
            removed = 0
            for uid in list(user_access_keys()):
                if get_user_access(uid) == "admin":
                    set_user_access(user_id= uid, access= "user", update= update)
                    removed += 1

            save_user_access()
            await update.message.reply_text(f"✅ {removed} ادمین با موفقیت حذف شدند.")
            await set_user_display(update, context, state="admin-list")
        elif is_valid_positive_integer(text):
            target_id = int(text)
            if get_user_access(target_id) != "admin":
                await update.message.reply_text("❌ این کاربر ادمین نیست.")
            else:
                set_user_access(user_id= target_id, access= "user", update= update)
                save_user_access()
                await update.message.reply_text(f"✅ کاربر با آیدی {target_id} از لیست ادمین‌ها حذف شد.")
            await set_user_display(update, context, state="admin-list")
        else:
            await update.message.reply_text("❌ لطفاً یک عدد صحیح مثبت وارد کنید.")

    elif state == "filter-panel":
        if text == "✅ تایید":
            await update.message.reply_text(str(context.user_data.get('filters', [])))
            if (context.user_data['filter-mode'] == "broadcast"):
                await set_user_display(update, context, state="message-panel")
            elif (context.user_data['filter-mode'] == "search"):
                registered_users = load_registered_users()
                filtered = {
                            uid: info for uid, info in registered_users.items()
                            if user_matches(info, context.user_data.get('filters', []), uid)
                            }
                count = len(filtered)
                await update.message.reply_text(f"تعداد کاربران انتخاب‌شده: {count}")
                await set_user_display(update, context, state="search-confirm")
        elif text == "🔙 بازگشت":
            if (context.user_data['filter-mode'] == "broadcast"):
                if user_id in SALATIN:
                    await set_user_display(update, context, state="backdoor-panel-head")
                else:
                    await set_user_display(update, context, state="backdoor-panel")
            elif (context.user_data['filter-mode'] == "search"):
                await set_user_display(update, context, state="search-choose")
        else:
            await filter_input(update, context)

    elif state == "message-panel":
        if text == "🔙 بازگشت":
            if user_id in SALATIN:
                await set_user_display(update, context, state="backdoor-panel-head")
            else:
                await set_user_display(update, context, state="backdoor-panel")
        else:
            if (await message_input(update, context)):
                await set_user_display(update, context, state="broadcast-confirm")

    elif state == "broadcast-confirm":
        if text == "❌ خیر":
            await update.message.reply_text("لغو شد.")
            next_state = "backdoor-panel-head" if user_id in SALATIN else "backdoor-panel"
            await set_user_display(update, context, state=next_state)
            return

        elif text == "✅ بله":
            registered_users = load_registered_users()
            users = {
                uid: info for uid, info in registered_users.items()
                if user_matches(info, context.user_data.get('filters', []), uid)
            }

            btype = context.user_data.get('broadcast_type')
            sent = 0

            for uid, info in users.items():
                try:
                    if btype == 'text':
                        msg = context.user_data['template'].format(**info, id=uid)
                        await context.bot.send_message(chat_id=int(uid), text=msg, parse_mode='HTML')

                    elif btype == 'photo':
                        caption = context.user_data['caption'].format(**info, id=uid)
                        await context.bot.send_photo(
                            chat_id=int(uid),
                            photo=context.user_data['photo_file_id'],
                            caption=caption,
                            parse_mode='HTML'
                        )

                    elif btype == 'forward':
                        await context.bot.forward_message(
                            chat_id=int(uid),
                            from_chat_id=context.user_data['from_chat_id'],
                            message_id=context.user_data['from_message_id']
                        )

                    sent += 1
                except Exception:
                    continue

            await update.message.reply_text(f"✅ ارسال انجام شد به {sent} کاربر.")
            next_state = "backdoor-panel-head" if user_id in SALATIN else "backdoor-panel"
            await set_user_display(update, context, state=next_state)

    elif state == "search-confirm":
        if text == "❌ خیر":
            await update.message.reply_text("لغو شد.")
            await set_user_display(update, context, state="search-choose")
        elif text == "✅ بله":
            registered_users = load_registered_users()
            users = {
                    uid: info for uid, info in registered_users.items()
                    if user_matches(info, context.user_data.get('filters', []), uid)
                    }

            if not users:
                await update.message.reply_text("هیچ کاربری با این مشخصات یافت نشد.")
            else:
                items = list(users.items())

                for i in range(0, len(items), USERS_PER_MSG):
                    chunk = items[i:i + USERS_PER_MSG]
                    result = f"👥 <b>نتایج جست‌وجو ({i+1}-{min(i+USERS_PER_MSG, len(items))}):</b>\n\n"
                    for uid, info in chunk:
                        try:
                            result += render_user_summary(uid, info) + "\n\n"
                        except Exception as e:
                            result += f"❗️خطا در نمایش کاربر {uid}: {e}\n\n"
                    await update.message.reply_text(result.strip(), parse_mode='HTML')

            await set_user_display(update, context, state="search-choose")

    elif state == "search-choose":
        if get_user_access(user_id) != "admin" and user_id not in SALATIN:
            await update.message.reply_text("دسترسی ندارید.")
            return
        if text == "🌐 اعمال فیلتر":
            start_filter(update, context, "search")
            await set_user_display(update, context, state="filter-panel")
        elif text == "📃 اطلاعات کاربر":
            await set_user_display(update, context, state="user-search")
        elif text == "📊 آمار تا این لحظه":
            await set_user_display(update, context, state="stats-panel")
        elif text == "🔙 بازگشت":
            if user_id in SALATIN:
                await set_user_display(update, context, state="backdoor-panel-head")
            else:
                await set_user_display(update, context, state="backdoor-panel")

    elif state == "user-search":
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="search-choose")
        else:
            lines = text.splitlines()
            stripped_lines = [line.strip() for line in lines if line.strip()]
            for mini_text in stripped_lines:
                if is_valid_positive_integer(mini_text):
                    target_id = str(int(mini_text))
                    registered_users = load_registered_users()
                    if target_id not in registered_users:
                        await update.message.reply_text(f"❌ کاربری با آیدی {target_id} یافت نشد.")
                    else:
                        data = registered_users.get(target_id)
                        if "interests" not in data or not isinstance(data["interests"], list):
                            data["interests"] = []
                        if "priorities" not in data or not isinstance(data["priorities"], list):
                            data["priorities"] = []

                        dcourse = data.get("course", "انتخاب نشده")
                        if dcourse is None:
                            dcourse = "انتخاب نشده"
                        dresult = data["is_passed"]
                        if dresult == True:
                            dresult = "قبول شده"
                            dpay = "پرداخت شده" if data.get("has_paid", False) else "پرداخت نشده"
                            await update.message.reply_text(
                                                            f"📄 <b>اطلاعات هدف: (شناسه کاربری \"</b><code>{target_id}</code><b>\")</b> 🆔\n\n"
                                                            f"👤 <b>نام:</b> {data['name']}\n"
                                                            f"👥 <b>نام خانوادگی:</b> {data['surname']}\n"
                                                            f"🔗 <b>آیدی تلگرام:</b> {data['username']}\n"
                                                            f"📞 <b>شماره تلفن:</b> {data['phone']}\n"
                                                            f"🏙️ <b>شهر محل زندگی:</b> {data['city']}\n"
                                                            f"🎓 <b>شماره دانشجویی:</b> {data['student_id']}\n"
                                                            f"📅 <b>سال ورودی:</b> {data['entry_year']}\n"
                                                            f"🔔 <b>دوره‌های انتخاب شده جهت یادآوری:</b> {data['interests']}\n"
                                                            f"📌 <b>اولویت‌های مصاحبه:</b> {data['priorities']}\n"
                                                            f"🗣️ <b>نتیجه مصاحبه:</b> {dresult}\n"
                                                            f"📘 <b>دوره اصلی:</b> {dcourse}\n"
                                                            f"💰 <b>وضعیت شهریه:</b> {dpay}\n"
                                                            ,parse_mode='HTML'
                                                        )
                        else:
                            if dresult == None:
                                dresult = "نامشخص"
                            elif dresult == False:
                                dresult = "رد شده"
                            await update.message.reply_text(
                                                            f"📄 <b>اطلاعات هدف: (شناسه کاربری \"</b><code>{target_id}</code><b>\")</b> 🆔\n\n"
                                                            f"👤 <b>نام:</b> {data['name']}\n"
                                                            f"👥 <b>نام خانوادگی:</b> {data['surname']}\n"
                                                            f"🔗 <b>آیدی تلگرام:</b> {data['username']}\n"
                                                            f"📞 <b>شماره تلفن:</b> {data['phone']}\n"
                                                            f"🏙️ <b>شهر محل زندگی:</b> {data['city']}\n"
                                                            f"🎓 <b>شماره دانشجویی:</b> {data['student_id']}\n"
                                                            f"📅 <b>سال ورودی:</b> {data['entry_year']}\n"
                                                            f"🔔 <b>دوره‌های انتخاب شده جهت یادآوری:</b> {data['interests']}\n"
                                                            f"📌 <b>اولویت‌های مصاحبه:</b> {data['priorities']}\n"
                                                            f"🗣️ <b>نتیجه مصاحبه:</b> {dresult}\n"
                                                            #f"📘 <b>دوره اصلی:</b> {dcourse}\n"
                                                            ,parse_mode='HTML'
                                                        )
                else:
                    await update.message.reply_text(f"❌ لطفاً یک عدد صحیح مثبت وارد کنید: {mini_text}.")

    elif state == "stats-panel":
        if text == "🔙 بازگشت":
            if user_id in SALATIN:
                await set_user_display(update, context, state="search-choose")
            else:
                await set_user_display(update, context, state="backdoor-panel")
        elif text == "🔔 آمار علاقمندی‌ها": 
            await set_user_display(update, context, state="user-stats-interests")
        elif text == "📌 آمار اولویت‌ها":
            await set_user_display(update, context, state="user-stats-priorities")
        elif text == "📘 آمار قبولی‌ها":
            await set_user_display(update, context, state="user-stats-results")

    elif state.startswith("user-stats-"):
        if text == "🔙 بازگشت":
            await set_user_display(update, context, state="stats-panel")
        elif text == "همه":
            registered_users = load_registered_users()
            courses = ["AI", "Back-End", "DevOps", "Blockchain", "Game", "Front-End", "Graphic Design"]
            counts = {course: 0 for course in courses}
            entry_year_counts = {course: {} for course in courses}
            users = 0
            totals = 0
            year_totals = {}

            for info in registered_users.values():
                selected_field = None
                if state.endswith("interests"):
                    selected_field = info.get("interests", [])
                elif state.endswith("priorities"):
                    selected_field = info.get("priorities", [])
                elif state.endswith("results"):
                    selected_field = info.get("course", None)
                    if selected_field is not None:
                        selected_field = [selected_field]
                    else:
                        selected_field = []
                if selected_field:
                    users += 1
                    totals += len(selected_field)
                    year = str(info.get("entry_year", "نامشخص"))
                    year_totals[year] = year_totals.get(year, 0) + 1
                    for course in selected_field:
                        if course in courses:
                            counts[course] += 1
                            entry_year_counts[course][year] = entry_year_counts[course].get(year, 0) + 1

            avg = round(totals / users, 2) if users else 0
            msg = ""
            if state.endswith("interests"):
                msg = (
                    f"👥 تعداد افرادی که حداقل به یک دوره علاقمند بودند: <b>{users}</b>\n"
                    f"📊 میانگین تعداد انتخاب‌های علاقمندی: <b>{avg}</b>\n\n"
                    "🔢 تعداد علاقمندان به هر دوره:\n"
                )
            elif state.endswith("priorities"):
                msg = (
                    f"👥 تعداد افرادی که حداقل یک دوره را به عنوان اولویت انتخاب کردند: <b>{users}</b>\n"
                    f"📊 میانگین تعداد اولویت‌ها: <b>{avg}</b>\n\n"
                    "🔢 تعداد اولویت‌های هر دوره:\n"
                )
            elif state.endswith("results"):
                #percent = round((users / len(registered_users) * 100), 2) if registered_users else 0
                msg = (
                    f"👥 تعداد افرادی که در پروسه مصاحبه قبول شده‌اند: <b>{users}</b>\n\n"
                    #f"📊 درصد قبولی افراد: <b>%{percent}</b>\n\n"
                    "🔢 تعداد افراد قبول شده در هر دوره:\n"
                )
            sorted_courses = sorted(courses, key=lambda c: counts[c], reverse=True)
            for course in sorted_courses:
                msg += f"• <b>{course}</b>: {counts[course]}\n"
            msg += "\n📅 دسته‌بندی بر اساس سال ورودی:\n"
            for year, ycount in sorted(year_totals.items()):
                msg += f"• {year}: {ycount}\n"

            await update.message.reply_text(msg, parse_mode='HTML')
        elif text in ["AI", "Back-End", "DevOps", "Blockchain", "Game", "Front-End", "Graphic Design"]:
            registered_users = load_registered_users()
            count = 0
            as_first_one = 0
            year_counts = {}
            for info in registered_users.values():
                selected_field = None
                if state.endswith("interests"):
                    selected_field = info.get("interests", [])
                elif state.endswith("priorities"):
                    selected_field = info.get("priorities", [])
                elif state.endswith("results"):
                    selected_field = info.get("course", None)
                    if selected_field is not None:
                        selected_field = [selected_field]
                    else:
                        selected_field = []
                if text in selected_field:
                    count += 1
                    year = str(info.get("entry_year", "نامشخص"))
                    year_counts[year] = year_counts.get(year, 0) + 1
                if selected_field and selected_field[0] == text and state.endswith("priorities"):
                    as_first_one += 1

            msg = ""
            if state.endswith("interests"):
                msg = (
                    f"👥 تعداد افراد علاقمند به دوره <b>{text}</b> تک‌استک: <b>{count}</b>\n"
                    "📅 دسته‌بندی بر اساس سال ورودی:\n"
                )
            elif state.endswith("priorities"):
                percent = round((as_first_one / count * 100), 2) if count > 0 else 0
                msg = (
                    f"👥 تعداد افراد با اولویت <b>{text}</b> تک‌استک: <b>{count}</b>\n"
                    f"📊 تعداد افرادی که این دوره را به عنوان اولویت اول انتخاب کردند: <b>{as_first_one} - (%{percent})</b>\n"
                    "📅 دسته‌بندی بر اساس سال ورودی:\n"
                )
            elif state.endswith("results"):
                msg = (
                    f"👥 تعداد افراد قبول‌شده در دوره <b>{text}</b> تک‌استک: <b>{count}</b>\n"
                    "📅 دسته‌بندی بر اساس سال ورودی:\n"
                )
            for year, ycount in sorted(year_counts.items()):
                msg += f"• {year}: {ycount}\n"

            await update.message.reply_text(msg, parse_mode='HTML')