import os
import requests
import firebase_admin
from firebase_admin import credentials, auth


def _load_dotenv_manual(dotenv_path):
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        _load_dotenv_manual('.env')

    cred_path = os.environ.get('FIREBASE_CRED_PATH')
    api_key = os.environ.get('FIREBASE_API_KEY')
    test_uid = os.environ.get('TEST_UID', 'test-user-postman')

    if not cred_path:
        print('Please set FIREBASE_CRED_PATH in environment or .env')
        return
    if not api_key:
        print('Please set FIREBASE_API_KEY in environment or .env')
        return

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

    # Create custom token
    custom_token = auth.create_custom_token(test_uid)
    try:
        custom_token_str = custom_token.decode('utf-8')
    except Exception:
        custom_token_str = str(custom_token)

    # Exchange for ID token (required for Cloud Run)
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken"
    payload = {
        "token": custom_token_str,
        "returnSecureToken": True
    }
    response = requests.post(
        url,
        json=payload,
        params={"key": api_key}
    )

    if response.status_code == 200:
        id_token = response.json().get("idToken")
        print(f"ID Token:\n{id_token}")
    else:
        print(f"Error: {response.text}")


if __name__ == '__main__':
    main()