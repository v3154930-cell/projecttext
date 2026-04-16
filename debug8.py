from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
session_id = "test_debug_amount"

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

# Now try different amounts
test_amounts = ["100000", "50000", "10000", "abc", "0", "-100"]
for amt in test_amounts:
    # Use new session each time
    session_id = f"test_amount_{amt}"
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
    session_id = r.json().get("session_id", session_id)
    
    for ans in answers:
        r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": amt})
    data = r.json()
    print(f"Amount='{amt}': step={data.get('current_step')}, err={data.get('error', '')}, question={data.get('question', '')[:40] if data.get('question') else 'None'}")