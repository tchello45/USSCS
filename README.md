# Universal Serverside Chat System (USSCS)   Version 3.0.3
Developed by Tilman Kurmayer

# Encrypted Chat System:
| Name: | Layer: | File: | Version: | Beta: | Description: |
|-------|--------|-------|----------|-------|--------------|
|  `db_kernel` | 1 | [enc_db_kernel.py](enc_db_kernel.py) | 3.0.3 | No | sqlite3 kernel to store messages and users |
| `db_api` | 2 | [enc_db_api.py](enc_db_api.py) | 3.0.3 | No | API for enc_db_kernel|

# Unencrypted Chat System:
| Name: | Layer: | File: | Version: | Beta: | Description: |
|-------|--------|-------|----------|-------|--------------|
| `db_kernel` | 1 | [db_kernel.py](db_kernel.py) | 3.0.3 | No | sqlite3 kernel to store messages and users |
| `db_api` | 2 | [db_api.py](db_api.py) | 3.0.3 | No | API for db_kernel|

# Python Packages:
| Name: | Version: |
|-------|----------|
| `usscs_enc` | 3.0.3 |
| `usscs` | 3.0.3 |
# In combination with:
`encpp` - encryption library for Python [encpp](https://github.com/tchello45/encpp) 

# Versioning:
Since Version 3.0.0 the versioning is based on the following scheme:
x.y.z
x: Major Version (new features, new API, new encryption) significant changes -> frontend code has to be heavily modified - Not Always Stable Version
y: Minor Version (new features, new API, new encryption) minor changes stable version of a patch version -> frontend code has to be modified - Stable Version
z: Patch Version (bug fixes, new features, new API, new encryption) -> frontend code has to be modified - Non Stable Version