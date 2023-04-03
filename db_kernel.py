#############################################
# USSCS - Universal Server Side Chat System #
# Version: 0.1.0                            #
# Author: Tilman Kurmayer                   #
# License: only with permission from author #
#                                           #       
# Info: This file contains the database     #
# This file contains the database kernel    #
# for the USSCS                             #
#                                           #
# LAYER 1                                   #
#############################################           
import hashlib
import rsa
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import os
import sqlite3
import secrets
from datetime import datetime
import pyotp
import qrcode
import json
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
        max_users = config["max_users"]
        rsa_key_size = config["rsa_key_size"]
    del config
    del f

else:
    max_users = 9000
    rsa_key_size = 512
"""
Username: min 3, no spaces, no special characters
privacy: 0 for public, 1 only contacts everbody can see me
only manage and user should be used from external files
"""

def fill_password(password:bytes) -> bytes:
    return password + b" " * (32 - len(password))

class encpp:
    class aes:
        def __init__(self, key:bytes) -> None:
            self.key = fill_password(key)
        # Encrypts data
        def encrypt(self, data:bytes)-> bytes:
            cipher = AES.new(self.key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(data, AES.block_size))
            iv = cipher.iv
            return iv + ct_bytes
        # Decrypts data
        def decrypt(self, data:bytes)-> bytes:
            iv = data[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            pt = unpad(cipher.decrypt(data[AES.block_size:]), AES.block_size)
            return pt
    class rsa:
        @staticmethod
        def encrypt(public_key:rsa.PublicKey, data:bytes) -> bytes:
            aes_key = os.urandom(32)
            enc = encpp.aes(aes_key).encrypt(data)
            return rsa.encrypt(aes_key, public_key) + "sep".encode() + enc
        @staticmethod
        def decrypt(private_key:rsa.PrivateKey, data:bytes) -> bytes:
            aes_key, enc = data.split("sep".encode())
            aes_key = rsa.decrypt(aes_key, private_key)
            return encpp.aes(aes_key).decrypt(enc)

class id_generators:
    @staticmethod
    def user_server_id(username:str) -> str:
        """
        username: Username of the user
        Generates a user_server_id for a username
        """
        for index in range(len(username)):
            if username[:index] == "" or user_db(username[:index]).get_user_count() >= max_users:
                continue
            return username[:index]
    @staticmethod
    def direct_server_id(username0:str, username1:str) -> str:
        """
        username0: Username of the first user
        username1: Username of the second user
        Generates a direct_server_id for two usernames
        """
        if username0 > username1:
            username0, username1 = username1, username0

        return username0 + "!" + username1



class main_db:
    def __init__(self, path:str="main.db") -> None:
        """Path: Path to the main database"""
        self.path = path
        self.conn = sqlite3.connect(path)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, server_id TEXT)")
        self.conn.commit()
    def add_user(self, username:str, server_id:str):
        """
        username: Username of the user
        server_id: Id of the user server
        Adds a user to the main database
        Important: This method does not create a user server
        """
        #check if the user already exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is not None:
            raise ValueError("User already exists")
        self.c.execute("INSERT INTO users VALUES (?, ?)", (username, server_id))
        self.conn.commit()
    def get_user_server_id(self, username:str) -> str:
        """
        username: Username of the user
        Returns the server_id of the user server
        """
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        self.c.execute("SELECT server_id FROM users WHERE username=?", (username,))
        return self.c.fetchone()[0]
    def exists(self, username:str) -> bool:
        """
        username: Username of the user
        Returns True if the user exists, False otherwise
        """
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        return self.c.fetchone() is not None
class user_db:
    def __init__(self, server_id:str) -> None:
        """
        server_id: Id of the current user server
        """
        self.server_id = server_id
        self.path = f"{server_id}.db"
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, public_key TEXT, private_key BLOB, password_hash TEXT, salt TEXT, privacy INTEGER, is_2fa_enabled BOOL, twofa_key TEXT)")
        self.c.execute("CREATE TABLE IF NOT EXISTS contacts (username TEXT, contact TEXT)")
        self.c.execute("CREATE TABLE IF NOT EXISTS unread (username TEXT, sender TEXT)")
        self.conn.commit()
    def add_user(self, username:str, password:str, privacy:int=0, is_2fa_enabled:bool=False):
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha3_512(password.encode() + salt.encode()).hexdigest()
        public_key, private_key = rsa.newkeys(rsa_key_size)
        public_key = public_key.save_pkcs1().decode()
        private_key = encpp.aes(password.encode()).encrypt(private_key.save_pkcs1())
        if is_2fa_enabled:
            twofa_key = pyotp.random_base32(length=128) # Normally 32, but 128 is better
        else:
            twofa_key = None
        self.c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (username, public_key, private_key, password_hash, salt, privacy, is_2fa_enabled, twofa_key))
        self.conn.commit()
        if is_2fa_enabled:
            return twofa_key
    def get_2fa(self, username:str) -> tuple:
        self.c.execute("SELECT is_2fa_enabled, twofa_key FROM users WHERE username=?", (username,))
        is_2fa_enabled = self.c.fetchone()[0]
        if is_2fa_enabled:
            twofa_key = self.c.fetchone()[1]
        else:
            twofa_key = None
        return is_2fa_enabled, twofa_key
    def get_user_count(self):
        self.c.execute("SELECT COUNT(*) FROM users")
        return self.c.fetchone()[0]
    def get_user(self, username:str):
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        return user
    def get_user_public_key(self, username:str) -> rsa.PublicKey:
        #check if the user exists
        self.c.execute("SELECT public_key FROM users WHERE username=?", (username,))
        public_key = self.c.fetchone()
        if public_key is None:
            raise ValueError("User does not exist")
        return rsa.PublicKey.load_pkcs1(public_key[0].encode())
    def get_user_private_key(self, username:str, password:str) -> rsa.PrivateKey:
        #check if the user exists
        self.c.execute("SELECT private_key, salt FROM users WHERE username=?", (username,))
        private_key, salt = self.c.fetchone()
        if private_key is None:
            raise ValueError("User does not exist")
        private_key = encpp.aes(password.encode()).decrypt(private_key)
        return rsa.PrivateKey.load_pkcs1(private_key)
    def get_user_privacy(self, username:str) -> int:
        #check if the user exists
        self.c.execute("SELECT privacy FROM users WHERE username=?", (username,))
        privacy = self.c.fetchone()
        if privacy is None:
            raise ValueError("User does not exist")
        return privacy[0]
    def set_user_privacy(self, username:str, privacy:int) -> None:
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        self.c.execute("UPDATE users SET privacy=? WHERE username=?", (privacy, username))
        self.conn.commit()
    def get_contacts(self, username:str) -> list:
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        self.c.execute("SELECT contact FROM contacts WHERE username=?", (username,))
        return [i[0] for i in self.c.fetchall()]
    def add_contact(self, username:str, contact:str) -> None:
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        #check if the contact exists
        self.c.execute("SELECT * FROM users WHERE username=?", (contact,))
        if self.c.fetchone() is None:
            raise ValueError("Contact does not exist")
        self.c.execute("INSERT INTO contacts VALUES (?, ?)", (username, contact))
        self.conn.commit()
    def remove_contact(self, username:str, contact:str) -> None:
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        #check if the contact exists
        self.c.execute("SELECT * FROM users WHERE username=?", (contact,))
        if self.c.fetchone() is None:
            raise ValueError("Contact does not exist")
        self.c.execute("DELETE FROM contacts WHERE username=? AND contact=?", (username, contact))
        self.conn.commit()
    def add_unread(self, username:str, sender:str):
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        self.c.execute("INSERT INTO unread VALUES (?, ?)", (username, sender))
        self.conn.commit()
    def set_read(self, username:str, sender:str):
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        self.c.execute("DELETE FROM unread WHERE username=? AND sender=?", (username, sender))
        self.conn.commit()
    def get_unread(self, username:str) -> list:
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        self.c.execute("SELECT sender FROM unread WHERE username=?", (username,))
        return [i[0] for i in self.c.fetchall()]
    def enable_2fa(self, username:str, password:str):
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        #check if 2fa is already enabled
        self.c.execute("SELECT * FROM users WHERE username=? AND two_factor_auth=?", (username, 1))
        if self.c.fetchone() is not None:
            raise ValueError("2FA is already enabled")
        #generate a secret
        two_fa_key = pyotp.random_base32(length=128)
        self.conn.execute("UPDATE users SET two_factor_auth=?, two_factor_auth_key=? WHERE username=?", (1, two_fa_key, username))
        self.conn.commit()
        return two_fa_key
    def disable_2fa(self, username:str, password:str):
        #check if the user exists
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is None:
            raise ValueError("User does not exist")
        #check if 2fa is already disabled
        self.c.execute("SELECT * FROM users WHERE username=? AND two_factor_auth=?", (username, 0))
        if self.c.fetchone() is not None:
            raise ValueError("2FA is already disabled")
        self.conn.execute("UPDATE users SET two_factor_auth=?, two_factor_auth_key=? WHERE username=?", (0, "", username))
        self.conn.commit()
class direct_db:
    def __init__(self, server_id:str) -> None:
        """
        server_id: Id of the current direct server
        """
        self.server_id = server_id
        self.path = f"{server_id}.db"
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS messages (message_id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, enc_for_sender BLOB, enc_for_receiver BLOB, timestamp TEXT, is_read BOOL, message_type TEXT)")
        self.conn.commit()
    def send_message(self, username:str, target:str, message:str, type:str="text"):    
        """
        username: Username of the sender
        target: Username of the receiver
        message: Message to send
        type: Type of the message
        Sends a message to a user"""
        #check if the users exist
        if not main_db().exists(target) or not main_db().exists(username):
            raise ValueError("User does not exist")        
        contact_privacy = manage().get_user_privacy(target)
        if contact_privacy >= 1:
            if not manage().check_contact(target, username):
                raise ValueError("Privacy error")
        elif contact_privacy == 0:
            pass
        #send the message
        public_key = manage().get_user_public_key(username)
        enc_for_sender = encpp.rsa().encrypt(public_key, message.encode())
        enc_for_receiver = encpp.rsa().encrypt(manage().get_user_public_key(target), message.encode())
        self.c.execute("INSERT INTO messages VALUES (NULL, ?, ?, ?, ?, ?, ?)", (username, enc_for_sender, enc_for_receiver,  datetime.now().strftime("%H:%M %d/%m/%y"), False, type))
        self.conn.commit()
        #set the unread message
        user_db(main_db().get_user_server_id(target)).add_unread(target, username)

    def get_conversation(self, username:str, target:str, password:str, id:int=-1):
        """
        username: Username of the current user
        target: Username of the other user
        password: Password of the current user
        id: Id of the message to start from if -1 it will return all the messages
        return a list of messages: [message_id, sender, message, timestamp, is_read, message_type]
        """
        #check if the users exist
        if not main_db().exists(target) or not main_db().exists(username):
            raise ValueError("User does not exist")
        if id == -1:
            self.c.execute("SELECT * FROM messages")
        else:
            self.c.execute("SELECT * FROM messages WHERE  message_id > ?", (id))
        messages = self.c.fetchall()
        #decrypt the messages
        private_key = manage().get_user_private_key(username, password)
        new_messages = []
        for i in messages:
            sender = i[1]
            enc_for_sender = i[2]
            enc_for_receiver = i[3]
            timestamp = i[4]
            is_read = i[5]
            message_type = i[6]
            if sender == username:
                message = encpp.rsa().decrypt(private_key, enc_for_sender)
            else:
                message = encpp.rsa().decrypt(private_key, enc_for_receiver)
                self.c.execute("UPDATE messages SET is_read=? WHERE message_id=?", (True, i[0]))
                self.conn.commit()
            new_messages.append((sender, message, timestamp, is_read, message_type))
        #set the messages as read
        user_db(main_db().get_user_server_id(target)).set_read(target, username)
        return new_messages

class manage:
    def __init__(self, main_db_path:str="main.db") -> None:
        """
        main_db_path: Path to the main database
        This class manages all the databases
        It is used to add users, contacts, messages, etc.
        """
        self.main_db = main_db(main_db_path)
    
    def add_user(self, username:str, password:str, twofa:bool=False) -> qrcode.make or None:
        """
        username: Username of the user
        password: Password of the user
        Adds a user to the database
        if twofa is True it will return a qrcode image
        """
        server_id = id_generators.user_server_id(username)
        self.main_db.add_user(username, server_id)
        if twofa:
            key = user_db(server_id).add_user(username, password, is_2fa_enabled=twofa) # TODO That's not logical. You generate the 2fa key and don't use it. In the user_db() you generate a new 2fa key. You should use the same key, because the one key is only for the qrcode and the other in the database.
            #generate the qr code
            uri = pyotp.totp.TOTP(key).provisioning_uri(username, issuer_name="Cyat")
            img = qrcode.make(uri)
            return img
        else:
            user_db(server_id).add_user(username, password)
    def get_user(self, username:str) -> tuple:
        """
        username: Username of the user
        Returns the user data
        structure: (username, public_key, private_key, password_hash, salt, privacy, is_2fa_enabled, twofa_key)
        """
        return user_db(self.main_db.get_user_server_id(username)).get_user(username)    
    def get_user_public_key(self, username:str) -> rsa.PublicKey:	
        """
        username: Username of the user
        Returns the user's public key
        """
        return user_db(self.main_db.get_user_server_id(username)).get_user_public_key(username)
    def get_user_private_key(self, username:str, password:str) -> rsa.PrivateKey:
        """
        username: Username of the user
        password: Password of the user
        Returns the user's private key
        """
        return user_db(self.main_db.get_user_server_id(username)).get_user_private_key(username, password)
    def get_user_privacy(self, username:str) -> int:
        """
        username: Username of the user
        Returns the user's privacy level
        """
        return user_db(self.main_db.get_user_server_id(username)).get_user_privacy(username)
    def check_contact(self, username:str, contact:str) -> bool:
        """
        username: Username of the user
        contact: Username of the contact
        Returns True if the contact exists
        """
        return contact in self.get_contacts(username)
    def get_contacts(self, username:str) -> list:
        """
        username: Username of the user
        Returns the list of contacts
        """
        return user_db(self.main_db.get_user_server_id(username)).get_contacts(username)
class user:
    def __init__(self, username:str, password:str, twofa_code=None):
        """
        username: Username of the user
        password: Password of the user
        """
        self.username = username
        self.password = password
        self.main_db = main_db()
        self.user_db = user_db(self.main_db.get_user_server_id(username))
        self.user_data = self.user_db.get_user(username)
        self.public_key = rsa.PublicKey.load_pkcs1(self.user_data[1].encode())  
        self.password_hash = self.user_data[3]
        self.salt = self.user_data[4]
        if not hashlib.sha3_512((password + self.salt).encode()).hexdigest() == self.password_hash:
            raise ValueError("Password is incorrect")
        self.private_key = rsa.PrivateKey.load_pkcs1(encpp.aes(self.password.encode()).decrypt(self.user_data[2]))
        self.privacy = self.user_data[5]
        self.is_2fa_enabled = self.user_data[6]
        self.twofa_key = self.user_data[7]
        self.contacts = self.user_db.get_contacts(username)
        if self.is_2fa_enabled:
            if not twofa_code:
                raise ValueError("2FA is enabled")
            if not self.check_twofa(twofa_code):
                raise ValueError("2FA code is invalid")

    def check_twofa(self, code:str) -> bool:
        """
        code: 2FA code
        Returns True if the code is valid
        """
        totp = pyotp.TOTP(self.twofa_key)
        return totp.verify(code)
        
    def send_message(self, target:str, message:str):
        """
        target: Username of the target
        message: Message to be sent
        Sends a message to the target if the privacy level allows it
        privacy level 0: Anyone can send messages
        privacy level 1: Only contacts can send messages
        """
        direct = direct_db(id_generators.direct_server_id(self.username, target))
        direct.send_message(self.username, target, message)
    def get_conversation(self, target:str, id:int=-1) -> list:
        """
        target: Username of the target
        id: Id of the message to start from if -1 it will return all the messages
        Returns the conversation with the target
        return a list of messages: [message_id, sender, message, timestamp, is_read, message_type]
        the message is in bytes format but its decrypted
        """
        direct = direct_db(id_generators.direct_server_id(self.username, target))
        return direct.get_conversation(self.username, target, self.password, id)
    def set_privacy(self, privacy:int):
        """
        privacy: Privacy level
        Sets the privacy level
        """
        self.user_db.set_user_privacy(self.username, privacy)
        self.privacy = privacy
    def enable_2fa(self) -> qrcode.make:
        """
        Enables 2FA
        """
        key = self.user_db.enable_2fa(self.username, self.password)
        self.is_2fa_enabled = True
        uri = pyotp.totp.TOTP(key).provisioning_uri(self.username, issuer_name="Cyat")
        img = qrcode.make(uri)
        return img
    def disable_2fa(self, code:str):
        """
        code: 2FA code
        Disables 2FA
        """
        if not self.check_twofa(code):
            raise ValueError("2FA code is invalid")
        self.user_db.disable_2fa(self.username, self.password)
        self.is_2fa_enabled = False
    def add_contact(self, contact:str):
        """
        contact: Username of the contact
        Adds a contact
        """
        self.user_db.add_contact(self.username, contact)
        self.contacts.append(contact)
    def remove_contact(self, contact:str):
        """
        contact: Username of the contact
        Removes a contact
        """
        self.user_db.remove_contact(self.username, contact)
        self.contacts.remove(contact)
        
