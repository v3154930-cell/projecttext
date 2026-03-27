import re
from typing import Optional, Callable
from framework.step import FieldStep


class BaseScenario:
    START_STEP = "start"

    def __init__(self, steps: list[FieldStep], template_path: str):
        self._steps = steps
        self._template_path = template_path
        self.reset()

    def reset(self):
        self._current_index = 0
        self.data = {}
        self._ready_to_generate = False

    def get_current_step(self) -> str:
        if self._current_index < len(self._steps):
            return self._steps[self._current_index].name
        return "done"

    def is_complete(self) -> bool:
        return self._ready_to_generate

    def get_next_question(self) -> Optional[str]:
        if self._current_index < len(self._steps):
            return self._steps[self._current_index].question
        return None

    def is_current_optional(self) -> bool:
        if self._current_index < len(self._steps):
            return self._steps[self._current_index].optional
        return False

    def get_current_field_type(self) -> Optional[str]:
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

    def process_answer(self, answer: str) -> Optional[str]:
        if self._ready_to_generate:
            return None

        answer = answer.strip()

        if self._current_index >= len(self._steps):
            return None

        step = self._steps[self._current_index]

        if step.optional and self._is_skip(answer):
            return self._advance_to_next_step()

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

        return self._advance_to_next_step()

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
