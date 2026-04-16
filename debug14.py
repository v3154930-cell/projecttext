from fastapi.testclient import TestClient
from main import app, sessions, _make_key
import uuid
import json

client = TestClient(app)

# Use unique session ID to avoid any caching
session_id = f"test_isolated_{uuid.uuid4()}"
print(f"Session ID: {session_id}")

# Start fresh
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)
print(f"After start: {r.json().get('current_step')}")

# Fill all steps in order, checking state at each point
answers = [
    ("Иванов Иван Иванович", "ask_passport_series"),
    ("4510", "ask_passport_number"),
    ("123456", "ask_passport_issued_by"),
    ("УВД г. Москвы", "ask_passport_date"),
    ("01.01.2020", "ask_passport_code"),
    ("", "ask_sender_fio"),  # skip passport_code
]

for ans, expected_next in answers:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    data = r.json()
    actual_step = data.get("current_step")
    print(f"Answer '{ans}' (len={len(ans)}): -> {actual_step} (expected: {expected_next})")
    
    # Check scenario data
    key = _make_key(session_id, "receipt_simple")
    s = sessions.get(key)
    print(f"  data keys: {list(s.data.keys())}")
    print(f"  passport_code in data: {'passport_code' in s.data}")
    if "passport_code" in s.data:
        print(f"  passport_code value: '{s.data['passport_code']}'")
    print()