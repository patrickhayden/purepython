import pypureclient
import urllib3


# Disable SSL warnings
urllib3.disable_warnings()

# Colored text
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# Set this variable to manage the volume name search
pattern = 'sql'

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
        client = pypureclient.flasharray.Client('192.168.92.20', api_token=api_token)  # Edit to specify array IP
        return client
    except pypureclient.exceptions.PureError as e:
        print(f"API error occurred while initializing the client: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while initializing the client: {e}")
    return None


def main():
    print("Reading API token from file...")
    api_token = read_api_token('api.txt')
    if not api_token:
        print(f"{RED}Problem reading API token.{RESET}")
        return  # If API token is invalid or not found, exit early

    print("\nInitializing the PurePY client...")
    client = get_client(api_token)
    if not client:
        print(f"{RED}Problem initializing the PurePY client.{RESET}")
        return  # If client initialization failed, exit early

    print(f"\nGetting every array snapshot and filtering by string '{GREEN}{pattern}{RESET}'...")

    # Get all volume snapshots
    snap_response = client.get_volume_snapshots()
    if not snap_response.items:
        print(f"{RED}No snapshots found on the array.{RESET}")
        return

    # Filter snapshots by the global pattern
    snapshots_filtered = []
    for item in snap_response.items:
        snap_name = item['name']
        if pattern in snap_name:
            snapshots_filtered.append(snap_name)

    if not snapshots_filtered:
        print(f"{YELLOW}No snapshots matched the pattern '{pattern}'!{RESET}")
        return

    try:
        print("\nCataloging Protection Groups and matching against filtered snapshots...")
        pg_response = client.get_protection_groups_volumes()

        # Tracking set to identify which snapshots are "accounted for"
        protected_snapshots = set()
        if pg_response.items:
            for pgitem in pg_response.items:
                pg_name = pgitem['group']['name']
                pg_member_name = pgitem['member']['name']

                # Only care about PG members that match our pattern
                if pattern in pg_member_name:
                    for item in snapshots_filtered:
                        # Logic: Must start with PG name and end with the specific Volume name
                        # This prevents the duplicate output from other volumes in the same PG
                        if item.startswith(f"{pg_name}.") and item.endswith(f".{pg_member_name}"):
                            print(
                                f"{GREEN}Snapshot match found:{RESET} {item} (Member of {pg_name}) Source Vol: {pg_member_name}")
                            protected_snapshots.add(item)
        else:
            print(f"{YELLOW}Note: No Protection Groups found on the array!{RESET}")

        print("-" * 60)

        # Identify and print Orphans (snapshots that match the pattern but didn't map to a PG member above)
        orphans = []
        for snap in snapshots_filtered:
            if snap not in protected_snapshots:
                orphans.append(snap)

        if orphans:
            print(f"Listing snapshots matching {GREEN}'{pattern}'{RESET} NOT associated with any Protection Group...")
            for orphan in orphans:
                print(f"  - {orphan}")
        else:
            print(f"{GREEN}All snapshots matching '{pattern}' are associated with a Protection Group.{RESET}")

        # Final Summary
        print("-" * 60)
        print(f"Snapshots Matching Filter: {len(snapshots_filtered)}")
        print(f"{GREEN}Protected:      {len(protected_snapshots)}{RESET}")
        print(f"{YELLOW}Orphaned:       {len(orphans)}{RESET}")

    except Exception as e:
        print(f"{RED}An error occurred during processing: {e}{RESET}")


if __name__ == "__main__":
    main()
