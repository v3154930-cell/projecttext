from fastapi.testclient import TestClient
from main import app, sessions, _make_key
import json

# Let's add some debug to the API endpoint directly
# by patching it

client = TestClient(app)

# Start with a unique session
session_id = "test_trace_api_001"

# Start
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)
key = _make_key(session_id, "receipt_simple")

# Fill
for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})

print(f"Before empty answer:")
s = sessions[key]
print(f"  scenario._current_index: {s._current_index}")
print(f"  step: {s._steps[s._current_index].name}")

# Now let's trace what happens in handle_scenario
# Add some manual tracing by checking what's passed to process_answer
print(f"\n--- Now let's trace the actual process_answer call ---")

# Import and wrap
from scenarios.receipt_simple import ReceiptSimpleScenario
original_method = ReceiptSimpleScenario.process_answer

def traced_process(self, answer):
    print(f"  -> process_answer called with answer='{answer}' (len={len(answer)})")
    print(f"  -> current _current_index before: {self._current_index}")
    result = original_method(self, answer)
    print(f"  -> current _current_index after: {self._current_index}")
    return result

ReceiptSimpleScenario.process_answer = traced_process

# Reset with new session
session_id = "test_trace_002"
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

# Fill
for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})

# Now send empty
print(f"\n--- Sending empty answer to skip optional ---")
key = _make_key(session_id, "receipt_simple")
s = sessions[key]
print(f"Before: scenario._current_index={s._current_index}, step={s._steps[s._current_index].name}")

r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
data = r.json()
print(f"After: response current_step={data.get('current_step')}")