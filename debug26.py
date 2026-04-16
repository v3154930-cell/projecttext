from fastapi.testclient import TestClient
from main import app, sessions, _make_key

client = TestClient(app)

# Test case 2: test_receipt_simple_collects_data
session_id = "test_collect_001"

# Start - get the actual session_id returned
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)  # Update session_id from response
print(f"Session ID: {session_id}")

answers = [
    "Иванов Иван Иванович",
    "4510",
    "123456",
    "УВД г. Москвы",
    "01.01.2020",
    "",
    "Петров Петр Петрович",
    "50000",
    "01.04.2026",
    "01.10.2026",
    "Сочи",
    "1",  # preview confirm
]

for i, answer in enumerate(answers):
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": answer})
    data = r.json()
    print(f"Step {i+1}: ans='{answer[:20] if answer else 'empty'}...' -> step={data.get('current_step')}, complete={data.get('is_complete')}")

# Final check
print(f"\nFinal: {r.json().get('current_step')}, complete={r.json().get('is_complete')}")