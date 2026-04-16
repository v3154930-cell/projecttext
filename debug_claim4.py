from fastapi.testclient import TestClient
from main import app, sessions, _make_key
import json

client = TestClient(app)
session_id = "test_claim_trace2"

# Start
r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)
key = _make_key(session_id, "claim_marketplace_buyer")

# After start
s = sessions[key]
print(f"After start: step={s.get_current_step()}")

# Answer 1: recipient_type
r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": "1"})
s = sessions[key]
print(f"After '1' (recipient_type): step={s.get_current_step()}")

# Answer 1: platform
r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": "1"})
s = sessions[key]
print(f"After '1' (platform): step={s.get_current_step()}, data={json.dumps(s.data, ensure_ascii=False)}")

# Check what step is at index
print(f"\nSteps from current index:")
for i in range(s._current_index, min(s._current_index+5, len(s._steps))):
    step = s._steps[i]
    print(f"  {i}: {step.name}, depends_on={step.depends_on}")

# Now answer order_number
print(f"\n--- Answering order_number ---")
r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": "123456789"})
data = r.json()
print(f"Response: step={data.get('current_step')}, error={data.get('error')}")

# Check state again
s = sessions[key]
print(f"After order_number: step={s.get_current_step()}")
print(f"data keys: {list(s.data.keys())}")