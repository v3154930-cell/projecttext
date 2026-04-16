from fastapi.testclient import TestClient
from main import app, sessions, _make_key

# Monkey-patch to add debugging
original_process_answer = None

def patched_process_answer(self, answer):
    print(f"  [DEBUG] process_answer called with: '{answer}'")
    print(f"  [DEBUG] current _current_index: {self._current_index}")
    if self._current_index < len(self._steps):
        print(f"  [DEBUG] current step name: {self._steps[self._current_index].name}")
        print(f"  [DEBUG] current step data_key: {self._steps[self._current_index].data_key}")
    result = original_process_answer(self, answer)
    print(f"  [DEBUG] after process_answer, _current_index: {self._current_index}")
    return result

# Apply patch
from scenarios import receipt_simple
original_process_answer = receipt_simple.ReceiptSimpleScenario.process_answer
receipt_simple.ReceiptSimpleScenario.process_answer = patched_process_answer

# Now run test
client = TestClient(app)
session_id = "test_patch"

r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

# Send one answer and see the debug output
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": "Иванов Иван Иванович"})
data = r.json()
print(f"\nAfter 'Иванов Иван Иванович':")
print(f"  current_step: {data.get('current_step')}")
print(f"  question: {data.get('question', '')[:50] if data.get('question') else 'None'}")