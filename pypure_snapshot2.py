import pypureclient
from pypureclient.exceptions import PureError
from pypureclient.flasharray.FA_2_35.models import VolumeSnapshotPost
from argparse import ArgumentParser
import urllib3

# Disable SSL warnings
urllib3.disable_warnings()


def read_api_token(file_path):
    """Read from a file with Pure Storage API credentials"""
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
    """Authenticate to Pure Storage array with API token"""
    try:
        # Initialize the client with the token from the file
        client = pypureclient.flasharray.Client('192.168.92.20', api_token=api_token)  # edit to specify array IP
        return client
    except pypureclient.exceptions.PureError as e:
        print(f"API error occurred while initializing the client: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while initializing the client: {e}")
    return None


def main():
    """Authenticate and connect to a Pure Storage array and compile a list of existing volumes.  Filter the volumes to
    create a subset to perform snapshot operations.  Perform the snapshot if it doesn't already exist on the array."""

    # Step 1: Read the API token from the file
    api_token = read_api_token('api.txt')
    if not api_token:
        return  # If API token is invalid or not found, exit early

    # Step 2: Initialize the client
    client = get_client(api_token)
    if not client:
        return  # If client initialization failed, exit early

    # Step 3: Build list of existing snaps
    snaps = []
    response = client.get_volume_snapshots()
    for item in response.items:
        snap_name = item.name
        snaps.append(snap_name)

    # Step 4: Form the new snapshot name
    parser = ArgumentParser()
    parser.add_argument("snap_suffix", type=str)
    args = parser.parse_args()

    # Step 5:  Create snapshot if it doesn't already exist
    volumes = client.get_volumes()
    for item in volumes.items:
        volume_name = item.name
        if "ds" in volume_name:         # filter a subset of volumes to snap
            snap_suffix = args.snap_suffix
            snapshot_name = f"{volume_name}.{snap_suffix}"

            try:
                if snapshot_name not in snaps:
                    volume_snapshot_details = VolumeSnapshotPost(suffix=snap_suffix)  # Define the snapshot details
                    # Create the snapshot
                    new_snap = client.post_volume_snapshots(
                        source_names=[volume_name],
                        volume_snapshot=volume_snapshot_details
                    )
                    print(f"Snapshot '{snapshot_name}' created for volume '{volume_name}'.")
                else:
                    raise ValueError(f"Snapshot '{snapshot_name}' already exists (possibly pending eradication)")

            except PureError as e:
                print(f"Failed to create snapshot for volume '{volume_name}': {e}")

            except ValueError as e:
                print(f"Error: {e}")


# Entry point
if __name__ == "__main__":
    main()
