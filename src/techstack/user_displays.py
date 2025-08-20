def get_state_keyboard(state: str):
    if state == "tech-stack-main":
        return [["📌 اولویت‌های من", "📓 مشاهده اطلاعات ثبت‌شده"], # "🔔 به من یادآوری کن", "📝 ثبت‌نام اولیه"
                ["🔗 دریافت لینک گروه دوره", "💫 مشاهده نتایج مصاحبه و پرداخت شهریه"], # "🎥 مشاهده ویدئو‌های معارفه", "📩 ارسال فایل تسک بک‌اند"
                ["🔙 بازگشت"]]
    elif state == "tech-stack-first-forum":
        return [["🔙 بازگشت"]]
    elif state == "tech-stack-user-info-confirm":
        return [["❌ خیر","✅ بله"]]
    elif state == "tech-stack-decision":
        return [["Back-End", "Front-End"],
                ["DevOps", "Graphic Design", "AI"],
                ["Game", "Blockchain"],
                ["🔙 بازگشت", "❌ حذف"]]
    elif state == "tech-stack-pay":
        return [["🔙 بازگشت"]]
    elif state == "tech-stack-vid-task":
        return [["🔙 بازگشت"]]
    elif state == "tech-stack-remind":
        return [["❌ حذف کردن","✅ اضافه کردن"],
                ["🔙 بازگشت"]]
    elif state == "remind-add":
        return [["Back-End", "Front-End"],
                ["DevOps", "Graphic Design", "AI"],
                ["Game", "Blockchain"],
                ["🔙 بازگشت"]]
    elif state == "remind-remove":
        return [["Back-End", "Front-End"],
                ["DevOps", "Graphic Design", "AI"],
                ["Game", "Blockchain"],
                ["🔙 بازگشت"]]
    elif state == "tech-stack-priority":
        return [["❌ حذف لیست", "📝 ویرایش لیست"],
                ["🔙 بازگشت"]]
    elif state == "priority-remove-confirm":
        return [["❌ خیر", "✅ بله"]]
    elif state.startswith("priority-selection-course-"):
        if state.endswith("-1"):
            return [["Back-End", "Front-End"],
                    ["DevOps", "Graphic Design", "AI"],
                    ["Game", "Blockchain"],
                    ["🔙 بازگشت"]]
        else:
            return [["Back-End", "Front-End"],
                    ["DevOps", "Graphic Design", "AI"],
                    ["Game", "Blockchain"],
                    ["🔙 بازگشت", "🛑 پایان"]]
    elif state == "priority-selection-confirm":
        return [["❌ خیر", "✅ بله"]]

def get_state_text(state: str) -> str:
    if state == "tech-stack-main":
        return "یکی از گزینه‌های زیر را انتخاب کنید:"
    elif state == "tech-stack-first-forum":
        return ("لطفا اطلاعات مورد نیاز را به این ترتیب وارد کنید" + "\n" +
                "نام: (فارسی)" + "\n" +
                "نام خانوادگی: (فارسی)" + "\n" +
                "شهر محل زندگی: (فارسی)" + "\n" +
                "شماره تلفن: (اعداد انگلیسی)" + "\n" +
                "شماره دانشجویی: (اعداد انگلیسی)" + "\n" +
                "سال ورودی: (اعداد انگلیسی)" + "\n" + "\n" +
                "مثال: " + "\n" +
                "امیرمحمد" + "\n" +
                "میرزایی" + "\n" +
                "اصفهان" + "\n" +
                "09987515432" + "\n" +
                "40143203" + "\n" +
                "1401" + "\n\n" +
                "نکته: درصورتی که دانشجوی دانشگاه صنعتی اصفهان نیستید، می‌توانید با مراجعه به اکانت پشتیبانی انجمن یک شماره دانشجویی موقت بگیرید." + "\n"
        )
    elif state == "tech-stack-user-info-confirm":
        return "آیا اطلاعات بالا را تایید می‌کنید؟ (توجه کنید که این اطلاعات را نمی‌توانید در آینده تغییر دهید)"
    elif state == "tech-stack-decision":
        return "لطفا حوزه‌ی مورد نظر را انتخاب کنید:"
    elif state == "tech-stack-pay":
        return (
            "لطفاً فیش واریزی خود را در اینجا ارسال کنید (حتماً به صورت عکس)." + "\n\n"
            "💳 شماره کارت جهت واریز:\n\n"
            "`6037 9982 6388 2192`"
            "\nمبلغ 150 هزار تومان مختص دانشجویان صنعتی، و 300 هزار تومان برای دانشجوهای دیگر\n"
            "محمد بزاززاده\n"
        )
    elif state == "tech-stack-vid-task":
        return ("لطفاً فایل تسک بک‌اند خود را ابتدا برروی سایت آپلود، و سپس لینک آن در اینجا ارسال کنید."
                "توجه داشته باشید که ویدئوی شما نمی‌تواند بیشتر از 5 دقیقه باشد، و همچنین تنها لینک‌های مجاز برای ارسال، شامل سه سایت (IUTBox, Google Drive, Uupload) هستند.")
    elif state == "tech-stack-remind":
        return ("در این قسمت می‌توانید دوره‌های مدنظر خود را انتخاب کنید تا هنگام برگزاری جلسه معارفه از طریق ربات مطلع شوید." + "\n" +
                "(⚠️ نیاز به یادآوری است که این قسمت جزو دوره اصلی و ثبت‌نام شما محاسبه نمی‌شود ⚠️)")
    elif state == "remind-add":
        return "لطفا حوزه‌ی مورد نظر را انتخاب کنید:"
    elif state == "remind-remove":
        return "لطفا حوزه‌ی مورد نظر را انتخاب کنید:"
    elif state == "tech-stack-priority":
        #return ("در این پنل شما می‌توانید دوره‌هایی که علاقمند به شرکت در جلسه مصاحبه آن هستید را با رعایت ترتیب مشخص کنید. برای تصمیم‌گیری  تماشای ویدئوهای معارفه هر دوره شدیدا پیشنهاد می‌شود.\n\n"
        #        "موارد مهم: شما تا حداکثر در سه مصاحبه می‌توانید شرکت کنید، و همچنین اگر در بیشتر از یک مصاحبه قبول شدید، بصورت خودکار دوره‌ای که شما اولویت بیشتری برای آن تنظیم کردید انتخاب می‌شود، و امکان تغییر نتیجه در هیچ شرایطی وجود ندارد.\n\n"
        #        "بنابرین در انتخاب خود لطفا دقت کنید.")
        return ("در این قسمت شما می‌توانید اولویت‌هایی که از پیش مشخص کردید را مورد ترتیب‌دهی دوباره قرار دهید، توجه کنید که به نسبت \"لیست اولیه\" شما نمی‌توانید دوره جدیدی اضافه کنید؛ اما امکان حذف وجود دارد.")
    elif state == "priority-remove-confirm":
        return "آیا از حذف لیست اولویت‌ها مطمئن هستید؟"
    elif state.startswith("priority-selection-course-"):
        convert = {
            "1": "اول",
            "2": "دوم",
            "3": "آخر"
        }
        course_number = state.split("-")[-1]
        return f"لطفاً اولویت {convert[course_number]} خود را انتخاب کنید:"
    elif state == "priority-selection-confirm":
        return "آیا اولویت‌های انتخابی خود را تایید می‌کنید؟"
    