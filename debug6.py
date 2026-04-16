from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
session_id = "debug_api_004"

# Start
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

answers = [
    "Иванов Иван Иванович",
    "4510",
    "123456",
    "УВД г. Москвы",
    "01.01.2020",
    "",
    "Петров Петр Петрович",
    "100000",
    "30.03.2026",
    "30.09.2026",
    "Москва",
]

for i, ans in enumerate(answers):
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    data = r.json()
    print(f"{i+1}. answer='{ans}' -> step={data.get('current_step')}, complete={data.get('is_complete')}")

# Now check what's returned after "Москва"
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
data = r.json()
print(f"\nEmpty answer after city: step={data.get('current_step')}, question={data.get('question', '')[:50] if data.get('question') else 'None'}")
print(f"is_complete: {data.get('is_complete')}")

# Try with preview answer
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "1"})
data = r.json()
print(f"\nWith '1' answer: step={data.get('current_step')}, complete={data.get('is_complete')}")
print(f"document: {str(data.get('document', ''))[:100] if data.get('document') else 'None'}")