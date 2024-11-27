import pypureclient
import urllib3
import os


# Disable SSL warnings
urllib3.disable_warnings()


def read_api_token(file_path):
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
    try:
        # Initialize the client with the token from the file
        client = pypureclient.flasharray.Client('192.168.92.20', api_token=api_token)  # edit to specify array IP
        return client
    except pypureclient.exceptions.PureError as e:
        print(f"API error occurred while initializing the client: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while initializing the client: {e}")
    return None


def print_vol_status(vol_name, vol_size):
    GREEN = "\033[32m"
    RESET = "\033[0m"  # Resets the color back to default

    print(f"{vol_name} {GREEN}{vol_size}{RESET} GiB provisioned")


def main():
    # Step 1: Read the API token from the file
    api_token = read_api_token('api.txt')
    if not api_token:
        return  # If API token is invalid or not found, exit early

    # Step 2: Initialize the client
    client = get_client(api_token)
    if not client:
        return  # If client initialization failed, exit early

    # Step 3: Get the list of volumes and handle the response
    response = client.get_volumes()
    if not response.items:
        print("No volumes found.")
        return

    # Loop through each volume and display status
    for item in response.items:
        vol_name = item.name
        vol_raw = item.provisioned
        vol_size = vol_raw / 1024 / 1024 / 1024

        # Print each volume's status
        print_vol_status(vol_name, vol_size)


# Entry point
if __name__ == "__main__":
    main()
