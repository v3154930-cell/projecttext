from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
session_id = "test_loan_debug"

# Start
r = client.post("/api/scenario/loan", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)
print(f"Start: {r.json().get('current_step')}")

answers = [
    "Иванов Иван Иванович",
    "4510",
    "111111",
    "УВД г. Москвы",
    "01.01.2020",
    "",
    "Петров Петр Петрович",
    "4511",
    "222222",
    "ОВД г. Сочи",
    "15.06.2021",
    "",
    "50000",
    "01.01.2026",
    "01.01.2027",
    "Москва",
]

for i, ans in enumerate(answers):
    r = client.post("/api/scenario/loan", json={"session_id": session_id, "answer": ans})
    data = r.json()
    print(f"Step {i+1}: ans='{ans[:15]}...' -> step={data.get('current_step')}, complete={data.get('is_complete')}")

# Now send preview confirm
r = client.post("/api/scenario/loan", json={"session_id": session_id, "answer": "1"})
data = r.json()
print(f"After '1': step={data.get('current_step')}, complete={data.get('is_complete')}")