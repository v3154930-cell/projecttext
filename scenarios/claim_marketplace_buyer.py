from typing import Optional
from datetime import datetime
from framework import BaseScenario, FieldStep, FieldType, required, validate_date, validate_money, format_money, normalize_date
from framework.common_components import create_fio_step, create_passport_steps

PASSPORT_STEPS, PASSPORT_ASSEMBLER = create_passport_steps("ask_passport", "passport")

MARKETPLACE_REQUISITES = {
    "Ozon": {
        "full_name": "ООО \"Озон\"",
        "inn": "6345002063",
        "legal_address": "123112, г. Москва, Пресненская наб., д. 10, помещение 1, эт. 41, комн. 6"
    },
    "Wildberries": {
        "full_name": "ООО \"Вайлдберриз\"",
        "inn": "7714752299",
        "legal_address": "142181, Московская область, г. Подольск, деревня Коледино, Территория Индустриальный парк Коледино, дом 6, стр.1"
    },
    "Yandex.Market": {
        "full_name": "ООО \"Яндекс Маркет\"",
        "inn": "9704254424",
        "legal_address": "121099, г. Москва, Новинский б-р, д. 8, пом. 9.03, этаж 9"
    }
}

def validate_recipient_type(value: str) -> Optional[str]:
    if not value:
        return "Выберите тип получателя"
    value = value.strip()
    valid = ["1", "2", "3"]
    if value not in valid:
        return "Введите 1, 2 или 3"
    return None

def normalize_recipient_type(value: str) -> str:
    types = {"1": "marketplace", "2": "inn", "3": "manual"}
    return types.get(value.strip(), value)

def validate_is_marketplace(value: str) -> bool:
    return value == "marketplace"

def should_show_for_marketplace(data: dict) -> bool:
    return data.get("recipient_type") == "marketplace"

def should_show_for_inn(data: dict) -> bool:
    return data.get("recipient_type") == "inn"

def should_show_for_manual(data: dict) -> bool:
    return data.get("recipient_type") == "manual"

def should_show_for_delivery_or_cancelled(data: dict) -> bool:
    return data.get("claim_reason") in ("delivery", "cancelled")

def validate_platform(value: str) -> Optional[str]:
    if not value:
        return "Выберите маркетплейс"
    value = value.strip()
    valid = ["1", "2", "3"]
    if value not in valid:
        return "Введите 1, 2 или 3"
    return None

def normalize_platform(value: str) -> str:
    platforms = {"1": "Ozon", "2": "Wildberries", "3": "Yandex.Market"}
    return platforms.get(value.strip(), value)

def post_process_platform(data: dict) -> dict:
    platform = data.get("platform", "")
    if platform in MARKETPLACE_REQUISITES:
        req = MARKETPLACE_REQUISITES[platform]
        data["seller_full_name"] = req["full_name"]
        data["seller_inn"] = req["inn"]
        data["seller_legal_address"] = req["legal_address"]
        data["seller_kpp"] = ""
    return data

def validate_seller_inn(value: str) -> Optional[str]:
    if not value:
        return "Введите ИНН (10 или 12 цифр)"
    value = value.strip()
    if len(value) not in [10, 12]:
        return "ИНН должен быть 10 (ЮЛ) или 12 (ИП) цифр"
    if not value.isdigit():
        return "ИНН должен содержать только цифры"
    return None

def validate_condition(value: str) -> Optional[str]:
    if not value:
        return None
    value = value.strip()
    valid = ["1", "2"]
    if value not in valid:
        return "Введите 1 или 2, или пропустите"
    return None

def normalize_condition(value: str) -> str:
    if not value:
        return ""
    conditions = {"1": "упаковка не вскрыта", "2": "товар примеряли"}
    return conditions.get(value.strip(), value)

def validate_claim_reason(value: str) -> Optional[str]:
    if not value:
        return "Выберите причину претензии"
    value = value.strip()
    valid = ["1", "2", "3", "4"]
    if value not in valid:
        return "Введите 1, 2, 3 или 4"
    return None

def normalize_claim_reason(value: str) -> str:
    reasons = {"1": "not_suitable", "2": "defect", "3": "delivery", "4": "cancelled"}
    return reasons.get(value.strip(), value)

STEPS = [
    FieldStep(name="start", question=""),
    FieldStep(
        name="ask_recipient_type",
        question="Выберите, кому направляется претензия:\n\n1. Маркетплейс (Ozon, WB, Яндекс)\n2. Организация по ИНН (поиск через ФНС)\n3. Заполню реквизиты самостоятельно\n\nВведите номер:",
        data_key="recipient_type",
        field_type=FieldType.TEXT,
        validators=[validate_recipient_type],
        post_process=normalize_recipient_type,
    ),
    FieldStep(
        name="ask_platform",
        question="Выберите маркетплейс:\n\n1. Ozon\n2. Wildberries\n3. Яндекс Маркет\n\nВведите номер:",
        data_key="platform",
        field_type=FieldType.TEXT,
        should_show=should_show_for_marketplace,
        validators=[validate_platform],
        post_process=normalize_platform,
    ),
    FieldStep(
        name="ask_seller_inn",
        question="Введите ИНН организации (10 или 12 цифр):",
        data_key="seller_inn",
        field_type=FieldType.TEXT,
        should_show=should_show_for_inn,
        validators=[validate_seller_inn],
    ),
    FieldStep(
        name="ask_seller_full_name",
        question="Введите полное наименование организации:",
        data_key="seller_full_name",
        field_type=FieldType.TEXT,
        should_show=should_show_for_inn,
        validators=[lambda a: required(a, "Наименование организации")],
    ),
    FieldStep(
        name="ask_seller_inn_manual",
        question="ИНН организации (опционально, 10 или 12 цифр):",
        data_key="seller_inn",
        field_type=FieldType.TEXT,
        should_show=should_show_for_manual,
        optional=True,
    ),
    FieldStep(
        name="ask_seller_legal_address",
        question="Юридический адрес:",
        data_key="seller_legal_address",
        field_type=FieldType.TEXT,
        should_show=should_show_for_manual,
        validators=[lambda a: required(a, "Юридический адрес")],
    ),
    FieldStep(name="ask_order_number", question="Введите номер заказа:", data_key="order_number", field_type=FieldType.TEXT, validators=[lambda a: required(a, "Номер заказа")]),
    FieldStep(name="ask_product_name", question="Введите наименование товара:", data_key="product_name", field_type=FieldType.TEXT, validators=[lambda a: required(a, "Наименование товара")]),
    FieldStep(name="ask_amount", question="Введите сумму в рублях (только цифры):", data_key="amount", field_type=FieldType.MONEY, validators=[validate_money], post_process=format_money),
    create_fio_step(name="ask_full_name", question="Введите ваше ФИО:", data_key="full_name", role_label="ФИО"),
    *PASSPORT_STEPS,
    FieldStep(name="ask_date", question="Введите дату подачи претензии (ДД.ММ.ГГГГ):", data_key="date", field_type=FieldType.DATE, validators=[validate_date], post_process=normalize_date),
    FieldStep(name="ask_receipt_date", question="Введите дату получения товара (ДД.ММ.ГГГГ), или нажмите 'Пропустить':", data_key="receipt_date", field_type=FieldType.DATE, optional=True, validators=[validate_date], post_process=normalize_date),
    FieldStep(name="ask_condition", question="Выберите состояние товара:\n\n1. Упаковка не вскрыта\n2. Товар примеряли\n\nВведите номер (или пропустите):", data_key="condition", field_type=FieldType.TEXT, optional=True, validators=[validate_condition], post_process=normalize_condition),
    FieldStep(
        name="ask_claim_reason",
        question="Выберите причину претензии:\n\n1. Товар не подошёл (цвет, размер, фасон)\n2. Товар сломался / брак / не работает\n3. Нарушен срок доставки\n4. Заказ отменён маркетплейсом\n\nВведите номер:",
        data_key="claim_reason",
        field_type=FieldType.TEXT,
        validators=[validate_claim_reason],
        post_process=normalize_claim_reason,
    ),
    FieldStep(
        name="ask_prepayment_date",
        question="Введите дату оплаты заказа (ДД.ММ.ГГГГ):",
        data_key="prepayment_date",
        field_type=FieldType.DATE,
        should_show=should_show_for_delivery_or_cancelled,
        validators=[validate_date],
        post_process=normalize_date,
    ),
    FieldStep(
        name="ask_prepayment_amount",
        question="Введите сумму предоплаты в рублях:",
        data_key="prepayment_amount",
        field_type=FieldType.MONEY,
        should_show=should_show_for_delivery_or_cancelled,
        validators=[validate_money],
        post_process=format_money,
    ),
    FieldStep(
        name="ask_refund_date",
        question="Введите дату возврата денег (ДД.ММ.ГГГГ), или нажмите 'Пропустить' если деньги ещё не возвращены:",
        data_key="refund_date",
        field_type=FieldType.DATE,
        should_show=should_show_for_delivery_or_cancelled,
        optional=True,
        validators=[validate_date],
        post_process=normalize_date,
    ),
]


class ClaimMarketplaceBuyerScenario(BaseScenario):
    TEMPLATE_MAP = {
        "not_suitable": "templates/claim_not_suitable.txt",
        "defect": "templates/claim_defect.txt",
        "delivery": "templates/claim_delivery.txt",
        "cancelled": "templates/claim_cancelled.txt",
    }

    def __init__(self):
        super().__init__(steps=STEPS, template_path="templates/claim_marketplace_buyer.txt")
        self._preview_enabled = True
        self._field_assemblers["passport"] = PASSPORT_ASSEMBLER

    def _get_receipt_date_text(self):
        receipt_date = self.data.get("receipt_date", "")
        if receipt_date:
            return f"Дата получения товара: {receipt_date}.\n"
        return ""

    def _get_condition_text(self):
        condition = self.data.get("condition", "")
        if condition:
            return f"{condition}, "
        return ""

    def calculate_penalty(self, prepayment_amount: float, prepayment_date: str, refund_date: Optional[str] = None) -> float:
        if not prepayment_amount or not prepayment_date:
            return 0.0
        
        parsed_prepayment_date = self._parse_date(prepayment_date)
        if not parsed_prepayment_date:
            return 0.0
        
        if refund_date:
            parsed_refund_date = self._parse_date(refund_date)
        else:
            parsed_refund_date = datetime.now()
        
        if not parsed_refund_date:
            return 0.0
        
        days = (parsed_refund_date - parsed_prepayment_date).days
        if days < 0:
            days = 0
        
        penalty = prepayment_amount * 0.005 * days
        return round(penalty, 2)

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            if '.' in date_str:
                parts = date_str.split('.')
                if len(parts) == 3:
                    return datetime(int(parts[2]), int(parts[1]), int(parts[0]))
            return datetime.strptime(date_str[:10], '%Y-%m-%d')
        except Exception:
            return None

    def _get_penalty_block(self) -> str:
        claim_reason = self.data.get("claim_reason", "")
        if claim_reason not in ("delivery", "cancelled"):
            return ""
        
        prepayment_amount = self.data.get("prepayment_amount", "")
        prepayment_date = self.data.get("prepayment_date", "")
        
        if not prepayment_amount or not prepayment_date:
            return ""
        
        try:
            amount_float = float(str(prepayment_amount).replace(' ', '').replace('₽', '').replace(',', '.'))
        except (ValueError, TypeError):
            amount_float = 0.0
        
        refund_date = self.data.get("refund_date", "")
        penalty = self.calculate_penalty(amount_float, prepayment_date, refund_date if refund_date else None)
        
        if penalty <= 0:
            return ""
        
        days = (datetime.now() - self._parse_date(prepayment_date)).days if not refund_date else (self._parse_date(refund_date) - self._parse_date(prepayment_date)).days
        
        return f"""
РАСЧЁТ НЕУСТОЙКИ:
- Сумма предоплаты: {prepayment_amount} руб.
- Дата оплаты: {prepayment_date}
- Период просрочки: {days} дней
- Размер неустойки (0,5% в день): {penalty} руб.

Неустойка рассчитана в соответствии со ст. 28 Закона РФ "О защите прав потребителей".
"""

    def generate_document(self, template_path: Optional[str] = None) -> str:
        claim_reason = self.data.get("claim_reason", "")
        if claim_reason in self.TEMPLATE_MAP:
            path = self.TEMPLATE_MAP[claim_reason]
        else:
            path = template_path or self._template_path
        
        self.data["receipt_date_text"] = self._get_receipt_date_text()
        self.data["condition_text"] = self._get_condition_text()
        self.data["penalty_block"] = self._get_penalty_block()
        
        return super().generate_document(path)

    def _advance_to_next_step(self):
        prev_index = self._current_index
        result = super()._advance_to_next_step()
        if prev_index < len(self._steps):
            step_name = self._steps[prev_index].name
            if step_name == "ask_platform" and self.data.get("platform"):
                self.data = post_process_platform(self.data)
        return result
