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


def print_controller_status(controller_name, model, conttype, version, status, mode):
    RED = "\033[31m"
    GREEN = "\033[32m"
    RESET = "\033[0m"  # Resets the color back to default

    if status == "ready":
        print(f"{controller_name} {model} {conttype} Purity {version} {GREEN}{status}{RESET} || {mode}")
    else:
        print(f"{controller_name} {model} {conttype} Purity {version} {RED}{status}{RESET} || {mode}")


def main():
    # Step 1: Read the API token from the file
    api_token = read_api_token('api.txt')
    if not api_token:
        return  # If API token is invalid or not found, exit early

    # Step 2: Initialize the client
    client = get_client(api_token)
    if not client:
        return  # If client initialization failed, exit early

    # Step 3: Get the list of controllers and handle the response
    response = client.get_controllers()
    if not response.items:
        print("No controllers found.")
        return

    for item in response.items:
        controller_name = item.name
        mode = item.mode
        model = item.model
        status = item.status
        conttype = item.type
        version = item.version

        # Print each controller's status
        print_controller_status(controller_name, model, conttype, version, status, mode)


# Entry point
if __name__ == "__main__":
    main()
