import requests
import urllib.parse
import urllib3
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

# Hard-coded values for testing
TOKEN = "M8qp_kcGLejWdkFG4vx9cu8fD02VRiEweegScYjBs9tU5emUS6DV6L9msaucEV0sC2RjZQVZr8ORvtUWuEO7_1VGq3SCFM3wGU-I"
SERVER_ID = "ni8292907_1"
NITRADO_ID = "16355842"


def debug_nitrado_download():
    # Base headers
    headers = {'Authorization': f'Bearer {TOKEN}'}
    # Common request parameters with SSL verification disabled
    request_params = {
        'headers': headers,
        'verify': False,  # Disable SSL verification
    }
   
    server_url = f'https://api.nitrado.net/services/{NITRADO_ID}/gameservers/file_server/download?file=/games/{SERVER_ID}/ftproot/dayzxb_missions/dayzOffline.chernarusplus/db/events.xml'
    print(f"URL: {server_url}")
    print(f"Headers: {headers}")

    print("\n=== Calling download API ===")
    server_response = requests.get(server_url, **request_params)
    print(f"Response Status: {server_response.status_code}")
    print(f"Response Body: {server_response.text}")
    print(f"Response size: {len(server_response.content)}\n")     

if __name__ == "__main__":
    print("=== Nitrado API Download Debug Script ===")
    debug_nitrado_download()