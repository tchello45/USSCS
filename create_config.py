import json
import os
max_users = input("Enter the maximum number of users: ")
max_users = int(max_users)
rsa_key_size = input("Enter the RSA key size: (512 low secure, 2048 medium secure, 4096 high secure) ")
rsa_key_size = int(rsa_key_size)
if rsa_key_size not in [512, 2048, 4096]:
    print("Invalid RSA key size")
    exit()
config = {
    "max_users": max_users,
    "rsa_key_size": rsa_key_size
}
if os.path.exists("config.json"):
    print("Config file already exists")
    exit()
with open("config.json", "w") as f:
    json.dump(config, f)
print("Config file created")