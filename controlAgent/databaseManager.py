import os
import bcrypt
from peewee import *

class DatabaseManager:
    
    def __init__(self):
        """
        Initializes the class by setting up the database file, connecting to the database, 
        creating tables if they do not exist, and displaying the current state of the database.
        """
        self.DB_file = "controlAgent/users.db"
        self.db = SqliteDatabase(self.DB_file)
        self.initialize_database()
        self.show_database()
        
        
    def initialize_database(self):
        """
        Checks if the database file exists. If not, creates the necessary tables for users 
        and databases, then inserts a default user and associated databases.
        """
        if not os.path.exists(self.DB_file):
            self.db.connect()
            self.db.create_tables([User, Database])
            self.db.close()
            self.insert_users()
        
            
    def insert_users(self):
        """
        Inserts a default user with a hardcoded username and password into the database.
        Creates associated database entries for this user.
        """
        user_id = self.add_user('al', 'veryDifficultPass')
        if user_id:
            self.add_databases(user_id)
      
      
    def add_user(self, username, password):
        """
        Adds a new user to the database with a hashed password. 
        Returns the user ID if successful, or None if the username already exists.

        Args:
            username (str): The username of the user to be added.
            password (str): The password for the user, which will be hashed.

        Returns:
            int or None: The ID of the created user or None if the user already exists.
        """
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            self.db.connect()
            user = User.create(username=username, password=hashed_password)
            return user.id  
        except IntegrityError:
            print(f"El usuario '{username}' ya existe.")
            return None
        finally:
            self.db.close()
            
            
    def add_databases(self, user_id):
        """
        Adds default database entries associated with a given user ID.

        Args:
            user_id (int): The ID of the user to whom the databases will be associated.
        """
        db_entries = [
            {'idUser': user_id, 'idDB': '-1', 'numdb': 1},
            {'idUser': user_id, 'idDB': '-1', 'numdb': 2},
            {'idUser': user_id, 'idDB': '-1', 'numdb': 3}
        ]
        try:
            self.db.connect()
            with self.db.atomic():  
                for entry in db_entries:
                    Database.create(**entry)
        except Exception as e:
            print(f"An error occurred while adding databases: {e}")
        finally:
            self.db.close()
           
           
    ##Delete this func
    def create_containers(self, folder_name):
        """
        Deletes all files and directories within a specified folder and then recreates the folder.
        This method is currently marked for deletion and should not be used.

        Args:
            folder_name (str): The name of the folder to be cleared and recreated.
        """
        if os.path.exists(folder_name):
            for root, dirs, files in os.walk(folder_name, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(folder_name)
        os.makedirs(folder_name)
        
        
    def verify_user(self, username, password):
        """
        Verifies if a user exists in the database with the given username and password.
        Updates an internal dictionary with the user ID if verification is successful.

        Args:
            username (str): The username to verify.
            password (str): The password to verify.

        Returns:
            bool: True if the user exists and the password is correct, False otherwise.
        """
        try:
            self.db.connect()
            user = User.get(User.username == username)
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return True
        except User.DoesNotExist:
            pass
        finally:
            self.db.close()
        return False


    def update_databaseID(self, username: str, database_number : int, new_databaseID: str ): 
        """
        Updates the database ID associated with a specific user and database number.

        This method connects to the database, retrieves the user based on the provided username, 
        and then finds the database entry associated with the user's ID and the specified database number.
        It updates the `idDB` field of the database entry with the new database ID and saves the changes.

        Args:
            username (str): The username of the user whose database entry needs to be updated.
            database_number (int or str): The number of the database entry to be updated.
            new_databaseID (str): The new database ID to set for the specified database entry.

        Returns:
            bool: True if the update is successful, False if the user does not exist or an error occurs.
        """
        self.db.connect()
        try: 
            user = User.get(User.username == username)
            db = Database.get((Database.idUser == user.id) & (Database.numdb == database_number))
            db.idDB  = new_databaseID
            db.save()
            return True
        except User.DoesNotExist:
            return False 
        


    def show_database(self):
        """
        Displays all users and their associated database entries from the database.
        
        Returns:
            bool: True if users are found and displayed, False if an error occurs or no users are found.
        """
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
