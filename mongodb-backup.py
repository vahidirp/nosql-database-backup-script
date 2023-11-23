import os
import subprocess
import shutil
from datetime import datetime

# Databases dictionary 
databases_info = [
    {"name": "db1", "host": "localhost", "port": "27017"},
    {"name": "db2", "host": "localhost", "port": "27017"},
    {"name": "db3", "host": "localhost", "port": "27017"}
]

backup_path = "/home/mongodb-backups"

os.makedirs(backup_path, exist_ok=True)

current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

for db_info in databases_info:
    db_name = db_info["name"]
    db_host = db_info["host"]
    db_port = db_info["port"]

    db_dir_path = os.path.join(backup_path, db_name)

    os.makedirs(db_dir_path, exist_ok=True)

    zip_file_name = os.path.join(db_dir_path, f"{db_name}_{current_datetime}.zip")

    backup_command = f"mongodump --host {db_host} --port {db_port} --db {db_name} --out {os.path.join(db_dir_path, db_name+'_backup')}"
    subprocess.run(backup_command, shell=True)

    shutil.make_archive(os.path.join(db_dir_path, db_name+"_backup"), 'zip', db_dir_path, db_name+"_backup")
  
    shutil.rmtree(os.path.join(db_dir_path, db_name+"_backup"))

    print(f"Backup for {db_name} completed. Zip file: {zip_file_name}")
