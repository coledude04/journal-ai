import os
import time
import requests
import json
from datetime import datetime


def _load_dotenv_manual(dotenv_path):
    """Lightweight .env loader if python-dotenv isn't available."""
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


def parse_journal_logs(file_path):
    logs = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            # Check if the line has a colon and isn't empty
            if ":" in line:
                # Split only on the first colon to keep colons in the content
                parts = line.split(":", 1)
                date_str = parts[0].strip()
                content_str = parts[1].strip()

                try:
                    # Attempt to parse the date (M/D/YYYY)
                    date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                    # Format to YYYY-MM-DD
                    formatted_date = date_obj.strftime("%Y-%m-%d")

                    logs.append({
                        "date": formatted_date,
                        "content": content_str
                    })
                except ValueError:
                    # If it's not a valid date (e.g., "Note: hello"), skip it
                    continue

    return logs


def main():
    # Try to load .env (prefer python-dotenv if available)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        _load_dotenv_manual('.env')

    file_name = os.environ.get('JOURNAL_FILE', '')
    if not file_name:
        print('Please set JOURNAL_FILE in the environment or .env file')
        return

    api_url = os.environ.get('API_URL', '')
    auth_token = os.environ.get('AUTH_TOKEN', '')
    timezone = os.environ.get('TIMEZONE', 'America/New_York')
    sleep_seconds = float(os.environ.get('SLEEP_SECONDS', '1'))

    if not api_url:
        print('Please set API_URL in the environment or .env file')
        return

    headers = {}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'

    parsed_logs = parse_journal_logs(file_name)

    for i, entry in enumerate(parsed_logs):
        payload = {
            "date": entry['date'],
            "content": entry['content'],
            "timezone": timezone
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()

            print(f"Status Code: {response.status_code}")
            try:
                print(json.dumps(response.json(), indent=4))
            except Exception:
                print(response.text)

        except Exception as e:
            print(f"Exception: {e}")

        print(f"{entry['date']}: {i + 1}/{len(parsed_logs)}")
        time.sleep(sleep_seconds)


if __name__ == '__main__':
    main()