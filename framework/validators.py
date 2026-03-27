import re
from datetime import date as date_type


def required(answer: str, field_label: str = "Поле") -> str | None:
    if not answer:
        return f"{field_label} не может быть пустым"
    return None


def validate_date(answer: str) -> str | None:
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', answer):
        return "Введите дату в формате ДД.ММ.ГГГГ:"
    try:
        day, month, year = map(int, answer.split('.'))
        date_type(year, month, day)
    except ValueError:
        return "Введите корректную дату в формате ДД.ММ.ГГГГ:"
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
