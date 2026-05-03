from typing import Optional
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

def validate_platform(value: str):
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
        data["platform_full_name"] = req["full_name"]
        data["platform_inn"] = req["inn"]
        data["platform_legal_address"] = req["legal_address"]
    return data

def validate_seller_inn(value: str):
    if not value:
        return "Введите ИНН (10 или 12 цифр)"
    value = value.strip()
    if len(value) not in [10, 12]:
        return "ИНН должен быть 10 (ЮЛ) или 12 (ИП) цифр"
    if not value.isdigit():
        return "ИНН должен содержать только цифры"
    return None

STEPS = [
    FieldStep(name="start", question=""),
    FieldStep(
        name="ask_platform",
        question="Выберите маркетплейс:\n\n1. Ozon\n2. Wildberries\n3. Яндекс Маркет\n\nВведите номер:",
        data_key="platform",
        field_type=FieldType.TEXT,
        validators=[validate_platform],
        post_process=normalize_platform,
    ),
    FieldStep(name="ask_seller_name", question="Введите наименование вашей организации:", data_key="seller_name", field_type=FieldType.TEXT, validators=[lambda a: required(a, "Наименование организации")]),
    FieldStep(name="ask_seller_inn", question="Введите ваш ИНН (10 или 12 цифр):", data_key="seller_inn", field_type=FieldType.TEXT, validators=[validate_seller_inn]),
    FieldStep(name="ask_report_date", question="Введите дату вынесения штрафа (ДД.ММ.ГГГГ):", data_key="report_date", field_type=FieldType.DATE, validators=[validate_date], post_process=normalize_date),
    FieldStep(name="ask_article", question="Введите артикул товара:", data_key="article", field_type=FieldType.TEXT, validators=[lambda a: required(a, "Артикул товара")]),
    FieldStep(name="ask_declared_dimensions", question="Введите заявленные габариты (ДхШхВ, см):", data_key="declared_dimensions", field_type=FieldType.TEXT, validators=[lambda a: required(a, "Заявленные габариты")]),
    FieldStep(name="ask_actual_dimensions", question="Введите фактические габариты (ДхШхВ, см):", data_key="actual_dimensions", field_type=FieldType.TEXT, validators=[lambda a: required(a, "Фактические габариты")]),
    FieldStep(name="ask_penalty_amount", question="Введите размер штрафа в рублях:", data_key="penalty_amount", field_type=FieldType.MONEY, validators=[validate_money], post_process=format_money),
    create_fio_step(name="ask_full_name", question="Введите ваше ФИО:", data_key="full_name", role_label="ФИО"),
    *PASSPORT_STEPS,
    FieldStep(name="ask_date", question="Введите дату подачи претензии (ДД.ММ.ГГГГ):", data_key="date", field_type=FieldType.DATE, validators=[validate_date], post_process=normalize_date),
]

class SellerClaimDimensionsScenario(BaseScenario):
    def __init__(self):
        super().__init__(steps=STEPS, template_path="templates/seller_claim_dimensions.txt")
        self._preview_enabled = True
        self._field_assemblers["passport"] = PASSPORT_ASSEMBLER

    def generate_document(self, template_path=None):
        self.data["seller_full_name"] = self.data.get("seller_name", "")
        self.data["seller_legal_address"] = ""
        self.data["seller_kpp"] = ""
        return super().generate_document(template_path)

    def _advance_to_next_step(self):
        prev_index = self._current_index
        result = super()._advance_to_next_step()
        if prev_index < len(self._steps):
            step_name = self._steps[prev_index].name
            if step_name == "ask_platform" and self.data.get("platform"):
                self.data = post_process_platform(self.data)
        return result