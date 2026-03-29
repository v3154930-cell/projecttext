from framework.step import FieldStep
from framework.fields import FieldType
from framework.validators import required, validate_passport, normalize_fio, normalize_passport


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