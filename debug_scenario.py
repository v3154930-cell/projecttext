from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
session_id = "debug_001"

answers = ["Иванов Иван Иванович"]
for i in range(25):
    response = client.post(
        "/api/scenario/receipt_simple", 
        json={"session_id": session_id, "answer": answers[-1]}
    )
    data = response.json()
    step = data.get("current_step", "?")
    q = data.get("question", "")[:80] if data.get("question") else ""
    complete = data.get("is_complete", False)
    print(f"Step {i+1}: {step} | complete={complete} | q={q}")
    if complete:
        doc = data.get("document", "")
        print(f"DOC preview: {doc[:300]}...")
        break
    if step == "done":
        print("Done!")
        break