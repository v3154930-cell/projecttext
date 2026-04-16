from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Simulate the full test flow like test_receipt_simple_happy_path
session_id = "debug_test_001"

# Start
r1 = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
print(f"Step 0 (start): {r1.json().get('current_step')}")
session_id = r1.json().get("session_id", session_id)

answers = [
    "Иванов Иван Иванович",  # ask_receiver_fio
    "4510",  # ask_passport_series
    "123456",  # ask_passport_number
    "УВД г. Москвы",  # ask_passport_issued_by
    "01.01.2020",  # ask_passport_date
    "",  # passport_code skip
    "Петров Петр Петрович",  # ask_sender_fio
    "100000",  # ask_amount
    "30.03.2026",  # ask_date
    "30.09.2026",  # ask_return_date
    "Москва",  # ask_city
    "1",  # preview confirm
]

for i, ans in enumerate(answers):
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    data = r.json()
    step = data.get("current_step", "?")
    complete = data.get("is_complete", False)
    doc = data.get("document", "")
    err = data.get("error", "")
    print(f"Step {i+1}: answer='{ans[:30]}...' -> step={step}, complete={complete}, has_doc={bool(doc)}, err={err[:50] if err else ''}")
    if complete:
        print(f"  Document: {doc[:200]}...")
        break