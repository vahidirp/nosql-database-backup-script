import os
import shutil
from datetime import datetime, timedelta
import requests

# CouchDB credentials and connection settings
couchdb_url = 'http://<username>:<password>@<hostname>:<port>'
database_name = 'YOUR_DATABASE_NAME'  # Replace with your CouchDB database name

# Backup path
backup_path = "/home/couchdb-backups"

# Timestamp for the backup folder and filename
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_folder = os.path.join(backup_path, current_datetime)
os.makedirs(backup_folder, exist_ok=True)

# Backup the CouchDB database
backup_url = f"{couchdb_url}/{database_name}"
backup_filename = os.path.join(backup_folder, f"{database_name}_{current_datetime}.json")

try:
    response = requests.get(backup_url)
    response.raise_for_status()

    with open(backup_filename, 'wb') as backup_file:
        backup_file.write(response.content)

    print(f"Backup for database {database_name} completed. JSON file: {backup_filename}")

except requests.exceptions.RequestException as e:
    print(f"Error creating backup: {e}")

# Optional: Delete old backups or perform other cleanup if needed
def delete_old_backups(backup_path, retention_days):
    current_time = datetime.now()
    for backup_folder in os.listdir(backup_path):
        backup_folder_path = os.path.join(backup_path, backup_folder)
        if os.path.isdir(backup_folder_path):
            try:
                folder_datetime = datetime.strptime(backup_folder, "%Y%m%d_%H%M%S")
                days_difference = (current_time - folder_datetime).days
                if days_difference > retention_days:
                    # Delete the old backup folder
                    print(f"Deleting old backup folder: {backup_folder_path}")
                    shutil.rmtree(backup_folder_path)
            except ValueError:
                # Ignore folders with incorrect datetime format
                pass

# Set the retention period in days
retention_days = 7

# Call the function to delete old backups
delete_old_backups(backup_path, retention_days)
