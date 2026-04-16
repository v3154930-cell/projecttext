from scenarios.receipt_simple import ReceiptSimpleScenario
import uuid

s = ReceiptSimpleScenario()
session_id = str(uuid.uuid4())
print(f"Session: {session_id}")

answers = [
    "",  # start
    "Иванов Иван Иванович",
    "4510",
    "123456",
    "УВД г. Москвы",
    "01.01.2020",
    "",
    "Петров Петр Петрович",
    "100000",
    "30.03.2026",
    "30.09.2026",
    "Москва",
    "1",  # preview confirm
]

for i, ans in enumerate(answers):
    result = s.process_answer(ans)
    print(f"{i+1}. answer='{ans}' -> step={s.get_current_step()}, complete={s.is_complete()}")

print("\n--- Final ---")
print(f"is_complete: {s.is_complete()}")
print(f"current_step: {s.get_current_step()}")
print(f"data keys: {list(s.data.keys())}")

if s.is_complete():
    doc = s.generate_document()
    print(f"\nDocument preview: {doc[:300]}...")