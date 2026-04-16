from scenarios.receipt_simple import ReceiptSimpleScenario

s = ReceiptSimpleScenario()

# Initialize
s.process_answer("")

# Fill up to passport_code
for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    s.process_answer(ans)

print(f"Before empty answer:")
print(f"  _current_index: {s._current_index}")
print(f"  current step: {s._steps[s._current_index].name}")
print(f"  step.optional: {s._steps[s._current_index].optional}")

# Check _is_skip
print(f"\n_is_skip(''): {s._is_skip('')}")

# Now process empty answer with debug
step = s._steps[s._current_index]
print(f"step.optional: {step.optional}")
print(f"_is_skip(''): {s._is_skip('')}")
print(f"Condition result: {step.optional and s._is_skip('')}")

# Now actually call it
result = s.process_answer("")
print(f"\nAfter process_answer(''):")
print(f"  _current_index: {s._current_index}")
print(f"  current step: {s._steps[s._current_index].name if s._current_index < len(s._steps) else 'done'}")
print(f"  result: {str(result)[:50] if result else 'None'}")