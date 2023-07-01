import json
import os
max_users = input("Enter the maximum number of users: ")
enc_db_folder = input("Enter the path to the database folder (enc): ")
db_folder = input("Enter the path to the database folder: ")
max_users = int(max_users)
config = {
    "max_users": max_users,
    "db_folder": db_folder,
    "enc_db_folder": enc_db_folder}
if os.path.exists("config.json"):
    print("Config file already exists")
    exit()
with open("config.json", "w") as f:
    json.dump(config, f)
print("Config file created")