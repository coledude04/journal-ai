import time
import requests
import json
from datetime import datetime

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

# Usage
file_name = ''  # Replace with your actual file path
parsed_logs = parse_journal_logs(file_name)
auth_token = ""

api_url = ""
headers = {
    "Authorization": f"Bearer {auth_token}"
}

# Displaying the results
for i, entry in enumerate(parsed_logs):
    payload = {
        "date": entry['date'],
        "content": entry['content'],
        "timezone": "America/New_York"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)

        response.raise_for_status()

        print(f"Status Code: {response.status_code}")
        print("Response Content:")
        print(json.dumps(response.json(), indent=4))

    except Exception as e:
        print(f"Exception: {e}")

    print(f"{entry['date']}: {i + 1}/{len(parsed_logs)}")
    time.sleep(1)