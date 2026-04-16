from fastapi.testclient import TestClient
from main import app, sessions, _make_key

client = TestClient(app)

# Test case 2: test_receipt_simple_collects_data
session_id = "test_collect_001"

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
]

for i, answer in enumerate(answers):
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": answer})
    data = r.json()
    print(f"Step {i+1}: ans='{answer[:20]}...' -> step={data.get('current_step')}, complete={data.get('is_complete')}")

# After all answers
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
data = r.json()
print(f"\nAfter all answers: step={data.get('current_step')}, complete={data.get('is_complete')}")

# Try with "1" to confirm preview
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "1"})
data = r.json()
print(f"After '1': step={data.get('current_step')}, complete={data.get('is_complete')}")