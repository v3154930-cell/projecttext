from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
session_id = "test_claim_debug"

# Start
r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)
print(f"Start: {r.json().get('current_step')}")

# Try first test case: test_claim_not_suitable
answers = [
    "1",   # recipient_type = marketplace
    "1",   # platform = Ozon
    "123456789",
    "Смартфон Xiaomi",
    "25000",
    "Иванов Иван Иванович",
    "4510",
    "123456",
    "УВД г. Москвы",
    "01.01.2020",
    "",
    "16.04.2026",
    "",
    "",
    "1",   # claim_reason = not_suitable
    "1",   # preview confirm
]

for i, ans in enumerate(answers):
    r = client.post("/api/scenario/claim_marketplace_buyer", json={"session_id": session_id, "answer": ans})
    data = r.json()
    print(f"Step {i+1}: ans='{ans}' -> step={data.get('current_step')}, complete={data.get('is_complete')}")
    if data.get('error'):
        print(f"  ERROR: {data.get('error')}")

# Final
data = r.json()
print(f"\nFinal: step={data.get('current_step')}, complete={data.get('is_complete')}")