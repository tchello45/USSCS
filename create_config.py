import json
import os
max_users = input("Enter the maximum number of users: ")
max_users = int(max_users)
config = {
    "max_users": max_users}
if os.path.exists("config.json"):
    print("Config file already exists")
    exit()
with open("config.json", "w") as f:
    json.dump(config, f)
print("Config file created")