from fastapi.testclient import TestClient
from main import app, sessions, _make_key
import uuid

# Monkey-patch to debug more deeply
original_process = None
original_advance = None
original_should_show = None

def patched_process(self, answer):
    step = self._steps[self._current_index] if self._current_index < len(self._steps) else None
    step_name = step.name if step else "none"
    step_optional = step.optional if step else False
    step_data_key = step.data_key if step else None
    
    print(f"  [process_answer] START: _current_index={self._current_index}, step={step_name}, optional={step_optional}")
    print(f"  [process_answer] answer='{answer}' (len={len(answer)})")
    
    result = original_process(self, answer)
    
    print(f"  [process_answer] END: _current_index={self._current_index}, result={str(result)[:50] if result else 'None'}")
    return result

def patched_advance(self):
    print(f"    [_advance] Before: _current_index={self._current_index}")
    result = original_advance(self)
    print(f"    [_advance] After: _current_index={self._current_index}, result={str(result)[:30] if result else 'None'}")
    return result

def patched_should_show(self, step):
    dep = step.depends_on
    result = original_should_show(self, step)
    print(f"    [_should_show] step={step.name}, depends_on={dep}, result={result}")
    return result

from framework.base_scenario import BaseScenario
original_process = BaseScenario.process_answer
original_advance = BaseScenario._advance_to_next_step
original_should_show = BaseScenario._should_show_step

BaseScenario.process_answer = patched_process
BaseScenario._advance_to_next_step = patched_advance
BaseScenario._should_show_step = patched_should_show

# Now run test
client = TestClient(app)
session_id = f"test_deep_{uuid.uuid4()}"

r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
session_id = r.json().get("session_id", session_id)

# Fill up to passport_code (index 5)
for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})

print("\n=== Now sending empty answer to skip passport_code ===")
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
data = r.json()
print(f"\nAPI response: step={data.get('current_step')}")