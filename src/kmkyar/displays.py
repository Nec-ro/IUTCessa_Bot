def get_state_keyboard(state: str):
    if state == "kmk-yar-main":
        return [["👥 عضویت در گروه", "📝 ثبت‌نام"],
                ["🔙 بازگشت"]]
    elif state == "kmk-yar-get-link":
        return [["توسعه و هم‌افزایی", "امور علمی و پژوهشی"],
                ["امور فنی", "مستندات"],
                ["🔙 بازگشت"]]

def get_state_text(state: str) -> str:
    if state == "kmk-yar-main":
        return "یکی از گزینه‌های زیر را انتخاب کنید:"
    elif state == "kmk-yar-get-link":
        return "لطفا حوزه‌ی مورد نظر را انتخاب کنید:"