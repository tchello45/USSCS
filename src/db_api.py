from db_kernel import manage
from db_kernel import user as user_kernel
import qrcode
import rsa
"""
USSCS - Universal Server Side Chat System 
Version: 1.0.0                        
Author: Tilman Kurmayer                   
License: only with permission from author 
                                                 
Info: This file contains the API for the  
database                                  
for the USSCS                             
                                          
LAYER 2                                       
"""
__version__ = '1.0.0'
#without login:
class add_user:
    @staticmethod
    def add_user(username:str, password:str, public_key:rsa.PublicKey, private_key:rsa.PrivateKey, privacy:int=0, twofa:bool=False):
        """
        Add a user to the database.
        If two factor authentication is enabled, will return qrcode image.
        """
        return manage().add_user(username, password, public_key, private_key, privacy, twofa)

#with login:
class user:
    def __init__(self, username:str, passwort:str, twofa_key:str=None):
        self._user = user_kernel(username, passwort, twofa_key)
        self._manage = manage()
    
    def send_message(self, target:str, message:str, type:str='text'):
        """
        Send a message to a user.
        """
        return self._user.send_message(target, message, type)
    def get_messages(self, target:str, message_id:int=-1):
        """
        Get all messages from a user.
        id is the id of the last message you have.
        """
        return self._user.get_conversation(target, message_id)
    def get_users_with_unread_messages(self):
        """
        Get all users with unread messages.
        """
        return self._user.get_unread_messages()
    
    def add_contact(self, contact:str):
        """
        Add a contact.
        """
        return self._user.add_contact(contact)
    def remove_contact(self, contact:str):
        """
        Remove a contact.
        """
        return self._user.remove_contact(contact)
    def get_contacts(self):
        """
        Get all contacts.
        """
        return self._manage.get_contacts(self._user.username)
    
    def set_privacy(self, privacy:int):
        """
        Set privacy level.
        0: public
        1: contacts
        """
        return self._user.set_privacy(privacy)
    def get_privacy(self):
        """
        Get privacy level.
        0: public
        1: contacts
        """
        return self._user.privacy
    
    def enable_twofa(self) -> qrcode.image:
        """
        Enable two factor authentication.
        """
        return self._user.enable_2fa()
    def disable_twofa(self):
        """
        Disable two factor authentication.
        """
        return self._user.disable_2fa()
    def get_twofa(self):
        """
        Get two factor authentication status.
        """
        return self._user.is_2fa_enabled

    def delete_account(self):
        """
        Delete account.
        """
        return self._user.delete_account()
    
    def get_all_users(self):
        """
        Get all users.
        """
        return self._manage.get_all_users()
    
    def change_password(self, new_password:str):
        """
        Change password.
        """
        return self._user.change_password(new_password)
    
