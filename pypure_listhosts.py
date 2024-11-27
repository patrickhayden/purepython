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


def print_host_status(host_name, iscsi_port, fc_port, connectivity_status, connectivity_details):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"  # Resets the color back to default

    # Determine color based on status
    if connectivity_status == "critical":
        status_output = f"{RED}{connectivity_status}{RESET}"
    elif connectivity_status == "healthy":
        status_output = f"{GREEN}{connectivity_status}{RESET}"
    else:
        status_output = f"{YELLOW}{connectivity_status}{RESET}"

    # Print the status
    print(f"{host_name} || IQN: {iscsi_port}, WWN: {fc_port}, {status_output}, {connectivity_details}.")


def main():
    # Step 1: Read the API token from the file
    api_token = read_api_token('api.txt')
    if not api_token:
        return  # If API token is invalid or not found, exit early

    # Step 2: Initialize the client
    client = get_client(api_token)
    if not client:
        return  # If client initialization failed, exit early

    # Step 3: Get the list of hosts and handle the response
    response = client.get_hosts()
    if not response.items:
        print("No hosts found.")
        return

    for item in response.items:
        host_name = item.name
        iscsi_port = item.iqns
        fc_port = item.wwns
        connectivity_status = item.port_connectivity.status
        connectivity_details = item.port_connectivity.details

        # Print each host's status
        print_host_status(host_name, iscsi_port, fc_port, connectivity_status, connectivity_details)


# Entry point
if __name__ == "__main__":
    main()
