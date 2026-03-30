from framework.step import FieldStep
from framework.fields import FieldType
from framework.validators import (
    required, validate_passport, normalize_fio, normalize_passport,
    validate_passport_series, normalize_passport_series,
    validate_passport_number, normalize_passport_number,
    validate_date, normalize_date,
)


def create_fio_step(name: str, question: str, data_key: str, role_label: str = "ФИО") -> FieldStep:
    """
    Создает шаг для ввода ФИО.
    
    Args:
        name: имя шага
        question: вопрос пользователю
        data_key: ключ для сохранения данных
        role_label: метка роли для валидации (например "ФИО", "ФИО передающего")
    
    Returns:
        FieldStep: готовый шаг для использования в сценарии
    """
    return FieldStep(
        name=name,
        question=question,
        data_key=data_key,
        field_type=FieldType.FIO,
        validators=[lambda a: required(a, role_label)],
        post_process=normalize_fio,
    )


def create_passport_step(name: str, question: str, data_key: str) -> FieldStep:
    """
    Создает шаг для ввода паспортных данных.
    
    Args:
        name: имя шага
        question: вопрос пользователю
        data_key: ключ для сохранения данных
    
    Returns:
        FieldStep: готовый шаг для использования в сценарии
    """
    return FieldStep(
        name=name,
        question=question,
        data_key=data_key,
        field_type=FieldType.PASSPORT,
        validators=[validate_passport],
        post_process=normalize_passport,
    )


def create_passport_steps(base_name: str, base_key: str):
    """
    Создаёт набор шагов для структурированного ввода паспорта.
    
    Args:
        base_name: базовая часть имени шагов (например "ask_passport")
        base_key: базовая часть ключей данных (например "passport")
    
    Returns:
        tuple: (list[FieldStep], assembler_fn)
            список шагов и функция-сборщик для регистрации через _field_assemblers
    """
    steps = [
        FieldStep(
            name=f"{base_name}_series",
            question="Введите серию паспорта (4 цифры):",
            data_key=f"{base_key}_series",
            field_type=FieldType.TEXT,
            validators=[validate_passport_series],
            post_process=normalize_passport_series,
        ),
        FieldStep(
            name=f"{base_name}_number",
            question="Введите номер паспорта (6 цифр):",
            data_key=f"{base_key}_number",
            field_type=FieldType.TEXT,
            validators=[validate_passport_number],
            post_process=normalize_passport_number,
        ),
        FieldStep(
            name=f"{base_name}_issued_by",
            question="Кем выдан паспорт:",
            data_key=f"{base_key}_issued_by",
            field_type=FieldType.TEXT,
            validators=[lambda a: required(a, "Кем выдан")],
        ),
        FieldStep(
            name=f"{base_name}_date",
            question="Дата выдачи паспорта (ДД.ММ.ГГГГ):",
            data_key=f"{base_key}_date",
            field_type=FieldType.DATE,
            validators=[validate_date],
            post_process=normalize_date,
        ),
        FieldStep(
            name=f"{base_name}_code",
            question="Код подразделения (6 цифр, или нажмите 'Пропустить'):",
            data_key=f"{base_key}_code",
            field_type=FieldType.TEXT,
            optional=True,
        ),
    ]

    def assembler(data):
        series = data.get(f"{base_key}_series", "")
        number = data.get(f"{base_key}_number", "")
        issued_by = data.get(f"{base_key}_issued_by", "")
        date = data.get(f"{base_key}_date", "")
        code = data.get(f"{base_key}_code", "")
        parts = [f"{series} {number}", f"выдан {issued_by}", f"{date}"]
        if code:
            parts.append(f"код подразделения {code}")
        return ", ".join(parts)

    return steps, assembler