from fastapi.testclient import TestClient
from main import app, sessions, _make_key
import json

client = TestClient(app)
session_id = "test_debug_sender"

# Start fresh
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

# Fill up to ask_sender_fio
answers = [
    "Иванов Иван Иванович",
    "4510",
    "123456",
    "УВД г. Москвы",
    "01.01.2020",
    "",
]

for ans in answers:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})

# Now check state
key = _make_key(session_id, "receipt_simple")
s = sessions.get(key)
print(f"Before ask_sender_fio answer:")
print(f"  _current_index: {s._current_index}")
print(f"  step name: {s._steps[s._current_index].name}")
print(f"  step data_key: {s._steps[s._current_index].data_key}")
print(f"  data: {json.dumps(s.data, ensure_ascii=False, indent=2)}")
print()

# Send answer for ask_sender_fio
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "Петров Петр Петрович"})
data = r.json()

print(f"After ask_sender_fio answer:")
print(f"  returned current_step: {data.get('current_step')}")
print(f"  returned question: {data.get('question', '')[:50] if data.get('question') else 'None'}")
print()

# Check scenario state after API call
s = sessions.get(key)
print(f"Scenario state after API call:")
print(f"  _current_index: {s._current_index}")
print(f"  step name: {s._steps[s._current_index].name}")
print(f"  data: {json.dumps(s.data, ensure_ascii=False, indent=2)}")