import re
from typing import Optional, Callable
from framework.step import FieldStep


class BaseScenario:
    START_STEP = "start"

    def __init__(self, steps: list[FieldStep], template_path: str):
        self._steps = steps
        self._template_path = template_path
        self._preview_enabled = False
        self._field_assemblers = {}
        self.reset()

    def reset(self):
        self._current_index = 0
        self.data = {}
        self._ready_to_generate = False
        self._in_preview = False
        self._preview_document = ""
        self._in_edit_mode = False
        self._return_to_preview = False
        self._skip_edit_return = False

    def get_current_step(self) -> str:
        if self._current_index < len(self._steps):
            return self._steps[self._current_index].name
        return "done"

    def is_complete(self) -> bool:
        if self._preview_enabled and self._in_preview:
            return False
        return self._ready_to_generate

    def get_next_question(self) -> Optional[str]:
        if self._preview_enabled and self._in_preview:
            return "Проверьте правильность заполнения:\n\n" + self._preview_document + "\n\nВыберите действие:\n1. Подтвердить\n2. Редактировать"
        if self._in_edit_mode:
            lines = ["Выберите поле для редактирования:\n"]
            for label, value, idx in self._editable_fields():
                val_short = (value[:40] + "...") if value and len(value) > 40 else (value or "")
                lines.append(f"  {len(lines)}. {label}: {val_short}")
            return "\n".join(lines)
        if self._current_index < len(self._steps):
            return self._steps[self._current_index].question
        return None

    def is_current_optional(self) -> bool:
        if self._preview_enabled and self._in_preview:
            return False
        if self._current_index < len(self._steps):
            return self._steps[self._current_index].optional
        return False

    def get_current_field_type(self) -> Optional[str]:
        if self._preview_enabled and self._in_preview:
            return "preview"
        if self._in_edit_mode:
            return "edit_select"
        if self._current_index < len(self._steps):
            return self._steps[self._current_index].field_type.value
        return None

    @staticmethod
    def _is_skip(answer: str) -> bool:
        return answer.strip().lower() in ["пропустить", "skip", ""]

    def _should_show_step(self, step: FieldStep) -> bool:
        if step.depends_on is None:
            return True
        return step.depends_on in self.data

    def _advance_to_next_step(self) -> Optional[str]:
        self._current_index += 1
        while self._current_index < len(self._steps):
            if self._should_show_step(self._steps[self._current_index]):
                return self._steps[self._current_index].question
            self._current_index += 1
        self._ready_to_generate = True
        return None

    def _try_enter_preview(self) -> Optional[str]:
        """If preview enabled and ready, enter preview. Returns None on success or error string."""
        if not (self._preview_enabled and self._ready_to_generate):
            return None
        try:
            self._preview_document = self.generate_document()
            self._in_preview = True
            return self.get_next_question()
        except Exception:
            self._ready_to_generate = False
            return "Ошибка генерации документа. Пожалуйста, проверьте введенные данные."

    def _run_assemblers(self):
        for key, fn in self._field_assemblers.items():
            self.data[key] = fn(self.data)

    def _editable_fields(self):
        """Returns list of (label, value, step_index) for fields with data."""
        LABELS = {
            "fio": "ФИО", "fio_receiver": "ФИО получателя", "fio_sender": "ФИО передающего",
            "fio_lender": "ФИО займодавца", "lender": "Займодавец", "borrower": "Заемщик",
            "fio_borrower": "ФИО заемщика", "passport_series": "Паспорт (серия)",
            "passport_number": "Паспорт (номер)", "passport_issued_by": "Паспорт (кем выдан)",
            "passport_date": "Паспорт (дата выдачи)", "passport_code": "Паспорт (код подразделения)",
            "amount": "Сумма", "date": "Дата", "return_date": "Срок возврата", "city": "Город",
            "term": "Срок возврата", "interest_rate": "Процентная ставка",
            "interest_period": "Период процентов", "penalty": "Штраф/пени",
            "repayment_order": "Порядок возврата", "repayment_method": "Порядок возврата",
            "purpose": "Цель займа", "collateral": "Обеспечение",
        }
        result = []
        for i, step in enumerate(self._steps):
            if step.data_key and step.data_key in self.data and step.name != "start":
                label = LABELS.get(step.data_key, step.data_key)
                value = self.data.get(step.data_key, "")
                result.append((label, value, i))
        return result

    def _return_to_preview_now(self):
        """Regenerate preview document and enter preview mode."""
        self._ready_to_generate = True
        self._run_assemblers()
        try:
            self._preview_document = self.generate_document()
            self._in_preview = True
        except Exception:
            pass

    def process_answer(self, answer: str) -> Optional[str]:
        # Edit mode: handle field selection from preview "Редактировать"
        if self._in_edit_mode:
            answer = answer.strip()
            if self._is_skip(answer) or answer in ["назад", "back"]:
                self._in_edit_mode = False
                self._return_to_preview = False
                self._return_to_preview_now()
                return self.get_next_question()
            try:
                idx = int(answer) - 1
            except ValueError:
                return "Введите номер поля:"
            fields = self._editable_fields()
            if idx < 0 or idx >= len(fields):
                return f"Введите число от 1 до {len(fields)}:"
            _, _, step_idx = fields[idx]
            self._current_index = step_idx
            self._in_edit_mode = False
            self._return_to_preview = True
            self._skip_edit_return = False
            return self.get_next_question()

        # Return to preview after edit: user either edited or skipped optional field
        if self._return_to_preview:
            if self._skip_edit_return:
                if self._is_skip(answer):
                    self._skip_edit_return = False
                    self._return_to_preview = False
                    self._return_to_preview_now()
                    return self.get_next_question()
                else:
                    self._skip_edit_return = False

            answer = answer.strip()
            step = self._steps[self._current_index]

            if step.optional and self._is_skip(answer):
                self._return_to_preview = False
                self._return_to_preview_now()
                return self.get_next_question()

            for validator in step.validators:
                error: Optional[str] = validator(answer)
                if error:
                    return error

            if step.data_key:
                value = step.post_process(answer) if step.post_process else answer
                self.data[step.data_key] = value

            for cv in step.cross_validators:
                error = cv(self.data[step.data_key] if step.data_key else answer, self.data)
                if error:
                    return error

            self._return_to_preview = False
            self._return_to_preview_now()
            return self.get_next_question()

        # Preview: handle confirm / edit
        if self._preview_enabled and self._in_preview:
            answer = answer.strip().lower()
            if answer in ["1", "подтвердить", "confirm"]:
                self._in_preview = False
                return None
            elif answer in ["2", "редактировать", "edit"]:
                self._in_preview = False
                self._in_edit_mode = True
                self._return_to_preview = True
                return self.get_next_question()
            else:
                return "Пожалуйста, выберите: 1 - Подтвердить, 2 - Редактировать"

        if self._ready_to_generate:
            return self._try_enter_preview() if self._preview_enabled else None

        answer = answer.strip()

        if self._current_index >= len(self._steps):
            return None

        step = self._steps[self._current_index]

        if step.optional and self._is_skip(answer):
            result = self._advance_to_next_step()
            self._run_assemblers()
            preview_result = self._try_enter_preview()
            return preview_result if preview_result is not None else result

        for validator in step.validators:
            error: Optional[str] = validator(answer)
            if error:
                return error

        if step.data_key:
            value = step.post_process(answer) if step.post_process else answer
            self.data[step.data_key] = value

        for cv in step.cross_validators:
            error = cv(self.data[step.data_key] if step.data_key else answer, self.data)
            if error:
                return error

        result = self._advance_to_next_step()
        self._run_assemblers()
        preview_result = self._try_enter_preview()
        return preview_result if preview_result is not None else result

    def generate_document(self, template_path: Optional[str] = None) -> str:
        if not self._ready_to_generate:
            raise ValueError("Невозможно сгенерировать документ: данные не собраны.")

        path = template_path or self._template_path
        with open(path, 'r', encoding='utf-8') as f:
            template = f.read()

        context = {f"has_{k}": True for k in self.data}

        def _replace_conditional(match: re.Match) -> str:
            field = match.group(1)
            if context.get(field, False):
                return '\n' + match.group(2) + '\n'
            return ''

        pattern = r'\n?{{#if (has_\w+)}}(.*?){{/if}}\n?'
        document = re.sub(pattern, _replace_conditional, template, flags=re.DOTALL)

        document = re.sub(r'\n{3,}', '\n\n', document)

        try:
            document = document.format(**self.data)
        except KeyError as e:
            raise ValueError(f"Отсутствует необходимое поле для шаблона: {e}")

        return document
