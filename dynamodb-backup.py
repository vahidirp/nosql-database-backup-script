import os
import zipfile
import boto3
from datetime import datetime

# AWS credentials and region
aws_access_key_id = 'YOUR_ACCESS_KEY_ID'
aws_secret_access_key = 'YOUR_SECRET_ACCESS_KEY'
aws_region = 'YOUR_AWS_REGION'

# Backup path
backup_path = "/home/dynamodb-backups"

# Create a DynamoDB client
dynamodb = boto3.client('dynamodb', region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# List all tables in DynamoDB
response = dynamodb.list_tables()
tables = response['TableNames']

# Timestamp for the backup filename and folder
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_folder = os.path.join(backup_path, current_datetime)
os.makedirs(backup_folder, exist_ok=True)

# Create a DynamoDB backup for each table
for table_name in tables:
    backup_filename = os.path.join(backup_folder, f"{table_name}_{current_datetime}.zip")

    # Create a backup using AWS Backup
    backup_response = dynamodb.create_backup(TableName=table_name, BackupName=f"{table_name}_backup_{current_datetime}")

    # Wait for the backup to be completed
    backup_arn = backup_response['BackupDetails']['BackupArn']
    dynamodb.get_waiter('backup_exists').wait(BackupArn=backup_arn)

    # Download the backup file
    backup_location = backup_response['BackupDetails']['S3Backup']['S3Bucket'] + '/' + backup_response['BackupDetails']['S3Backup']['S3Key']
    s3 = boto3.client('s3', region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.download_file(backup_response['BackupDetails']['S3Backup']['S3Bucket'], backup_response['BackupDetails']['S3Backup']['S3Key'], backup_filename)

    print(f"Backup for table {table_name} completed. Zip file: {backup_filename}")

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
