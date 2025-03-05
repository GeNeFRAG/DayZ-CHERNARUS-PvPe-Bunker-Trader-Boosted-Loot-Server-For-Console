import requests
import json
import argparse
import fnmatch
import sys
from datetime import datetime
import urllib3
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

NITRADO_API_BASE_URL = "https://api.nitrado.net/services/"

class NitradoAPI:
    def __init__(self, token, nitrado_id, server_id, remote_base_path, ssl_verify=True):
        """
        Initialize the NitradoAPI class.

        Args:
            token (str): Nitrado API token.
            nitrado_id (str): Nitrado ID.
            server_id (str): Game server ID.
            remote_base_path (str): Base path for remote files.
            ssl_verify (bool): Whether to verify SSL certificates.
        """
        self.token = token
        self.nitrado_id = nitrado_id
        self.server_id = server_id
        self.headers = {"Authorization": f"Bearer {token}"}
        self.remote_base_path = remote_base_path
        self.ssl_verify = ssl_verify

    def get_logs_info(self):
        """
        Get log files information from the server.

        Returns:
            list: List of file stats, or None if an error occurred.
        """
        print(f"Get log files information from Nitrado...")
        base_path = f"/games/{self.server_id}/ftproot/dayzxb/config/"

        try:
            # Get file stats from the directory
            url = f"{NITRADO_API_BASE_URL}{self.nitrado_id}{self.remote_base_path}/list?dir={base_path}"
            response = requests.get(url, headers=self.headers, verify=self.ssl_verify)

            if response.status_code == 200:
                response_json = response.json()
                if len(response_json["data"]["entries"]) == 0:
                    print(f"No file stats returned for {base_path}")
                    return None
                file_stats = [
                    {
                        "path": file["path"],
                        "modified_at": datetime.fromtimestamp(
                            file["modified_at"]
                        ).isoformat(),
                        "name": file["name"],
                    }
                    for file in response_json["data"]["entries"]
                    if file["type"] == "file"
                ]
            else:
                print(
                    f"Error fetching file stats: {response.status_code} : {response.text}"
                )
                return None

            print(f"Successfully fetched {len(file_stats)} log file stats from Nitrado")
            return file_stats
        except Exception as e:
            print(f"ERROR: {str(e)}")
        return None

    def download_file(self, file_path):
        """
        Download a file using Nitrado's two-step download process.
        
        Args:
            file_path: Path to the file to download
            
        Returns:
            Optional[bytes]: File content if successful, None if failed
        """
        try:
            # Step 1: Get download token
            url = f'{NITRADO_API_BASE_URL}{self.nitrado_id}{self.remote_base_path}/download?file={file_path}'
            token_response = self._get_download_token(url)

            if not token_response or 'data' not in token_response:
                print(f"Failed to get download token for {file_path}")
                return None

            # Extract token information
            token_data = token_response['data']['token']
            download_url = token_data['url']
            download_token = token_data['token']

            # Step 2: Download the actual file using the token
            download_response = requests.get(
                download_url,
                params={'token': download_token},
                verify=self.ssl_verify
            )
            
            download_response.raise_for_status()
            print(f"Successfully downloaded {file_path}")
            return download_response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file {file_path}: {e}")
            return None
        except KeyError as e:
            print(f"Unexpected response format while downloading {file_path}: {e}")
            return None

    def _get_download_token(self, url):
        """
        Make an API request to Nitrado
        
        Args:
            url: Download URL
            
        Returns:
            Optional[Dict]: JSON response if successful, None if failed
        """
        try: 
            response = requests.get(url, headers=self.headers, verify=self.ssl_verify)
            response.raise_for_status()
            print(f"Successfully fetched download token for {url}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except ValueError as e:
            print(f"Failed to parse API response: {e}")
            return None

def filter_and_download_logs(api: NitradoAPI, 
                           file_stats,
                           start_date: str = None,
                           end_date: str = None,
                           filename_pattern: str = None,
                           latest_default: bool = True) -> bool:
    """
    Filter and download log files based on various criteria.
    By default, downloads the 2 latest .RPT and 2 latest .ADM files.
    
    Args:
        api: NitradoAPI instance
        file_stats: List of file statistics
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        filename_pattern: Unix-style filename pattern
        latest_default: If True, download 2 latest .RPT and 2 latest .ADM files when no other filters match
    
    Returns:
        bool: True if any files were downloaded successfully, False otherwise
    """
    if not file_stats:
        print("No file stats provided")
        return False

    filtered_files = []

    # Apply filters if provided
    if start_date or end_date or filename_pattern:
        # Apply date filters if provided
        # Apply date filters if provided
        if start_date or end_date:
            try:
                # Convert start_date and end_date to datetime objects
                start_dt = datetime.fromisoformat(start_date + "T00:00:00") if start_date else datetime.min
                end_dt = datetime.fromisoformat(end_date + "T23:59:59") if end_date else datetime.max
                
                filtered_files = [
                    f for f in file_stats
                    if start_dt <= datetime.fromisoformat(f['modified_at']) <= end_dt
                ]
                print(f"Filtered files based on date range ({start_date} to {end_date}):")
            except ValueError as e:
                print(f"Error parsing dates: {e}")
                return False

        # Apply filename pattern if provided
        if filename_pattern:
            filtered_files = [
                f for f in filtered_files
                if fnmatch.fnmatch(f['name'].lower(), filename_pattern.lower())
            ]
    else:
        # If no specific filters are provided and latest_default is True,
        # get the 2 latest .RPT and 2 latest .ADM files
        if latest_default:
            # Get and sort RPT files by modification date
            rpt_files = sorted(
                [f for f in file_stats if f['name'].endswith('.RPT')],
                key=lambda x: x['modified_at'],
                reverse=True
            )
            
            # Get and sort ADM files by modification date
            adm_files = sorted(
                [f for f in file_stats if f['name'].endswith('.ADM')],
                key=lambda x: x['modified_at'],
                reverse=True
            )
            
            # Add up to 2 latest RPT files
            if rpt_files:
                filtered_files.extend(rpt_files[:2])
                print(f"Selected {len(rpt_files[:2])} latest RPT files")
            else:
                print("No RPT files found")

            # Add up to 2 latest ADM files
            if adm_files:
                filtered_files.extend(adm_files[:2])
                print(f"Selected {len(adm_files[:2])} latest ADM files")
            else:
                print("No ADM files found")

    if not filtered_files:
        print("No files matched the specified criteria")
        return False

    # Download matched files
    success = True
    for file in filtered_files:
        print(f"Downloading {file['name']} (Modified: {file['modified_at']})")
        content = api.download_file(file['path'])
        if content:
            # Save the file locally
            try:
                with open(file['name'], 'wb') as f:
                    f.write(content)
                print(f"Successfully saved: {file['name']}")
            except IOError as e:
                print(f"Error saving {file['name']}: {e}")
                success = False
        else:
            print(f"Failed to download {file['name']}")
            success = False
    print(f"Downloaded {len(filtered_files)} files")
    return success

def main():
    parser = argparse.ArgumentParser(
        description="Download DayZ server logs with filters"
    )
    parser.add_argument(
        "--config",
        default="nitrado_api.json",
        help="Path to configuration file (default: nitrado_api.json)",
    )
    parser.add_argument("--start-date", help="Start date for log files (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date for log files (YYYY-MM-DD)")
    parser.add_argument(
        "--pattern", help='Filename pattern (e.g., "*.RPT" or "script_*.ADM")'
    )
    parser.add_argument(
        "--no-default",
        action="store_true",
        help="Disable downloading latest .RPT and .ADM files when no other filters match",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        with open(args.config, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False

    # Initialize NitradoAPI
    api = NitradoAPI(
        config["api_token"],
        config["nitrado_id"],
        config["server_id"],
        config["remote_base_path"],
        config.get("ssl_verify", True),
    )

    # Get log files information
    file_stats = api.get_logs_info()
    if not file_stats:
        return False

    # Apply filters and download files
    return filter_and_download_logs(
        api,
        file_stats,
        start_date=args.start_date,
        end_date=args.end_date,
        filename_pattern=args.pattern,
        latest_default=not args.no_default,
    )


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
