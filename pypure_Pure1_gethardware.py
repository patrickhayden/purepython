from pypureclient import pure1
from pypureclient.exceptions import PureError
import urllib3
import os

urllib3.disable_warnings()


def read_password(private_key_password: str) -> str:
    """Read from file password.txt with private key decryption password"""
    try:
        # Open the file and read the token
        with open('password.txt', 'r') as file:
            private_key_password = file.read().strip()
            if not private_key_password:
                raise ValueError("Password file is empty.")
            return private_key_password
    except FileNotFoundError:
        print(f"Error: The file was not found.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


def get_client(app_id: str) -> str:
    """Authenticates to Pure1 and returns a client object.  Requires app_id from Pure1 and Private Key at minimum"""
    private_key_file = "pure1key.txt"
    private_key_password = read_password(private_key_file)    # if the private key file is password protected

    if not os.path.exists(private_key_file):
        print(f"ERROR: Private key file not found: {private_key_file}")
        return None

    try:
        client = pure1.Client(
            private_key_file=private_key_file,
            private_key_password=private_key_password,
            app_id=app_id,
        )
        return client
    except PureError as e:
        print(e)
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def main():
    """Main function. Execute simple Pure1 query to get_volumes to demonstrate client usage."""
    app_id = "pure1:apikey:SEAdY9KN1C7KucZ0"  # Replace with actual app ID from Pure1
    client = get_client(app_id)

    if client:
        print("Client obtained successfully. Proceeding with API calls.\n")


        try:
            response = client.get_hardware()
            hardware = list(response.items)
            #print(hardware)
            for item in hardware:
                print(item.name)
                hardware_type = item.type
                print(f"Status: {item.status} for {hardware_type}")

        except Exception as e:
            print(f"Error getting volumes: {e}")
    else:
        print("Failed to obtain client. Exiting.")
        return ValueError("Nope")


if __name__ == "__main__":
    main()
