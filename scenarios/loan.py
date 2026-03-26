from typing import Optional
from enum import Enum

class Step(str, Enum):
    START = "start"
    ASK_LENDER = "ask_lender"
    ASK_BORROWER = "ask_borrower"
    ASK_AMOUNT = "ask_amount"
    ASK_TERM = "ask_term"
    ASK_INTEREST_RATE = "ask_interest_rate"
    ASK_REPAYMENT_METHOD = "ask_repayment_method"
    ASK_DATE = "ask_date"
    ASK_CITY = "ask_city"
    ASK_PURPOSE = "ask_purpose"
    ASK_PENALTY = "ask_penalty"
    ASK_COLLATERAL = "ask_collateral"
    DONE = "done"

class LoanScenario:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.state = Step.START
        self.data = {}
        self.ready_to_generate = False
    
    def get_next_question(self) -> Optional[str]:
        if self.state == Step.START:
            return None
        elif self.state == Step.ASK_LENDER:
            return "Введите займодавца (ФИО или наименование организации):"
        elif self.state == Step.ASK_BORROWER:
            return "Введите заемщика (ФИО или наименование организации):"
        elif self.state == Step.ASK_AMOUNT:
            return "Введите сумму займа в рублях (только цифры):"
        elif self.state == Step.ASK_TERM:
            return "Введите срок возврата займа (например: 25.12.2026):"
        elif self.state == Step.ASK_INTEREST_RATE:
            return "Укажите процентную ставку (например: 10% годовых) или введите 'пропустить':"
        elif self.state == Step.ASK_REPAYMENT_METHOD:
            return "Укажите порядок возврата (например: 'единовременно', 'по частям'):"
        elif self.state == Step.ASK_DATE:
            return "Введите дату составления договора (ДД.ММ.ГГГГ):"
        elif self.state == Step.ASK_CITY:
            return "Введите город составления договора:"
        elif self.state == Step.ASK_PURPOSE:
            return "Укажите цель займа или введите 'пропустить':"
        elif self.state == Step.ASK_PENALTY:
            return "Укажите неустойку за просрочку (например: 0,1% от суммы за каждый день) или 'пропустить':"
        elif self.state == Step.ASK_COLLATERAL:
            return "Укажите обеспечение (например: залог, поручительство) или введите 'пропустить':"
        return None
    
    def is_skip(self, answer: str) -> bool:
        return answer.strip().lower() in ["пропустить", "skip", ""]
    
    def process_answer(self, answer: str) -> Optional[str]:
        if self.state == Step.DONE:
            return None
        
        answer = answer.strip()
        
        # START - инициализация сценария
        if self.state == Step.START:
            self.state = Step.ASK_LENDER
            return self.get_next_question()
        
        # Обязательные шаги
        if self.state == Step.ASK_LENDER:
            if not answer:
                return "Займодавец не может быть пустым. Введите ФИО или наименование организации:"
            self.data['lender'] = answer
            self.state = Step.ASK_BORROWER
            return self.get_next_question()
        
        if self.state == Step.ASK_BORROWER:
            if not answer:
                return "Заемщик не может быть пустым. Введите ФИО или наименование организации:"
            self.data['borrower'] = answer
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
            self.state = Step.ASK_TERM
            return self.get_next_question()
        
        if self.state == Step.ASK_TERM:
            if not answer:
                return "Введите срок возврата в формате ДД.ММ.ГГГГ (например: 25.12.2026):"
            self.data['term'] = answer
            self.state = Step.ASK_INTEREST_RATE
            return self.get_next_question()
        
        if self.state == Step.ASK_INTEREST_RATE:
            if not self.is_skip(answer):
                self.data['interest_rate'] = answer
            self.state = Step.ASK_REPAYMENT_METHOD
            return self.get_next_question()
        
        if self.state == Step.ASK_REPAYMENT_METHOD:
            if not answer:
                return "Введите порядок возврата (например: 'единовременно', 'по частям'):"
            self.data['repayment_method'] = answer
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
                return "Введите город составления договора:"
            self.data['city'] = answer
            self.state = Step.ASK_PURPOSE
            return self.get_next_question()
        
        # Опциональные шаги
        if self.state == Step.ASK_PURPOSE:
            if not self.is_skip(answer):
                self.data['purpose'] = answer
            self.state = Step.ASK_PENALTY
            return self.get_next_question()
        
        if self.state == Step.ASK_PENALTY:
            if not self.is_skip(answer):
                self.data['penalty'] = answer
            self.state = Step.ASK_COLLATERAL
            return self.get_next_question()
        
        if self.state == Step.ASK_COLLATERAL:
            if not self.is_skip(answer):
                self.data['collateral'] = answer
            self.ready_to_generate = True
            self.state = Step.DONE
            return None
        
        return None
    
    def generate_document(self, template_path: str) -> str:
        if not self.ready_to_generate:
            raise ValueError("Невозможно сгенерировать документ: данные не собраны.")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        context = self.data.copy()
        context['has_interest_rate'] = 'interest_rate' in context
        context['has_repayment_method'] = 'repayment_method' in context
        context['has_purpose'] = 'purpose' in context
        context['has_penalty'] = 'penalty' in context
        context['has_collateral'] = 'collateral' in context
        context.setdefault('days', '3')
        context.setdefault('notice_days', '30')
        
        import re
        def replace_conditional(match):
            field = match.group(1)
            if context.get(field, False):
                return match.group(2)
            else:
                return ''
        
        pattern = r'{{#if (has_\w+)}}(.*?){{/if}}'
        document = re.sub(pattern, replace_conditional, template, flags=re.DOTALL)
        
        # Replace [field] placeholders with data values
        for key, value in context.items():
            document = document.replace(f'[{key}]', str(value))
        
        return document
    
    def is_complete(self) -> bool:
        return self.ready_to_generate
    
    def get_current_step(self) -> str:
        return self.state.value