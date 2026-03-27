import sys
print("Python:", sys.version)
print("---")
from scenarios.receipt_simple import ReceiptSimpleScenario
s = ReceiptSimpleScenario()
print("Step:", s.get_current_step())
s.process_answer("")
print("After init:", s.get_current_step())
print("Q:", s.get_next_question())

# Simulate full flow
answers = [
    "Ivanov Ivan Ivanovich",
    "4510 123456, UVD g. Moskvy, 01.01.2020",
    "Petrov Petr Petrovich",
    "100000",
    "25.12.2026",
    "01.01.2025",
    "Moskva",
]
for a in answers:
    result = s.process_answer(a)
    print(f"Answer: {a[:30]} -> Step: {s.get_current_step()}, Result: {str(result)[:50] if result else 'None'}")

print("---")
print("Complete:", s.is_complete())
print("Data:", s.data)
