import re

pattern = re.compile(r'''^\s*(?P<field>\w+)\s*(?P<op>not contains|not in|is not|==|!=|>=|<=|>|<|contains|in|is)\s*(?P<value>.+?)\s*$''', re.VERBOSE)

def is_valid_persian(text: str) -> bool:
    return bool(re.fullmatch(r'[آ-ی‌ٔء\s]{2,}', text.strip()))

def is_valid_phone_number(text: str) -> bool:
    return bool(re.fullmatch(r'09\d{9}', text.strip()))

def is_valid_student_id(text: str) -> bool:
    text = text.strip()
    return bool(re.fullmatch(r'40[0-4][0-3]\d{3}3', text)) or bool(re.fullmatch(r'99[0-3]\d{3}3', text))

def is_valid_entry_year(text: str) -> bool:
    return text.strip().isdigit() and text.strip() in {'1399', '1400', '1401', '1402', '1403'}

def is_valid_positive_integer(text: str) -> bool:
    return re.fullmatch(r"^\d+$", text) is not None

def vaildate_info(text: str):
    lines = text.strip().splitlines()
    if len(lines) < 6:
        return [False, "باید همه اطلاعات را در یک پیام بنویسید و بین هرکدام یک خط فاصله بگذارید"]

    if not is_valid_persian(lines[0]):
        return [False, "نام باید حتما به فارسی باشد"]
    if not is_valid_persian(lines[1]):
        return [False, "نام خانوادگی باید حتما به فارسی باشد"]
    if not is_valid_persian(lines[2]):
        return [False, "شهر باید حتما به فارسی باشد"]
    if not is_valid_phone_number(lines[3]):
        return [False, "لطفا شماره تلفن را به درستی وارد کنید"]
    if not is_valid_student_id(lines[4]):
        return [False, "شماره دانشجویی وارده معتبر نیست"]
    if not is_valid_entry_year(lines[5]):
        return [False, "لطفا سال ورودی را به درستی وارد کنید"]

    return [True, lines[:6]]

def extract_forward_info(text: str):
    match = re.match(r"https://t\.me/(?P<channel>\w+)/(?P<msg_id>\d+)", text)
    if match:
        return match.group('channel'), int(match.group('msg_id'))
    return None, None
