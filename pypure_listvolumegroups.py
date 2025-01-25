import pypureclient
import urllib3


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


def print_vg_status(vg_name, vol_count, qos, drr, virtual, unique):
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"  # Resets the color back to default

    print(f"{GREEN}{vg_name}{RESET} || Volume Count: {vol_count} || QOS: {qos}")
    print(f"Data Reduction: {round(drr,2)}")
    virtual_GB = virtual/1024/1024/1024
    unique_GB = unique/1024/1024/1024
    print(f"Virtual Space: {round(virtual_GB, 2)} GB || Unique Space: {YELLOW}{round(unique_GB, 2)}{RESET} GB")


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
    response = client.get_volume_groups()
    if not response.items:
        print("No volume groups found.")
        return

    for item in response.items:
        vg_name = item.name
        vol_count = item.volume_count
        qos = item.qos
        #space = item.space
        drr = item.space.data_reduction
        unique = item.space.unique
        virtual = item.space.virtual

        # Print each VG's status
        print_vg_status(vg_name, vol_count, qos, drr, virtual, unique)


# Entry point
if __name__ == "__main__":
    main()
