from fastapi.testclient import TestClient
from main import app, sessions, _make_key
import json

client = TestClient(app)
session_id = "test_claim_trace"

# Start
r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

# After start
key = _make_key(session_id, "claim_marketplace_buyer")
s = sessions[key]
print(f"After start: data={json.dumps(s.data, ensure_ascii=False)}")
print(f"  current_step: {s.get_current_step()}")

# Answer 1: recipient_type
r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": "1"})
s = sessions[key]
print(f"\nAfter '1' (recipient_type): data={json.dumps(s.data, ensure_ascii=False)}")
print(f"  current_step: {s.get_current_step()}")

# Answer 1: platform
r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": "1"})
s = sessions[key]
print(f"\nAfter '1' (platform): data={json.dumps(s.data, ensure_ascii=False)}")
print(f"  current_step: {s.get_current_step()}")

# Answer: order_number
r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": "123456789"})
data = r.json()
s = sessions[key]
print(f"\nAfter order number: current_step={s.get_current_step()}")
print(f"  Response step: {data.get('current_step')}")