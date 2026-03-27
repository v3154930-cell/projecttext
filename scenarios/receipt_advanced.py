from framework import BaseScenario, FieldStep, FieldType, required, validate_date, validate_money, validate_passport, format_money, normalize_date, validate_date_after

STEPS = [
    FieldStep(
        name="start",
        question="",
    ),
    FieldStep(
        name="ask_receiver_fio",
        question="Введите ФИО получателя (того, кто берет деньги):",
        data_key="fio_receiver",
        field_type=FieldType.FIO,
        validators=[lambda a: required(a, "ФИО")],
    ),
    FieldStep(
        name="ask_passport",
        question="Введите паспортные данные получателя (серия, номер, кем и когда выдан):",
        data_key="passport",
        field_type=FieldType.PASSPORT,
        validators=[validate_passport],
    ),
    FieldStep(
        name="ask_sender_fio",
        question="Введите ФИО передающего (того, кто дает деньги):",
        data_key="fio_sender",
        field_type=FieldType.FIO,
        validators=[lambda a: required(a, "ФИО передающего")],
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
    FieldStep(
        name="ask_interest_rate",
        question="Укажите процентную ставку (например: 10% годовых):",
        data_key="interest_rate",
        field_type=FieldType.TEXT,
        optional=True,
    ),
    FieldStep(
        name="ask_interest_period",
        question="Укажите период начисления процентов (например: 'со дня получения до дня возврата'):",
        data_key="interest_period",
        field_type=FieldType.TEXT,
        optional=True,
        depends_on="interest_rate",
    ),
    FieldStep(
        name="ask_penalty",
        question="Укажите штраф/пени за просрочку (например: 0,1% от суммы за каждый день):",
        data_key="penalty",
        field_type=FieldType.TEXT,
        optional=True,
    ),
    FieldStep(
        name="ask_repayment_order",
        question="Укажите порядок возврата (например: 'наличными', 'переводом на карту'):",
        data_key="repayment_order",
        field_type=FieldType.TEXT,
        optional=True,
    ),
]


class ReceiptAdvancedScenario(BaseScenario):
    def __init__(self):
        super().__init__(steps=STEPS, template_path="templates/receipt_advanced.txt")
