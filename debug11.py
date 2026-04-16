from fastapi.testclient import TestClient
from main import app, sessions, _make_key

client = TestClient(app)
session_id = "test_trace2"

# Start fresh
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

# Trace step by step from passport_code onwards
answers = [
    "4510",
    "123456",
    "УВД г. Москвы",
    "01.01.2020",
    "",  # skip passport_code
    "Петров Петр Петрович",  # ask_sender_fio
]

for i, ans in enumerate(answers):
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    data = r.json()
    
    # Get scenario state
    key = _make_key(session_id, "receipt_simple")
    s = sessions.get(key)
    
    print(f"Answer: '{ans}'")
    print(f"  -> returned step: {data.get('current_step')}")
    print(f"  -> returned question: {data.get('question', '')[:50] if data.get('question') else 'None'}")
    print(f"  -> returned error: {data.get('error')}")
    print(f"  -> scenario._current_index: {s._current_index if s else 'N/A'}")
    print(f"  -> scenario._steps[s._current_index].name: {s._steps[s._current_index].name if s and s._current_index < len(s._steps) else 'N/A'}")
    print(f"  -> scenario.data keys: {list(s.data.keys()) if s else 'N/A'}")
    print()