import db_kernel
from db_kernel import add_user
from db_kernel import remove_user
__name__ = "db_api"
__version__ = "3.0.3"
__author__ = "Tilman Kurmayer"
class user:
    def __init__(self, username:str, password:str, path:str):
        if not db_kernel.main_db(path).exists(username):
            raise Exception("User does not exist")
        self.username = username
        self.password = password
        self.path = path
        self.user_obj = db_kernel.user_db(db_kernel.main_db(path).get_user_server_id(username), path)
        if not self.user_obj.auth(username, password):
            raise Exception("Invalid password")
    def send_message(self, target:str, message:str, mes_type:str="text"):
        return db_kernel.direct_db(self.username, target, self.password, self.path).send_message(message, mes_type)
    def get_conversation(self, target:str, _id=-1):
        return db_kernel.direct_db(self.username, target, self.password, self.path).get_conversation(_id)
    def get_unread_messages(self, target:str):
        return db_kernel.direct_db(self.username, target, self.password, self.path).get_unread_messages()
    def get_unread_users(self):
        return self.user_obj.get_unread(self.username)
    def get_all_users(self):
        return db_kernel.main_db(self.path).get_all_users()
    def get_contacts(self):
        return self.user_obj.get_contacts()
    def add_contact(self, target:str):
        self.user_obj.add_contact(target)
    def remove_contact(self, target:str):
        self.user_obj.remove_contact(target)
    def get_privacy(self):
        return self.user_obj.get_user_privacy(self.username)
    def set_privacy(self, privacy:int):
        if privacy not in [0, 1]:
            raise Exception("Invalid privacy setting")
        self.user_obj.set_user_privacy(self.username, privacy)