import hashlib
import rsa
import os
import sqlite3
import secrets
from datetime import datetime
import json
from encpp.encpp import *
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
        max_users = config["max_users"]
        db_folder = config["db_folder"]
    del config
    del f

else:
    max_users = 9000
    db_folder = "db/"
    if not os.path.exists(db_folder):
        os.mkdir(db_folder)
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
        for i in range(1, 1000000000000000):
            if user_db((username + str(i))).get_user_count() >= max_users:
                continue
            return (username + str(i))
        return ValueError("No free user_server_id found")
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
    def __init__(self) -> None:
        self.path = db_folder + "main.db"
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, server_id TEXT)")
        self.conn.commit()

    def add_user(self, username, server_id) -> None:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.c.fetchone() is not None:
            raise ValueError("User already exists")
        self.c.execute("INSERT INTO users VALUES (?, ?)", (username, server_id))
        self.conn.commit()
    def remove_user(self, username) -> None:
        self.c.execute("DELETE FROM users WHERE username=?", (username,))
        self.conn.commit()
    
    def get_user_server_id(self, username) -> str:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        return self.c.fetchone()[1]
    
    def get_all_users(self) -> list:
        self.c.execute("SELECT username FROM users")
        return self.c.fetchall()
    
    def exists(self, username) -> bool:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        return self.c.fetchone() is not None

class user_db:
    def __init__(self, server_id:str) -> None:
        self.server_id = server_id
        self.path = f"{db_folder}user_db/{server_id}.db"
        if not os.path.exists(db_folder + "user_db/"):
            os.mkdir(db_folder + "user_db/")
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, public_key TEXT, private_key BLOB, password_hash TEXT, salt TEXT, privacy INTEGER)")
        self.c.execute("CREATE TABLE IF NOT EXISTS contacts (username TEXT, contact TEXT)")
        self.c.execute("CREATE TABLE IF NOT EXISTS unread (username TEXT, sender TEXT)")
        self.conn.commit()
    def add_user(self, username:str, password:str, public_key:rsa.PublicKey, private_key:rsa.PrivateKey,  privacy:int=0) -> None: 
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha3_512(password.encode() + salt.encode()).hexdigest()
        public_key = public_key.save_pkcs1().decode()
        private_key = encpp.aes(password.encode()).encrypt(private_key.save_pkcs1())
        self.c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (username, public_key, private_key, password_hash, salt, privacy))
        self.conn.commit()
    def remove_user(self, username:str) -> None:
        self.c.execute("DELETE FROM users WHERE username=?", (username,))
        self.conn.commit()
    def get_user_count(self) -> int:
        self.c.execute("SELECT * FROM users")
        return len(self.c.fetchall())
    def get_user(self, username:str) -> tuple:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        return user
    def get_user_public_key(self, username:str) -> rsa.PublicKey:
        self.c.execute("SELECT public_key FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        return rsa.PublicKey.load_pkcs1(user[0].encode())
    def get_user_private_key(self, username:str, password:str) -> rsa.PrivateKey:
        self.c.execute("SELECT private_key, salt FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        return rsa.PrivateKey.load_pkcs1(encpp.aes(password.encode()).decrypt(user[0]))
    
    def get_user_privacy(self, username:str) -> int:
        self.c.execute("SELECT privacy FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        return user[0]
    def set_user_privacy(self, username, privacy) -> None:
        self.c.execute("SELECT privacy FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        self.c.execute("UPDATE users SET privacy=? WHERE username=?", (privacy, username))
        self.conn.commit()

    def get_contacts(self, username:str) -> list:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        self.c.execute("SELECT contact FROM contacts WHERE username=?", (username,))
        return self.c.fetchall()
    def add_contact(self, username:str, contact:str) -> None:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        if main_db().exists(contact) is False:
            raise ValueError("Contact does not exist")
        self.c.execute("INSERT INTO contacts VALUES (?, ?)", (username, contact))
        self.conn.commit()
    def remove_contact(self, username:str, contact:str) -> None:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        if main_db().exists(contact) is False:
            raise ValueError("Contact does not exist")
        self.c.execute("DELETE FROM contacts WHERE username=? AND contact=?", (username, contact))
        self.conn.commit()
    def is_contact(self, username:str, contact:str) -> bool:
        self.c.execute("SELECT * FROM contacts WHERE username=? AND contact=?", (username, contact))
        return self.c.fetchone() is not None
    
    def get_unread(self, username:str) -> list:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        self.c.execute("SELECT sender FROM unread WHERE username=?", (username,))
        return self.c.fetchall()
    def add_unread(self, username:str, sender:str) -> None:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        if main_db().exists(sender) is False:
            raise ValueError("Sender does not exist")
        self.c.execute("INSERT INTO unread VALUES (?, ?)", (username, sender))
        self.conn.commit()
    def remove_unread(self, username:str, sender:str) -> None:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        if main_db().exists(sender) is False:
            raise ValueError("Sender does not exist")
        self.c.execute("DELETE FROM unread WHERE username=? AND sender=?", (username, sender))
        self.conn.commit()
    def auth(self, username:str, password:str) -> bool:
        self.c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.c.fetchone()
        if user is None:
            raise ValueError("User does not exist")
        password_hash = hashlib.sha3_512(password.encode() + user[4].encode()).hexdigest()
        return password_hash == user[3]
class direct_db:
    def __init__(self, username:str, target:str, password:str) -> None:
        self.password = password
        self.server_id = id_generators.direct_server_id(username, target)
        self.username = username
        self.target = target
        if not main_db().exists(self.target) or not main_db().exists(self.username):
            raise ValueError("User does not exist")
        self.id_user = main_db().get_user_server_id(self.username)
        self.id_target = main_db().get_user_server_id(self.target)
        self.path = f"{db_folder}direct_db/{self.server_id}.db"
        if not os.path.exists(db_folder + "direct_db/"):
            os.mkdir(db_folder + "direct_db/")
        self.conn = sqlite3.connect(self.path)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS messages (message_id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, enc_for_sender BLOB, enc_for_receiver BLOB, timestamp TEXT, is_read BOOL, message_type TEXT)")
        self.conn.commit()
    def send_message(self, message:str, type:str="text"):      
        contact_privacy = user_db(self.id_target).get_user_privacy(self.target)
        if contact_privacy != 0 and user_db(self.id_target).is_contact(self.target, self.username) is False:
                raise ValueError("Privacy error")
        pub_username, pub_target = user_db(self.id_user).get_user_public_key(self.username), user_db(self.id_target).get_user_public_key(self.target)
        enc_for_sender, enc_for_receiver = encpp.rsa.encrypt(pub_username, message.encode()), encpp.rsa.encrypt(pub_target, message.encode())
        time = datetime.now().strftime("%H:%M %d/%m/%y")
        self.c.execute("INSERT INTO messages VALUES (NULL, ?, ?, ?, ?, ?, ?)", (self.username, enc_for_sender, enc_for_receiver,  time, False, type))
        self.conn.commit()
        user_db(self.id_target).add_unread(self.target, self.username)
        return self.c.lastrowid # alternatively, return self.c.execute("SELECT message_id FROM messages WHERE sender=? AND enc_for_sender=? AND enc_for_receiver=? AND timestamp=?", (username, enc_for_sender, enc_for_receiver, time)).fetchone()[0]
    def get_conversation(self, _id:int=-1):
        self.c.execute("SELECT * FROM messages WHERE  message_id >= ?", (_id,))
        messages = self.c.fetchall()
        private_key = user_db(self.id_user).get_user_private_key(self.username, self.password)
        conversation = []
        for i in messages:
            id_ = i[0]
            sender = i[1]
            enc_for_sender = i[2]
            enc_for_receiver = i[3]
            timestamp = i[4]
            is_read = i[5]
            message_type = i[6]
            if sender == self.username:
                message = encpp.rsa().decrypt(private_key, enc_for_sender).decode()
            else:
                message = encpp.rsa().decrypt(private_key, enc_for_receiver).decode()
                self.c.execute("UPDATE messages SET is_read=? WHERE message_id=?", (True, id_))
                self.conn.commit()
            mes_dict = {
                "id": id_,
                "sender": sender,
                "message": message,
                "timestamp": timestamp,
                "is_read": is_read,
                "message_type": message_type
            }
            conversation.append(mes_dict)
        self.c.execute("UPDATE messages SET is_read=? WHERE sender=? AND is_read=?", (True, self.target, False))
        self.conn.commit()
        user_db(self.id_target).remove_unread(self.target, self.username)
        return conversation
    def get_unread_messages(self):
        messages = self.c.execute("SELECT * FROM messages WHERE sender=? AND is_read=?", (self.target, False)).fetchall()
        private_key = user_db(self.id_user).get_user_private_key(self.username, self.password)
        conversation = []
        for i in messages:
            id_ = i[0]
            sender = i[1]
            enc_for_sender = i[2]
            enc_for_receiver = i[3]
            timestamp = i[4]
            is_read = i[5]
            message_type = i[6]
            if sender == self.username:
                message = encpp.rsa().decrypt(private_key, enc_for_sender).decode()
            else:
                message = encpp.rsa().decrypt(private_key, enc_for_receiver).decode()
            mes_dict = {
                "id": id_,
                "sender": sender,
                "message": message,
                "timestamp": timestamp,
                "is_read": is_read,
                "message_type": message_type
            }
            conversation.append(mes_dict)
        self.c.execute("UPDATE messages SET is_read=? WHERE sender=? AND is_read=?", (True, self.target, False))
        self.conn.commit()
        user_db(self.id_target).remove_unread(self.target, self.username)
        return conversation

def add_user(username:str, password:str, public_key:rsa.PublicKey, private_key:rsa.PrivateKey,  privacy:int=0):
    invalid_chars = [" ", "!", "?", ".", ",", ":", ";", "'", '"', "(", ")", "[", "]", "{", "}", "/", "\\", "|", "<", ">", "+", "-", "*", "=", "~", "`", "@", "#", "$", "%", "^", "&"]
    for i in invalid_chars:
        if i in username:
            raise ValueError("Invalid username")
    server_id = id_generators.user_server_id(username)
    if main_db().exists(username):
        raise ValueError("User already exists")
    main_db().add_user(username, server_id)
    user_db(server_id).add_user(username, password, public_key, private_key, privacy)
def remove_user(username:str):
    user_id = main_db().get_user_server_id(username)
    main_db().remove_user(username)
    user_db(user_id).remove_user(username)
    if user_db(user_id).get_user_count() == 0:
        os.remove(db_folder + "user_db/" + user_id + ".db")
    import glob
    for i in glob.glob(db_folder + "direct_db/*.db"):
        if i.split("/")[-1].split(".")[0].split("!")[0] == username or i.split("/")[-1].split(".")[0].split("!")[1] == username:
            os.remove(i)
    
