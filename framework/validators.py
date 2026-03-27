import re
from datetime import date as date_type


def required(answer: str, field_label: str = "Поле") -> str | None:
    if not answer:
        return f"{field_label} не может быть пустым"
    return None


def validate_date(answer: str) -> str | None:
    if not answer:
        return "Дата не может быть пустой"
    digits = re.sub(r'\D', '', answer)
    if not digits:
        return "Введите дату цифрами (например: 02.03.2026 или 020326):"
    if len(digits) > 8:
        return "Слишком много цифр. Максимум 8 цифр для даты:"
    if re.search(r'[a-zA-Zа-яА-ЯёЁ]', answer):
        return "Дата должна содержать только цифры и точки:"
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


def normalize_date(answer: str) -> str:
    answer = answer.strip()
    parts = re.split(r'[.\s/\-]+', answer)
    if len(parts) == 3:
        try:
            d_str, m_str, y_str = parts
            if not d_str or not m_str or not y_str:
                return answer
            if len(y_str) not in (2, 4):
                return answer
            day = int(d_str)
            month = int(m_str)
            year = int(y_str)
            if len(y_str) == 2:
                year = 2000 + year
            date_type(year, month, day)
            return f"{day:02d}.{month:02d}.{year}"
        except (ValueError, TypeError):
            return answer
    digits = re.sub(r'\D', '', answer)
    if len(digits) == 6:
        day, month, year = int(digits[0:2]), int(digits[2:4]), 2000 + int(digits[4:6])
    elif len(digits) == 8:
        day, month, year = int(digits[0:2]), int(digits[2:4]), int(digits[4:8])
    else:
        return answer
    try:
        date_type(year, month, day)
    except ValueError:
        return answer
    return f"{day:02d}.{month:02d}.{year}"
