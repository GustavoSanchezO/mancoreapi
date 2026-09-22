import requests
import json

# Login as employee
res = requests.get("http://127.0.0.1:8000/auth/")
print("Auth without login:", res.status_code)

# We can just check via FastAPI TestClient
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
# Actually, since auth uses cookies, we'd need to mock it.
