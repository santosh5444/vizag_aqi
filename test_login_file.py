import requests
try:
    url = "http://localhost:8000/api/farmer/login"
    payload = {"email": "monish@gmail.com", "password": "password"}
    response = requests.post(url, json=payload, timeout=5)
    with open("response.txt", "w") as f:
        f.write(f"Status Code: {response.status_code}\n")
        f.write(f"Response: {response.text}\n")
except Exception as e:
    with open("response.txt", "w") as f:
        f.write(f"Exception: {e}\n")
