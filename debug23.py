from fastapi.testclient import TestClient
from main import app, sessions, _make_key

client = TestClient(app)

# Start
session_id = "test_check_001"
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)
key = _make_key(session_id, "receipt_simple")

# Fill
for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})

print(f"Before empty answer:")
s = sessions[key]
print(f"  _current_index: {s._current_index}")
print(f"  step name: {s._steps[s._current_index].name}")
print(f"  step optional: {s._steps[s._current_index].optional}")

# Check the actual API call in detail
print("\n--- Let's add some print inside main.py temporarily ---")
# Instead let's trace using a different approach

# Use raise_server_exceptions to see any errors
r = client.post(
    "/api/scenario/receipt_simple", 
    json={"session_id": session_id, "answer": ""},
    raise_server_exceptions=True
)
print(f"Status: {r.status_code}")
print(f"Response: {r.json()}")