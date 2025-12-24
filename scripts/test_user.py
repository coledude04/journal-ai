import firebase_admin
from firebase_admin import credentials, auth
import requests

cred = credentials.Certificate('') # Cred file path
firebase_admin.initialize_app(cred)

test_uid = "test-user-postman"

# Create custom token
custom_token = auth.create_custom_token(test_uid)
custom_token_str = custom_token.decode('utf-8')

# Exchange for ID token (required for Cloud Run)
url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken"
payload = {
    "token": custom_token_str,
    "returnSecureToken": True
}
response = requests.post(
    url,
    json=payload,
    params={"key": ""}  # Get from Firebase Console > Project Settings > General
)

if response.status_code == 200:
    id_token = response.json()["idToken"]
    print(f"ID Token:\n{id_token}")
else:
    print(f"Error: {response.text}")