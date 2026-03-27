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

    def process_answer(self, answer: str) -> Optional[str]:
        if self._ready_to_generate:
            return None

        answer = answer.strip()

        if self._current_index >= len(self._steps):
            return None

        step = self._steps[self._current_index]

        for validator in step.validators:
            error: Optional[str] = validator(answer)
            if error:
                return error

        if step.data_key:
            value = step.post_process(answer) if step.post_process else answer
            self.data[step.data_key] = value

        self._current_index += 1

        if self._current_index >= len(self._steps):
            self._ready_to_generate = True
            return None

        return self._steps[self._current_index].question

    def generate_document(self, template_path: Optional[str] = None) -> str:
        if not self._ready_to_generate:
            raise ValueError("Невозможно сгенерировать документ: данные не собраны.")

        path = template_path or self._template_path
        with open(path, 'r', encoding='utf-8') as f:
            template = f.read()

        document = template.format(**self.data)
        return document
