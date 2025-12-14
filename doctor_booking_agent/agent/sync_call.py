import sys
import requests

def sync_call(call_id):
    url = f"http://localhost:5000/api/call/sync/{call_id}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            print(f"Successfully synced call {call_id}")
            print(response.json())
        else:
            print(f"Failed to sync call {call_id}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sync_call.py <call_id>")
        sys.exit(1)
    
    call_id = sys.argv[1]
    sync_call(call_id)
