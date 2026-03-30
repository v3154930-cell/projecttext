from typing import Optional
from enum import Enum

class Step(str, Enum):
    START = "start"
    ASK_RECEIVER_FIO = "ask_receiver_fio"
    ASK_PASSPORT = "ask_passport"
    ASK_SENDER_FIO = "ask_sender_fio"
    ASK_AMOUNT = "ask_amount"
    ASK_RETURN_DATE = "ask_return_date"
    ASK_DATE = "ask_date"
    ASK_CITY = "ask_city"
    DONE = "done"

class ReceiptSimpleScenario:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.state = Step.START
        self.data = {}
        self.ready_to_generate = False
    
    def get_next_question(self) -> Optional[str]:
        if self.state == Step.START:
            return "Введите ФИО получателя (того, кто берет деньги):"
        elif self.state == Step.ASK_RECEIVER_FIO:
            return "Введите паспортные данные получателя (серия, номер, кем и когда выдан):"
        elif self.state == Step.ASK_PASSPORT:
            return "Введите ФИО передающего (того, кто дает деньги):"
        elif self.state == Step.ASK_SENDER_FIO:
            return "Введите сумму в рублях (только цифры):"
        elif self.state == Step.ASK_AMOUNT:
            return "Введите срок возврата (например: 25.12.2026):"
        elif self.state == Step.ASK_RETURN_DATE:
            return "Введите дату составления расписки (ДД.ММ.ГГГГ):"
        elif self.state == Step.ASK_DATE:
            return "Введите город составления расписки:"
        return None
    
    def process_answer(self, answer: str) -> Optional[str]:
        if self.state == Step.DONE:
            return None
        
        answer = answer.strip()
        
        if self.state == Step.START:
            if not answer:
                return "ФИО не может быть пустым. Введите ФИО получателя:"
            self.data['fio_receiver'] = answer
            self.state = Step.ASK_PASSPORT
            return self.get_next_question()
        
        if self.state == Step.ASK_RECEIVER_FIO:
            if not answer:
                return "Паспортные данные не могут быть пустыми. Введите серию, номер, кем и когда выдан:"
            self.data['passport'] = answer
            self.state = Step.ASK_SENDER_FIO
            return self.get_next_question()
        
        if self.state == Step.ASK_SENDER_FIO:
            if not answer:
                return "ФИО передающего не может быть пустым. Введите ФИО:"
            self.data['fio_sender'] = answer
            self.state = Step.ASK_AMOUNT
            return self.get_next_question()
        
        if self.state == Step.ASK_AMOUNT:
            try:
                amount = int(float(answer.replace(',', '.')))
                if amount <= 0:
                    return "Сумма должна быть больше нуля. Введите сумму в рублях:"
                self.data['amount'] = f"{amount:,}".replace(',', ' ')
            except ValueError:
                return "Пожалуйста, введите число (например: 50000 или 15000.50):"
            self.state = Step.ASK_RETURN_DATE
            return self.get_next_question()
        
        if self.state == Step.ASK_RETURN_DATE:
            if not answer:
                return "Введите срок возврата в формате ДД.ММ.ГГГГ (например: 25.12.2026):"
            self.data['return_date'] = answer
            self.state = Step.ASK_DATE
            return self.get_next_question()
        
        if self.state == Step.ASK_DATE:
            if not answer:
                return "Введите дату составления в формате ДД.ММ.ГГГГ:"
            self.data['date'] = answer
            self.state = Step.ASK_CITY
            return self.get_next_question()
        
        if self.state == Step.ASK_CITY:
            if not answer:
                return "Введите город составления расписки:"
            self.data['city'] = answer
            self.ready_to_generate = True
            self.state = Step.DONE
            return None
        
        return None
    
    def generate_document(self, template_path: str) -> str:
        if not self.ready_to_generate:
            raise ValueError("Невозможно сгенерировать документ: данные не собраны.")
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        try:
            document = template.format(**self.data)
            return document
        except KeyError as e:
            raise ValueError(f"Отсутствует необходимое поле для шаблона: {e}")
    
    def is_complete(self) -> bool:
        return self.ready_to_generate
    
    def get_current_step(self) -> str:
        return self.state.value