from encpp.encpp import *
import db_api as usscs
import json
"""
USSCS - Universal Server Side Chat System 
Version: 0.1.0 beta                             
Author: Tilman Kurmayer                   
License: only with permission from author 

Info: This file is the API for the USSCS
it`s the highest layer of the USSCS. It contains the dtabase API and allows you to create Software specific characteristics for users.
The USSCS datbase only needs a username and a password for each user. The USSCS API allows you to add more information to the user.
This information is NOT stored in the database. Every user has a JSON file in the users folder. This file contains the information.
To add more information to the user, you have to add it to the JSON schema. The JSON schema is a dictionary with the keys as the name of the information and the values as the default value.
To interact with the USSCS database, you have to add a user and then user_functions are available at usscs.user(username, password)!

The default user functions from usscs are:
    send message
    get message
    get unread

    add contact
    remove contact
    get contacts

    set privacy
    get privacy

    enable 2fa
    disable 2fa
    get 2fa

    delete account

    change password

    get all users

LAYER 3 and last LAYER
"""

__version__ = '0.1.0 beta'
__author__ = 'Tilman Kurmayer'


#Here you have to add the most code yourself! You can add more information to the user and give the function more arguments.
#Remember: The USSCS database only needs a username and a password for each user. The USSCS API for user is stored at usscs.user(username, password)!

folder_path = 'users/'
json_schema = {
} #you can add information to the user.

def add_user(username:str, password:str, public_key:rsa.PublicKey, private_key:rsa.PrivateKey, privacy:int=0, twofa:bool=False):
    """
    Add a user to the database.
    If two factor authentication is enabled, will return qrcode image.

    you can add more information to the user and give the function more arguments.
    """
    file_path = folder_path + username + '.json'
    json_schema = {}# you can add information to the user. example: json_schema = {'age': 0}

    return usscs.add_user(username, password, public_key, private_key, privacy, twofa)



