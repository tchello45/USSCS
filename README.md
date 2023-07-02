# Universal Serverside Chat System (USSCS)   Version 3.0.0
Developed by Tilman Kurmayer

# Encrypted Chat System:
| Name: | Layer: | File: | Version: | Beta: | Description: |
|-------|--------|-------|----------|-------|--------------|
|  `db_kernel` | 1 | [enc_db_kernel.py](enc_db_kernel.py) | 3.0.0 | No | sqlite3 kernel to store messages and users |
| `db_api` | 2 | [enc_db_api.py](enc_db_api.py) | 3.0.0 | No | API for enc_db_kernel|

# Unencrypted Chat System:
| Name: | Layer: | File: | Version: | Beta: | Description: |
|-------|--------|-------|----------|-------|--------------|
| `db_kernel` | 1 | [db_kernel.py](db_kernel.py) | 3.0.0 | No | sqlite3 kernel to store messages and users |
| `db_api` | 2 | [db_api.py](db_api.py) | 3.0.0 | No | API for db_kernel|

# Python Packages:
| Name: | Version: |
|-------|----------|
| `usscs_enc` | 3.0.0 |
| `usscs` | 3.0.0 |
# In combination with:
`encpp` - encryption library for Python [encpp](https://github.com/tchello45/encpp) 
