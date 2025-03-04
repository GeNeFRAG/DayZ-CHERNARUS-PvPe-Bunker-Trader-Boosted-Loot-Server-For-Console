import requests
import urllib.parse
import urllib3
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)


def get_file_stats(self, remote_dirs):
    """
    Get file information from the server.

    Args:
        remote_dirs (list): List of remote directories to get file stats from.

    Returns:
        list: List of file stats, or None if an error occurred.
    """
    print(f"Get file information from Nitrado...")
    base_path = f"/games/{self.server_id}/ftproot/dayzxb_missions/dayzOffline.chernarusplus/"

    try:
        # Get file stats from the main directory
        url = f'{NITRADO_API_BASE_URL}{self.nitrado_id}{self.remote_base_path}/list?dir={base_path}'
        response = requests.get(url, headers=self.headers, verify=self.ssl_verify)
        
        if response.status_code == 200:
            response_json = response.json()
            file_stats = [
                {
                    'path': file['path'],
                    'modified_at': datetime.fromtimestamp(file['modified_at']).isoformat(),
                    'name': file['name']
                }
                for file in response_json['data']['entries'] if file['type'] == 'file'
            ]
        else:
            print(f"Error fetching file stats: {response.text}")
            return None
        
        # Get file stats from each remote directory
        for remote_dir in remote_dirs:
            dir_url = f'{NITRADO_API_BASE_URL}{self.nitrado_id}{self.remote_base_path}/list?dir={base_path}/{remote_dir}'
            dir_response = requests.get(dir_url, headers=self.headers, verify=self.ssl_verify)
            if dir_response.status_code == 200:
                dir_response_json = dir_response.json()
                file_stats.extend([
                    {
                        'path': file['path'],
                        'modified_at': datetime.fromtimestamp(file['modified_at']).isoformat(),
                        'name': file['name']
                    }
                    for file in dir_response_json['data']['entries'] if file['type'] == 'file'
                ])
            elif dir_response.status_code == 404:
                print(f"ERROR: Directory not found: {dir_response.status_code} {remote_dir}")
                return None
            else:
                print(f"Error fetching file stats from {remote_dir}: {dir_response.status_code}: {dir_response.text}")
                return None
        print(f"Successfully fetched {len(file_stats)} file stats fromo Nitrado")
        return file_stats
    except Exception as e:
        print(f"ERROR: {str(e)}")
    return None

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