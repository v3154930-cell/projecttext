from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
session_id = "test_detail"

# Start fresh
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

# Fill up to amount
answers = [
    "Иванов Иван Иванович",
    "4510",
    "123456",
    "УВД г. Москвы",
    "01.01.2020",
    "",
    "Петров Петр Петрович",
]

for ans in answers:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})

# Now check the response in detail
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "100000"})
data = r.json()

print("=== Response for amount=100000 ===")
print(f"question: '{data.get('question')}'")
print(f"current_step: '{data.get('current_step')}'")
print(f"is_complete: {data.get('is_complete')}")
print(f"error: '{data.get('error')}'")
print(f"collected_data: {data.get('collected_data', {})}")
print()

# Now let's check what the actual scenario contains
from main import sessions, _make_key
key = _make_key(session_id, "receipt_simple")
if key in sessions:
    s = sessions[key]
    print(f"=== Scenario state ===")
    print(f"_current_index: {s._current_index}")
    print(f"data: {s.data}")
    print(f"is_complete: {s.is_complete()}")