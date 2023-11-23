import subprocess
import os
import datetime

# Redis Database server identity configurations
redis_host = 'localhost'
redis_port = 6379
redis_password = 'your_redis_password'  # Set to None if no password is set
backup_directory = '/home/redisbackup'

# Create backup directory if it doesn't exist
if not os.path.exists(backup_directory):
    os.makedirs(backup_directory)

# Create a folder with the current date
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
backup_folder = os.path.join(backup_directory, current_date)
os.makedirs(backup_folder, exist_ok=True)

# Fetch all Redis databases
redis_databases = subprocess.check_output(['redis-cli', '-h', redis_host, '-p', str(redis_port), '-a', redis_password, 'INFO', 'keyspace'])

# Extract the database numbers
database_numbers = [int(db.split(':')[0].split('db')[1]) for db in redis_databases.decode('utf-8').split('\n') if 'db' in db]

# Backup each database
for db_number in database_numbers:
    output_file = os.path.join(backup_folder, f'dump_db{db_number}.rdb')
    subprocess.run(['redis-cli', '-h', redis_host, '-p', str(redis_port), '-a', redis_password, 'SAVE'])
    subprocess.run(['redis-cli', '-h', redis_host, '-p', str(redis_port), '-a', redis_password, 'BGSAVE'])
    subprocess.run(['cp', os.path.join('/var/lib/redis', f'dump.rdb'), output_file])
    print(f'Database {db_number} backed up to {output_file}')

print('Backup completed.')
