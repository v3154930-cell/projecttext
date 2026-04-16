from fastapi.testclient import TestClient
from main import app, sessions, _make_key

client = TestClient(app)
session_id = "test_trace"

# Start fresh
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

# Trace each step carefully
answers = [
    "Иванов Иван Иванович",  # 1
    "4510",  # 2
    "123456",  # 3
    "УВД г. Москвы",  # 4
    "01.01.2020",  # 5
    "",  # 6 - skip passport_code
    "Петров Петр Петрович",  # 7
    "100000",  # 8
]

for i, ans in enumerate(answers):
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    data = r.json()
    
    # Get scenario state
    key = _make_key(session_id, "receipt_simple")
    s = sessions.get(key)
    
    print(f"Step {i+1}. Answer: '{ans}'")
    print(f"  -> returned step: {data.get('current_step')}")
    print(f"  -> scenario._current_index: {s._current_index if s else 'N/A'}")
    print(f"  -> scenario.data.get('fio_sender'): {s.data.get('fio_sender') if s else 'N/A'}")
    print()