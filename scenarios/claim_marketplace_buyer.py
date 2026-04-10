from typing import Optional
from framework import BaseScenario, FieldStep, FieldType, required, validate_date, validate_money, format_money, normalize_date
from framework.common_components import create_fio_step, create_passport_steps

PASSPORT_STEPS, PASSPORT_ASSEMBLER = create_passport_steps("ask_passport", "passport")

def validate_platform(value: str) -> Optional[str]:
    """Валидация выбора маркетплейса."""
    if not value:
        return "Выберите маркетплейс"
    value = value.strip()
    valid_platforms = ["1", "2", "3"]
    if value not in valid_platforms:
        return "Введите 1, 2 или 3"
    return None

def normalize_platform(value: str) -> str:
    """Нормализация выбора маркетплейса."""
    platforms = {"1": "Ozon", "2": "Wildberries", "3": "Яндекс Маркет"}
    return platforms.get(value.strip(), value)

def validate_condition(value: str) -> Optional[str]:
    """Валидация состояния товара."""
    if not value:
        return None
    value = value.strip()
    valid = ["1", "2"]
    if value not in valid:
        return "Введите 1 или 2, или пропустите"
    return None

def normalize_condition(value: str) -> str:
    """Нормализация состояния товара."""
    if not value:
        return ""
    conditions = {"1": "упаковка не вскрыта", "2": "товар примеряли"}
    return conditions.get(value.strip(), value)

STEPS = [
    FieldStep(
        name="start",
        question="",
    ),
    FieldStep(
        name="ask_platform",
        question="Выберите маркетплейс:\n\n1. Ozon\n2. Wildberries\n3. Яндекс Маркет\n\nВведите номер:",
        data_key="platform",
        field_type=FieldType.TEXT,
        validators=[validate_platform],
        post_process=normalize_platform,
    ),
    FieldStep(
        name="ask_order_number",
        question="Введите номер заказа:",
        data_key="order_number",
        field_type=FieldType.TEXT,
        validators=[lambda a: required(a, "Номер заказа")],
    ),
    FieldStep(
        name="ask_product_name",
        question="Введите наименование товара:",
        data_key="product_name",
        field_type=FieldType.TEXT,
        validators=[lambda a: required(a, "Наименование товара")],
    ),
    FieldStep(
        name="ask_amount",
        question="Введите сумму в рублях (только цифры):",
        data_key="amount",
        field_type=FieldType.MONEY,
        validators=[validate_money],
        post_process=format_money,
    ),
    create_fio_step(
        name="ask_full_name",
        question="Введите ваше ФИО:",
        data_key="full_name",
        role_label="ФИО",
    ),
    *PASSPORT_STEPS,
    FieldStep(
        name="ask_date",
        question="Введите дату подачи претензии (ДД.ММ.ГГГГ):",
        data_key="date",
        field_type=FieldType.DATE,
        validators=[validate_date],
        post_process=normalize_date,
    ),
    FieldStep(
        name="ask_receipt_date",
        question="Введите дату получения товара (ДД.ММ.ГГГГ), или нажмите 'Пропустить':",
        data_key="receipt_date",
        field_type=FieldType.DATE,
        optional=True,
        validators=[validate_date],
        post_process=normalize_date,
    ),
    FieldStep(
        name="ask_condition",
        question="Выберите состояние товара:\n\n1. Упаковка не вскрыта\n2. Товар примеряли\n\nВведите номер (или пропустите):",
        data_key="condition",
        field_type=FieldType.TEXT,
        optional=True,
        validators=[validate_condition],
        post_process=normalize_condition,
    ),
]


class ClaimMarketplaceBuyerScenario(BaseScenario):
    def __init__(self):
        super().__init__(steps=STEPS, template_path="templates/claim_marketplace_buyer.txt")
        self._preview_enabled = True
        self._field_assemblers["passport"] = PASSPORT_ASSEMBLER