from typing import Optional
from framework import BaseScenario, FieldStep, FieldType, required, validate_date, validate_money, validate_passport, format_money, normalize_date, validate_date_after, normalize_fio, normalize_passport
from framework.common_components import create_fio_step, create_passport_step

class ReceiptSimpleScenario(BaseScenario):
    PREVIEW_STEP = "preview"

    def __init__(self):
        super().__init__(steps=STEPS, template_path="templates/receipt_simple.txt")
        self._in_preview = False
        self._preview_document = ""

    def is_complete(self) -> bool:
        return self._ready_to_generate and not self._in_preview

    def get_next_question(self) -> Optional[str]:
        if self._in_preview:
            return "Проверьте правильность заполнения:\n\n" + self._preview_document + "\n\nВыберите действие:\n1. Подтвердить\n2. Редактировать"
        return super().get_next_question()

    def is_current_optional(self) -> bool:
        if self._in_preview:
            return False
        return super().is_current_optional()

    def get_current_field_type(self) -> Optional[str]:
        if self._in_preview:
            return "preview"
        return super().get_current_field_type()

    def process_answer(self, answer: str) -> Optional[str]:
        if self._in_preview:
            answer = answer.strip().lower()
            if answer in ["1", "подтвердить", "confirm"]:
                self._in_preview = False
                return None
            elif answer in ["2", "редактировать", "edit"]:
                self._in_preview = False
                self._ready_to_generate = False
                self._current_index = len(self._steps) - 1
                return None
            else:
                return "Пожалуйста, выберите: 1 - Подтвердить, 2 - Редактировать"
        
        result = super().process_answer(answer)
        
        if self._ready_to_generate and not self._in_preview:
            try:
                self._preview_document = self.generate_document()
                self._in_preview = True
                return self.get_next_question()
            except Exception:
                self._ready_to_generate = False
                return "Ошибка генерации документа. Пожалуйста, проверьте введенные данные."
        
        return result

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
    create_passport_step(
        name="ask_passport",
        question="Введите паспортные данные получателя (серия, номер, кем и когда выдан):",
        data_key="passport",
    ),
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
