import datetime
from framework import BaseScenario, FieldStep, FieldType, required, validate_date, validate_money, validate_passport, format_money, normalize_date, validate_date_after, normalize_percent, normalize_fio
from framework.common_components import create_fio_step, create_passport_steps

LENDER_PASSPORT_STEPS, LENDER_PASSPORT_ASSEMBLER = create_passport_steps("ask_lender_passport", "lender_passport")
BORROWER_PASSPORT_STEPS, BORROWER_PASSPORT_ASSEMBLER = create_passport_steps("ask_borrower_passport", "borrower_passport")

STEPS = [
    FieldStep(
        name="start",
        question="",
    ),
    create_fio_step(
        name="ask_lender",
        question="Введите займодавца (ФИО или наименование организации):",
        data_key="lender",
        role_label="Займодавец",
    ),
    *LENDER_PASSPORT_STEPS,
    create_fio_step(
        name="ask_borrower",
        question="Введите заемщика (ФИО или наименование организации):",
        data_key="borrower",
        role_label="Заемщик",
    ),
    *BORROWER_PASSPORT_STEPS,
    FieldStep(
        name="ask_amount",
        question="Введите сумму займа в рублях (только цифры):",
        data_key="amount",
        field_type=FieldType.MONEY,
        validators=[validate_money],
        post_process=format_money,
    ),
    FieldStep(
        name="ask_date",
        question="Введите дату составления договора (ДД.ММ.ГГГГ):",
        data_key="date",
        field_type=FieldType.DATE,
        validators=[validate_date],
        post_process=normalize_date,
    ),
    FieldStep(
        name="ask_term",
        question="Введите срок возврата займа (например: 25.12.2026):",
        data_key="term",
        field_type=FieldType.DATE,
        validators=[validate_date],
        post_process=normalize_date,
        cross_validators=[validate_date_after("date", "Срок возврата не может быть раньше даты составления договора")],
    ),
    FieldStep(
        name="ask_interest_rate",
        question="Укажите процентную ставку (например: 10% годовых):",
        data_key="interest_rate",
        field_type=FieldType.TEXT,
        optional=True,
        post_process=normalize_percent,
    ),
    FieldStep(
        name="ask_payment_option",
        question="Выберите вариант погашения процентов:\n\n1. Единовременно в конце срока\n2. Ежемесячно (аннуитетные платежи)\n3. Ежемесячно (дифференцированные платежи)\n\nВведите номер варианта (или пропустите):",
        data_key="payment_option",
        field_type=FieldType.TEXT,
        optional=True,
        depends_on="interest_rate",
    ),
    FieldStep(
        name="ask_city",
        question="Введите город составления договора:",
        data_key="city",
        field_type=FieldType.TEXT,
        validators=[lambda a: required(a, "Город")],
    ),
    FieldStep(
        name="ask_purpose",
        question="Укажите цель займа:",
        data_key="purpose",
        field_type=FieldType.TEXT,
        optional=True,
    ),
    FieldStep(
        name="ask_penalty",
        question="Укажите неустойку за просрочку (например: 0,1% от суммы за каждый день):",
        data_key="penalty",
        field_type=FieldType.TEXT,
        optional=True,
        post_process=normalize_percent,
    ),
    FieldStep(
        name="ask_collateral",
        question="Укажите обеспечение (например: залог, поручительство):",
        data_key="collateral",
        field_type=FieldType.TEXT,
        optional=True,
    ),
]


class LoanScenario(BaseScenario):
    def __init__(self):
        super().__init__(steps=STEPS, template_path="templates/loan.txt")
        self._preview_enabled = True
        self._field_assemblers["lender_passport"] = LENDER_PASSPORT_ASSEMBLER
        self._field_assemblers["borrower_passport"] = BORROWER_PASSPORT_ASSEMBLER
        self.data["contract_number"] = f"ДЗ-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    def reset(self):
        super().reset()
        self.data["days"] = "3"
        self.data["notice_days"] = "30"
