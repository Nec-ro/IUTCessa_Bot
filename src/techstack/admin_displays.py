from core.access_levels import load_user_access

def get_state_keyboard(state: str):
    if state == "backdoor-panel-head":
        return [["👥 تنظیمات ادمین‌ها"],
                ["📩 ویرایش ثبت‌نامی‌ها", "💸 لیست پرداختی‌ها", "🗨️ لیست مصاحبه‌ای‌ها"],
                ["📢 ارسال پیام همگانی", "🔎 جستجو در دیتابیس"],
                ["🔙 بازگشت"]]
    elif state == "backdoor-panel":
        return [["💸 لیست پرداختی‌ها", "📊 آمار تا این لحظه"],
                ["🔙 بازگشت"]]
    elif state == "backdoor-access-denied":
        return [["🔢 دریافت آیدی عددی"],
                ["🔙 بازگشت"]]
    elif state == "admin-list":
        return [["❌ حذف کردن","✅ اضافه کردن"],
                ["🔙 بازگشت"]]
    elif state == "admin-add":
        return [["🔙 بازگشت"]]
    elif state == "admin-remove":
        return [["🔙 بازگشت"]]
    elif state == "registrant-panel":
        return [["❌ حذف کردن","✍️ ویرایش کردن"],
                ["🔙 بازگشت"]]
    elif state == "registrant-edit":
        return [["🔙 بازگشت"]]
    elif state == "registrant-edit-input":
        return [["🔙 بازگشت"]]
    elif state == "registrant-remove":
        return [["🔙 بازگشت"]]
    elif state == "registrant-remove-confirm":
        return [["🔙 بازگشت"]]
    elif state == "interview-panel":
        return [["🕳️ حذف کردن"],
                ["❌ رد کردن", "✅ قبول کردن"],
                ["🔙 بازگشت"]]
    elif state == "interviewee-accept":
        return [["🔙 بازگشت"]]
    elif state == "interviewee-remove":
        return [["🔙 بازگشت"]]
    elif state == "interviewee-reject":
        return [["🔙 بازگشت"]]
    elif state == "pay-panel":
        return [["👁️ مشاهده لیست"],
                ["❌ حذف کردن","✅ اضافه کردن"],
                ["🔙 بازگشت"]]
    elif state == "pay-list":
        return [["Back-End", "Front-End"],
                    ["DevOps", "Graphic Design", "AI"],
                    ["Game", "Blockchain"],
                    ["🔙 بازگشت", "همه"]]
    elif state == "payer-add":
        return [["🔙 بازگشت"]]
    elif state == "payer-remove":
        return [["🔙 بازگشت"]]
    elif state == "filter-panel":
        return [["✅ تایید"],
                ["🔙 بازگشت"]]
    elif state == "message-panel":
        return [["🔙 بازگشت"]]
    elif state == "broadcast-confirm":
        return [["❌ خیر","✅ بله"]]
    elif state == "search-choose":
        return [["📃 اطلاعات کاربر","🌐 اعمال فیلتر"],
                ["🔙 بازگشت", "📊 آمار تا این لحظه"]]
    elif state == "search-confirm":
        return [["❌ خیر","✅ بله"]]
    elif state == "user-search":
        return [["🔙 بازگشت"]]
    elif state == "stats-panel":
        return [["📌 آمار اولویت‌ها","🔔 آمار علاقمندی‌ها"],
                ["🔙 بازگشت", "📘 آمار قبولی‌ها"]]
    elif state.startswith("user-stats-"):
        return [["Back-End", "Front-End"],
                    ["DevOps", "Graphic Design", "AI"],
                    ["Game", "Blockchain"],
                    ["🔙 بازگشت", "همه"]]
    
def get_state_text(state: str) -> str:
    if state == "backdoor-panel-head":
        return "پنل سلطان:"
    elif state == "backdoor-panel":
        return "پنل ادمین:"
    elif state == "backdoor-access-denied":
        return "شما اجازه ورود نداری! برای گرفتن این دسترسی باید به رئیس پیام بدی! (آیدی عددی هم باید براش بفرستی)"
    elif state == "admin-list":
        data = load_user_access()
        if data is None:
            return "خطا در بارگذاری اطلاعات دسترسی!"
        admins = [user for user, access in data.items() if access == "admin"]
        if not admins:
            return "لیست ادمین‌ها خالیست!"
        txt = "لیست ادمین‌ها:\n\n"
        for i, user in enumerate(admins, 1):
            txt += f"{i}. {user}\n"
        return txt
    elif state == "admin-add":
        return "لطفا آیدی عددی کاربر را برای اضافه کردن وارد کنید."
    elif state == "admin-remove":
        return ("لطفا آیدی عددی کاربر را برای حذف کردن وارد کنید." + "\n" +
                "برای حذف همه میتوانید از عبارت \"ALL\" و یا \"همه\" استفاده کنید.")
    elif state == "registrant-panel":
        return "لطفا گزینه‌ی مدنظر را انتخاب کنید:"
    elif state == "registrant-edit":
        return "لطفا آیدی عددی کاربر را برای ویرایش کردن وارد کنید."
    elif state == "registrant-edit-input":
        return (
        "لطفاً اطلاعاتی که می‌خواهید ویرایش کنید را وارد نمایید. فقط فیلدهای زیر قابل ویرایش هستند:"
        "\nEDITABLE_FIELDS = {'name', 'surname', 'city', 'phone', 'student_id', 'entry_year', 'course', 'got_link'}\n"
        "\nVALID_COURSES = {'Back-End', 'Front-End', 'DevOps', 'Graphic Design', 'AI', 'Game', 'Blockchain'}\n"
        "\nهر فیلد را در یک خط وارد کنید، بعنوان مثال:\n"
        "name > علی\n"
        "city > تهران\n"
        "phone > 09123456789"
        )
    elif state == "registrant-remove":
        return "لطفا آیدی عددی کاربر را برای حذف کردن وارد کنید."
    elif state == "registrant-remove-confirm":
        return "آیا از انجام این عملیات مطمئن هستید؟ درصورت اطمینان از حذف این کاربر عبارت \"YES YES YES I AM 100 PERCANT POSETIVE JUST DELETE THIS POOR PERSON\" را وارد کنید. "
    elif state == "interview-panel":
        return "لطفا گزینه‌ی مدنظر را انتخاب کنید:"
    elif state == "interviewee-accept":
        return "لطفا آیدی عددی کاربر را برای قبول کردن وارد کنید."
    elif state == "interviewee-remove":
        return ("لطفا آیدی عددی کاربر را برای حذف کردن وارد کنید." + "\n" +
                "برای حذف همه میتوانید از عبارت \"DELETE THE WHOLE DATABASE FOR THOSE POOR SOULS WHO DID OR DID NOT PASS THE INTERVIEW\" استفاده کنید.")
    elif state == "interviewee-reject":
        return "لطفا آیدی عددی کاربر را برای رد کردن وارد کنید."
    elif state == "pay-panel":
        return "لطفا گزینه‌ی مدنظر را انتخاب کنید:"
    elif state == "pay-list":
        return "لطفا حوزه‌ی مورد نظر را انتخاب کنید:"
    elif state == "payer-add":
        return "لطفا آیدی عددی کاربر را برای اضافه کردن وارد کنید."
    elif state == "payer-remove":
        return ("لطفا آیدی عددی کاربر را برای حذف کردن وارد کنید." + "\n" +
                "برای حذف همه میتوانید از عبارت \"DELETE THE WHOLE DATABASE FOR THOSE POOR SOULS WHO HAVE PAID\" استفاده کنید.")
    elif state == "filter-panel":
        return (
        "لطفاً شرایط انتخاب کاربران را در هر خط بصورت: field op value وارد کنید."
        "\nمثال:\ncity == اصفهان\nentry_year >= 1401\n"
        "\nALLOWED_FIELDS = {'id','username', 'name', 'surname', 'city', 'phone', 'student_id', 'entry_year', 'course', 'is_passed', 'has_paid', 'interests', 'priorities', 'got_link'}\n"
        "\npossible_ops = ['not contains', 'contains', 'is not', 'not in', '>=', '<=', '==', '!=', '>', '<', 'in', 'is']\n\n"
        "برای پایان، گزینه تایید را کنید.")
    elif state == "message-panel":
        return (
            "فیلترها ثبت شدند. حالا متن پیام را با فرمت HTML کنید ({name}, {course}, ... برای جای‌گذاری):")
    elif state == "broadcast-confirm":
        return "آیا برای ارسال پیام آماده‌اید؟"
    elif state == "search-confirm":
        return "آیا برای نمایش جستجو آماده‌اید؟"
    elif state == "search-choose":
        return ("لطفا گزینه مورد نظر خود را انتخاب کنید." + "\n" +
                "🌐 اعمال فیلتر: اطلاعات جزئی تمامی کاربرانی که شرط ورودی برای آنها صدق می‌کند را نمایش می‌دهد." + "\n" +
                "📃 اطلاعات کاربر: اطلاعات کامل شخص را نمایش می‌دهد. (با کلید ورودی آیدی عددی)" + "\n" +
                "📊 آمار تا این لحظه: آمار کلی از تعداد کاربران برای هر پارامتر علاقمندی، اولویت‌بندی، و قبولی را نمایش می‌دهد."
                )
    elif state == "user-search":
        return "لطفا آیدی عددی کاربر را برای جستجو وارد کنید."
    elif state == "stats-panel":
        return "لطفا گزینه‌ی مدنظر را انتخاب کنید:"
    elif state.startswith("user-stats-"):
        return "لطفا حوزه‌ی مورد نظر را انتخاب کنید:"
