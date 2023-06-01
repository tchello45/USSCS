from encpp.encpp import *
from db_api import add_user as usscs_add_user
from db_api import user as usscs_user
from db_api import exists as usscs_exists
"""
USSCS - Universal Server Side Chat System 
Version: 1.0.2                         
Author: Tilman Kurmayer                   
License: only with permission from author 

Info: This file is the API for the USSCS
it`s the highest layer of the USSCS. It contains the dtabase API and allows you to create Software specific characteristics for users.
The USSCS datbase only needs a username and a password for each user. The USSCS API allows you to add more information to the user.
This information is NOT stored in the database.
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
__version__ = "1.0.2"
class add_user(usscs_add_user):
    pass
class exists(usscs_exists):
    pass
class user(usscs_user):
    pass
