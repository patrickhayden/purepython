import pypureclient
from pypureclient.flasharray.FA_2_35.models import VolumeSnapshotPost
import urllib3

urllib3.disable_warnings()

# Initialize the client
client = pypureclient.flasharray.Client('192.168.92.20', api_token='xxxxxxx-yyyyy')

# Get the list of volumes
volumes = client.get_volumes()

# Iterate over each volume and create a snapshot
for item in volumes.items:
    volume_name = item.name
    print(volume_name)
    snap_suffix='pysnap'      # edit accordingly
    snapshot_name = f"{volume_name}.{snap_suffix}"

    # Create the snapshot
    try:
        volume_snapshot_details = VolumeSnapshotPost(suffix=snap_suffix)         # Define the snapshot details

        # Create the snapshot
        new_snap = client.post_volume_snapshots(
            source_names=[volume_name],
            volume_snapshot=volume_snapshot_details
        )

        print(f"Snapshot '{snapshot_name}' created for volume '{volume_name}'.")
    except Exception as e:
        print(f"Failed to create snapshot for volume '{volume_name}': {e}")
