import requests
import json
from random_insert_thread import generate_name, generate_category, generate_thread_text, generate_title
url = "http://127.0.0.1:8000/api/v1/insert-thread"  # Change this to your actual endpoint

# JSON payload
payload = {
    "username": "Joe Bide",
    "thread_text": "USA",
    "title_text": "I dropped my ice cream",
    "category": "lol",
    "company_profile": "magnussons-fisk-ab",
}

# Headers
headers = {
    "Content-Type": "application/json"
}

# Print the payload for debugging
print("Payload:")
print(json.dumps(payload, indent=2))

# Send POST request
response = requests.post(url, json=payload, headers=headers)

# Check response
print(f"Status Code: {response.status_code}")
print("Response Content:")
print(json.dumps(response.json(), indent=2))

if response.status_code >= 400:
    print("\nError Details:")
    print(f"Error Type: {response.json().get('detail', 'Unknown error')}")

