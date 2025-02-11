import pypureclient
import urllib3
import os
from datetime import datetime


# Disable SSL warnings
urllib3.disable_warnings()


def read_api_token(file_path):
    """access file with Pure Storage API credentials"""
    try:
        # Open the file and read the token
        with open(file_path, 'r') as file:
            api_token = file.read().strip()
            if not api_token:
                raise ValueError("API token is empty.")
            return api_token
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


def get_client(api_token):
    """authenticate to Pure Storage array with API token"""
    try:
        # Initialize the client with the token from the file
        client = pypureclient.flasharray.Client('192.168.92.20', api_token=api_token)  # edit to specify array IP
        return client
    except pypureclient.exceptions.PureError as e:
        print(f"API error occurred while initializing the client: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while initializing the client: {e}")
    return None


def convert_ms_to_datetime(milliseconds):
    """Converts milliseconds since the UNIX epoch to user-readable timestamp"""
    seconds = milliseconds / 1000
    timestamp = datetime.fromtimestamp(seconds)
    return datetime.strftime(timestamp, "%Y-%m-%d %H:%M:%S")


def print_snap_status(snap_name, snap_source, created, destroyed=False):
    """output the snapshot list"""
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"  # Resets the color back to default

    status_message = f"{GREEN}{snap_name}{RESET} based on {snap_source} || created at: {created}"
    if destroyed:
        status_message += f"  {RED}Pending Eradication{RESET}"

    print(status_message)


def main():
    # Step 1: Read the API token from the file
    api_token = read_api_token('api.txt')
    if not api_token:
        return  # If API token is invalid or not found, exit early

    # Step 2: Initialize the client
    client = get_client(api_token)
    if not client:
        return  # If client initialization failed, exit early

    # Step 3: Get the list of snapshots and handle the response
    response = client.get_volume_snapshots()
    if not response.items:
        print("No snapshots found.")
        return

    # Loop through each snap and display status
    for item in response.items:
        snap_name = item.name
        snap_source = item.source.name
        created = convert_ms_to_datetime(item.created)

        destroyed = item.destroyed
        if not destroyed:
            print_snap_status(snap_name, snap_source, created, destroyed=False)
        else:
            print_snap_status(snap_name, snap_source, created, destroyed=True)

# Entry point
if __name__ == "__main__":
    main()
