from fastapi.testclient import TestClient
import requests

# Test with requests library instead to see raw HTTP
session_id = "test_http_001"
base_url = "http://127.0.0.1:8000"

# First, start the server manually and then test
# Let's use TestClient but add more debug

from main import app
from fastapi.testclient import TestClient

# Override the endpoint to add logging
original_handler = None

# Use the test client but print what's happening
client = TestClient(app, raise_server_exceptions=False)

session_id = "test_debug_http"

# Start
r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ""})
print(f"Start: {r.status_code}, {r.json().get('current_step')}")
session_id = r.json().get("session_id", session_id)

# Fill up to passport_code (index 5)
for ans in ["Иванов Иван Иванович", "4510", "123456", "УВД г. Москвы", "01.01.2020"]:
    r = client.post("/api/scenario/receipt_simple", json={"session_id": session_id, "answer": ans})
    data = r.json()
    print(f"  After '{ans[:15]}...': step={data.get('current_step')}")

# Now check - what's the current step?
print(f"\nBefore empty answer, current step: {r.json().get('current_step')}")

# Send empty answer - let's see raw request/response
import http.client
import json as json_lib

# Actually, let's just print what's in the request object
print(f"\nSending empty answer...")
r = client.post(
    "/api/scenario/receipt_simple", 
    json={"session_id": session_id, "answer": ""},
    headers={"Content-Type": "application/json"}
)
data = r.json()
print(f"Response: status={r.status_code}, step={data.get('current_step')}, question={data.get('question', '')[:30] if data.get('question') else 'None'}")
print(f"Response full: {data}")