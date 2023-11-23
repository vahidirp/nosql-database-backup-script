from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import datetime
import os
import shutil

# Cassandra credentials and connection settings
cassandra_contact_points = ['localhost']  # Replace with your Cassandra contact points
cassandra_username = 'YOUR_CASSANDRA_USERNAME'  # Replace with your Cassandra username
cassandra_password = 'YOUR_CASSANDRA_PASSWORD'  # Replace with your Cassandra password
cassandra_keyspace = 'YOUR_KEYSPACE'  # Replace with your Cassandra keyspace

# Backup path
backup_path = "/home/cassandra-backups"

# Connect to Cassandra cluster
auth_provider = PlainTextAuthProvider(username=cassandra_username, password=cassandra_password)
cluster = Cluster(contact_points=cassandra_contact_points, auth_provider=auth_provider)
session = cluster.connect()

# Timestamp for the backup folder and filename
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_folder = os.path.join(backup_path, current_datetime)
os.makedirs(backup_folder, exist_ok=True)

# Backup each keyspace
keyspaces = [row[0] for row in session.execute("SELECT keyspace_name FROM system_schema.keyspaces")]
for keyspace in keyspaces:
    backup_filename = os.path.join(backup_folder, f"{keyspace}_{current_datetime}.cql")

    # Execute nodetool snapshot for the keyspace
    snapshot_command = f"nodetool snapshot -t {current_datetime} {keyspace}"
    os.system(snapshot_command)

    # Copy the snapshot files to the backup folder
    snapshot_path = os.path.join(os.getcwd(), "data", keyspace, "snapshots", current_datetime)
    shutil.copytree(snapshot_path, backup_folder)

    # Remove the snapshot files
    os.system(f"nodetool clearsnapshot -t {current_datetime} {keyspace}")

    print(f"Backup for keyspace {keyspace} completed. Snapshot files copied to: {backup_folder}")

# Disconnect from Cassandra cluster
cluster.shutdown()
