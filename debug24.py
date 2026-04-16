from fastapi.testclient import TestClient
from main import app, sessions, _make_key

client = TestClient(app)

# Test with the parameterized endpoint directly
session_id = "test_param_endpoint_001"

# Start - use the parameterized endpoint
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
print(f"Start: {r.json().get('current_step')}")
session_id = r.json().get("session_id", session_id)
key = _make_key(session_id, "receipt_simple")

# Fill
for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    print(f"  After '{ans[:15]}...': {r.json().get('current_step')}")

# Now check step before empty answer
s = sessions[key]
print(f"\nBefore empty: _current_index={s._current_index}, step={s._steps[s._current_index].name}")

# Send empty - this should skip
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
data = r.json()
print(f"After empty: step={data.get('current_step')}, question={data.get('question', '')[:30] if data.get('question') else 'None'}")

# Check state again
s = sessions[key]
print(f"After empty in scenario: _current_index={s._current_index}, step={s._steps[s._current_index].name if s._current_index < len(s._steps) else 'done'}")