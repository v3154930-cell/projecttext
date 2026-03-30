from framework import BaseScenario, FieldStep, FieldType, required, validate_date, validate_money, format_money, normalize_date, validate_date_after, normalize_fio
from framework.common_components import create_fio_step, create_passport_steps

PASSPORT_STEPS, PASSPORT_ASSEMBLER = create_passport_steps("ask_passport", "passport")

STEPS = [
    FieldStep(
        name="start",
        question="",
    ),
    create_fio_step(
        name="ask_receiver_fio",
        question="Введите ФИО получателя (того, кто берет деньги):",
        data_key="fio_receiver",
        role_label="ФИО",
    ),
    *PASSPORT_STEPS,
    create_fio_step(
        name="ask_sender_fio",
        question="Введите ФИО передающего (того, кто дает деньги):",
        data_key="fio_sender",
        role_label="ФИО передающего",
    ),
    FieldStep(
        name="ask_amount",
        question="Введите сумму в рублях (только цифры):",
        data_key="amount",
        field_type=FieldType.MONEY,
        validators=[validate_money],
        post_process=format_money,
    ),
    FieldStep(
        name="ask_date",
        question="Введите дату составления расписки (ДД.ММ.ГГГГ):",
        data_key="date",
        field_type=FieldType.DATE,
        validators=[validate_date],
        post_process=normalize_date,
    ),
    FieldStep(
        name="ask_return_date",
        question="Введите срок возврата (например: 25.12.2026):",
        data_key="return_date",
        field_type=FieldType.DATE,
        validators=[validate_date],
        post_process=normalize_date,
        cross_validators=[validate_date_after("date", "Дата возврата не может быть раньше даты составления расписки")],
    ),
    FieldStep(
        name="ask_city",
        question="Введите город составления расписки:",
        data_key="city",
        field_type=FieldType.TEXT,
        validators=[lambda a: required(a, "Город")],
    ),
]


class ReceiptSimpleScenario(BaseScenario):
    def __init__(self):
        super().__init__(steps=STEPS, template_path="templates/receipt_simple.txt")
        self._preview_enabled = True
        self._field_assemblers["passport"] = PASSPORT_ASSEMBLER
