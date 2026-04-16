from fastapi.testclient import TestClient
from main import app, sessions
import json

client = TestClient(app)

# Use new session each time
session_id = "test_new_session_001"

# Start
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)
print(f"After start: {r.json().get('current_step')}")

# Now let's check what session key is used
from main import _make_key
key = _make_key(session_id, "receipt_simple")
print(f"Session key: {key}")
print(f"Sessions in memory: {list(sessions.keys())}")

# Fill up to passport_code
for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    data = r.json()
    print(f"  After '{ans[:15]}...': step={data.get('current_step')}")

# Check session
print(f"\nSessions after fill: {list(sessions.keys())}")

# Now send empty - debug what happens inside
print("\n--- Sending empty answer ---")
print(f"Current session key: {key}")
s = sessions.get(key)
print(f"Scenario object exists: {s is not None}")
print(f"  _current_index: {s._current_index}")
print(f"  step name: {s._steps[s._current_index].name}")

r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
data = r.json()
print(f"\nAfter empty answer:")
print(f"  Response step: {data.get('current_step')}")
print(f"  Sessions: {list(sessions.keys())}")

s = sessions.get(key)
print(f"  Scenario _current_index: {s._current_index}")
print(f"  Scenario step name: {s._steps[s._current_index].name}")