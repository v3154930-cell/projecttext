from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

# Test 1: With explicit session_id
print("=== Test 1: With explicit session_id ===")
session_id = "test_001"
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)
print(f"After start: session_id={session_id}")

answers = ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020", "", "Петров Петр Петрович"]
for i, ans in enumerate(answers):
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    data = r.json()
    print(f"  {i+1}. ans='{ans}' -> step={data.get('current_step')}, err={data.get('error', '')}")

# Check the actual request being made
print("\n=== Debug: Verify session is stored ===")
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "100000"})
data = r.json()
print(f"  After amount 100000: step={data.get('current_step')}, err={data.get('error', '')}")
print(f"  data: {json.dumps(data, ensure_ascii=False)[:300]}")

r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "30.03.2026"})
data = r.json()
print(f"  After date: step={data.get('current_step')}, err={data.get('error', '')}")

r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "30.09.2026"})
data = r.json()
print(f"  After return_date: step={data.get('current_step')}, err={data.get('error', '')}")

r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "Москва"})
data = r.json()
print(f"  After city: step={data.get('current_step')}, err={data.get('error', '')}, complete={data.get('is_complete')}")

r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "1"})
data = r.json()
print(f"  After preview confirm: step={data.get('current_step')}, complete={data.get('is_complete')}")
if data.get("document"):
    print(f"  Document preview: {data['document'][:100]}")