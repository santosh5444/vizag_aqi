import requests
import json

try:
    url = "http://localhost:8000/api/farmer/login"
    payload = {"email": "monish@gmail.com", "password": "password"}
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
