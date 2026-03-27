import re
from datetime import date as date_type
from typing import Callable


def required(answer: str, field_label: str = "Поле") -> str | None:
    if not answer:
        return f"{field_label} не может быть пустым"
    return None


def validate_date(answer: str) -> str | None:
    if not answer:
        return "Дата не может быть пустой"
    if re.search(r'[a-zA-Zа-яА-ЯёЁ]', answer):
        return "Дата должна содержать только цифры и точки:"
    parts = re.split(r'[.\s/\-]+', answer.strip())
    day = month = year = None
    if len(parts) == 3 and parts[0] and parts[1] and parts[2]:
        if len(parts[2]) in (2, 4):
            try:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError:
                pass
    if day is None:
        digits = re.sub(r'\D', '', answer)
        if len(digits) == 6:
            day, month, year = int(digits[0:2]), int(digits[2:4]), 2000 + int(digits[4:6])
        elif len(digits) == 8:
            day, month, year = int(digits[0:2]), int(digits[2:4]), int(digits[4:8])
    if day is None:
        return "Введите дату в формате ДД.ММ.ГГГГ:"
    if len(parts) == 3 and year and len(parts[2]) == 2:
        year = 2000 + year
    if not (1 <= month <= 12):
        return "Месяц должен быть от 1 до 12:"
    if not (1 <= day <= 31):
        return "День должен быть от 1 до 31:"
    if not (1900 <= year <= 2099):
        return "Год должен быть от 1900 до 2099:"
    try:
        date_type(year, month, day)
    except ValueError:
        return "Некорректная дата (проверьте день и месяц):"
    return None


def validate_money(answer: str) -> str | None:
    try:
        amount = float(answer.replace(',', '.'))
        if amount <= 0:
            return "Сумма должна быть больше нуля. Введите сумму в рублях:"
    except ValueError:
        return "Пожалуйста, введите число (например: 50000 или 15000.50):"
    return None


def validate_passport(answer: str) -> str | None:
    if not answer:
        return "Паспортные данные не могут быть пустыми. Введите серию, номер, кем и когда выдан:"
    return None


def validate_plain_text(answer: str) -> str | None:
    if not answer:
        return "Значение не может быть пустым"
    return None


def is_skip(answer: str) -> bool:
    return answer.strip().lower() in ["пропустить", "skip", ""]


def format_money(answer: str) -> str:
    amount = int(float(answer.replace(',', '.')))
    return f"{amount:,}".replace(',', ' ')


def normalize_percent(answer: str) -> str:
    if '%' in answer:
        return answer
    cleaned = answer.strip().replace(',', '.')
    try:
        float(cleaned)
        return answer.strip() + '%'
    except ValueError:
        return answer


def normalize_fio(answer: str) -> str:
    return answer.strip()


def normalize_passport(answer: str) -> str:
    return answer.strip()


def normalize_date(answer: str) -> str:
    answer = answer.strip()
    parts = re.split(r'[.\s/\-]+', answer)
    day = month = year = None
    if len(parts) == 3 and parts[0] and parts[1] and parts[2]:
        if len(parts[2]) in (2, 4):
            try:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError:
                pass
    if day is None:
        digits = re.sub(r'\D', '', answer)
        if len(digits) == 6:
            day, month, year = int(digits[0:2]), int(digits[2:4]), 2000 + int(digits[4:6])
        elif len(digits) == 8:
            day, month, year = int(digits[0:2]), int(digits[2:4]), int(digits[4:8])
    if day is None:
        return answer
    if len(parts) == 3 and year and len(parts[2]) == 2:
        year = 2000 + year
    try:
        date_type(year, month, day)
    except ValueError:
        return answer
    return f"{day:02d}.{month:02d}.{year}"


def _parse_ddmmyyyy(s: str):
    m = re.match(r'^(\d{2})\.(\d{2})\.(\d{4})$', s.strip())
    if m:
        return int(m.group(3)), int(m.group(2)), int(m.group(1))
    return None


def validate_date_after(earlier_key: str, field_label: str = "Дата") -> Callable:
    def _check(answer: str, data: dict) -> str | None:
        earlier = data.get(earlier_key)
        if not earlier:
            return None
        a = _parse_ddmmyyyy(answer)
        b = _parse_ddmmyyyy(earlier)
        if a and b:
            from datetime import date as _d
            if _d(*a) < _d(*b):
                return f"{field_label} не может быть раньше {earlier_key}:"
        return None
    return _check
