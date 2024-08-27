import os
import bcrypt
from peewee import *

class DatabaseManager:
    
    def __init__(self):
        self.DB_file = "controlAgent/users.db"
        self.db = SqliteDatabase(self.DB_file)
        self.initialize_database()
        self.show_database()
        
    def initialize_database(self):
        if not os.path.exists(self.DB_file):
            self.db.connect()
            self.db.create_tables([User, Database])
            self.db.close()
            self.insert_users()
            
    def insert_users(self):
        self.add_user('al', 'veryDifficultPass')
      
    def add_user(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            self.db.connect()
            User.create(username=username, password=hashed_password)
        except IntegrityError:
            print(f"El usuario '{username}' ya existe.")
        finally:
            self.db.close()
            
    def create_containers(self, folder_name):
        if os.path.exists(folder_name):
            for root, dirs, files in os.walk(folder_name, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(folder_name)
        os.makedirs(folder_name)
        
    def verify_user(self, username, password):
        try:
            self.db.connect()
            user = User.get(User.username == username)
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                self.dict[username] = user.id
                return True
        except User.DoesNotExist:
            pass
        finally:
            self.db.close()
        return False

    def show_database(self):
        try:
            self.db.connect()
            # Obtener todos los usuarios
            users = User.select()
            if users:
                for user in users:
                    print(f"User ID: {user.id}, Username: {user.username}, Password: {user.password}")

                    # Obtener todas las bases de datos asociadas a este usuario
                    databases = user.databases.select()
                    if databases:
                        for db_entry in databases:
                            print(f"  Database ID: {db_entry.id}, idUser: {db_entry.idUser}, numdb: {db_entry.numdb}, idDB: {db_entry.idDB}")
                    else:
                        print("  No databases found for this user.")
                return True
            else:
                print("No users found in the database.")
                return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            self.db.close()
    
class BaseModel(Model):
    class Meta:
        database = SqliteDatabase("controlAgent/users.db")

class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()

class Database(BaseModel):
    idUser = ForeignKeyField(User, backref='databases')
    numdb = IntegerField()
    idDB = CharField()
