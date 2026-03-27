from enum import Enum


class FieldType(str, Enum):
    TEXT = "text"
    FIO = "fio"
    DATE = "date"
    MONEY = "money"
    PASSPORT = "passport"
    OPTIONAL_TEXT = "optional_text"
