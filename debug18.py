# Let's check what the step definition looks like for passport_code
from scenarios.receipt_simple import ReceiptSimpleScenario, PASSPORT_STEPS

s = ReceiptSimpleScenario()

# Find passport_code step
for i, step in enumerate(s._steps):
    if step.name == "ask_passport_code":
        print(f"Step {i}: {step.name}")
        print(f"  optional: {step.optional}")
        print(f"  data_key: {step.data_key}")
        print(f"  depends_on: {step.depends_on}")
        print(f"  validators: {step.validators}")
        break