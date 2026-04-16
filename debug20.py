from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)
session_id = "test_ws"

# Fill up to passport_code
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})

# Get current state
key = f"{session_id}:receipt_simple"
from main import sessions
s = sessions[key]
print(f"Current step: {s._steps[s._current_index].name}")
print(f"Step is optional: {s._steps[s._current_index].optional}")

# Now send with explicit empty string
print("\n--- Test 1: send empty string ---")
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
print(f"response step: {r.json().get('current_step')}")
print(f"response optional: {r.json().get('optional')}")

# Check scenario state
s = sessions[key]
print(f"scenario step: {s._steps[s._current_index].name}")

# Now send again
print("\n--- Test 2: send empty string again ---")
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
print(f"response step: {r.json().get('current_step')}")

s = sessions[key]
print(f"scenario step: {s._steps[s._current_index].name}")
print(f"scenario data keys: {list(s.data.keys())}")