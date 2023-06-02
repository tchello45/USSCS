# Universal Serverside Chat System (USSCS)   Version 1.0.4
Developed by Tilman Kurmayer

# Construction:
| Name: | Layer: | File: | Version: | Beta: | Description: |
|-------|--------|-------|----------|-------|--------------|
|  `db_kernel` | 1 | [db_kernel.py](db_kernel.py) | 1.0.4 | No | sqlite3 kernel to store messages and users |
| `db_api` | 2 | [db_api.py](db_api.py) | 1.0.3 | No | API for db_kernel|
| `usscs_api` | 3 | [usscs_api.py](usscs_api.py) | 1.0.3 | No | API for usscs_kernel LAST LAYER |



# In combination with:
`encpp` - encryption library for Python [encpp](https://github.com/tchello45/encpp) 
