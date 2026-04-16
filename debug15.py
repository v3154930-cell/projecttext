from fastapi.testclient import TestClient
from main import app, sessions, _make_key
import uuid
import json

# Monkey-patch to debug
original_advance = None

def patched_advance(self):
    print(f"  [_advance] Before: _current_index={self._current_index}")
    result = original_advance(self)
    print(f"  [_advance] After: _current_index={self._current_index}, result={str(result)[:50] if result else 'None'}")
    return result

from framework.base_scenario import BaseScenario
original_advance = BaseScenario._advance_to_next_step
BaseScenario._advance_to_next_step = patched_advance

# Now run test
client = TestClient(app)
session_id = f"test_patch_advance_{uuid.uuid4()}"

r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

# Fill up to passport_code
for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})

print("\n--- Now sending empty answer to skip passport_code ---")
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
data = r.json()
print(f"\nAPI response: step={data.get('current_step')}, question={data.get('question', '')[:50] if data.get('question') else 'None'}")