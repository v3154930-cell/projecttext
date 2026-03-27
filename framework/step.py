from dataclasses import dataclass, field
from typing import Optional, Callable
from framework.fields import FieldType


@dataclass
class FieldStep:
    name: str
    question: str
    data_key: str = ""
    field_type: FieldType = FieldType.TEXT
    validators: list[Callable[[str], Optional[str]]] = field(default_factory=list)
    post_process: Optional[Callable[[str], str]] = None
