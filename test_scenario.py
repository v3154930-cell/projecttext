from scenarios.receipt_simple import ReceiptSimpleScenario

s = ReceiptSimpleScenario()
print(f"Before: {s.get_current_step()}")
s.process_answer("")
print(f"After: {s.get_current_step()}")
print(f"Next question: {s.get_next_question()}")
