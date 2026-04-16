from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
session_id = "debug_003"

# Start
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
print(f"Start: {r.json().get('current_step')}")
session_id = r.json().get("session_id", session_id)

# Step by step with more detail
answers = [
    "Иванов Иван Иванович",
    "4510",
    "123456",
    "УВД г. Москвы",
    "01.01.2020",
    "",
    "Петров Петр Петрович",
    "100000",
]

for i, ans in enumerate(answers):
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    data = r.json()
    print(f"{i+1}. answer='{ans}'")
    print(f"   -> current_step={data.get('current_step')}")
    print(f"   -> question={data.get('question', '')[:60] if data.get('question') else 'None'}")
    print(f"   -> error={data.get('error', '')}")
    print()