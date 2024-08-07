import sqlite3
import os 
import uuid
import bcrypt

class DatabaseManager:
    
    def __init__(self): 
        self.DB_file = "controlAgent/users.db"
        self.dict = dict()
        result = self.verify_user("al", "veryDifficultPass")
        print (result)
        
    def initialize_database(self):
        db_filename = self.DB_file
        CREATE_TABLE_QUERY = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                data_address TEXT NOT NULL
            );
        """
        if not os.path.exists(db_filename):
            conn = sqlite3.connect(db_filename)
            cursor = conn.cursor()
            cursor.execute(CREATE_TABLE_QUERY)
            conn.commit()
            conn.close()
            self.insert_users()
        
    def insert_users(self):
        personal_path = str(uuid.uuid4())
        personal_path = os.path.join("controlAgent","databases" ,personal_path)
        self.add_user('al', 'veryDifficultPass', personal_path)
        self.create_containers(personal_path)
        
        
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
        conn = sqlite3.connect(self.DB_file)
        cursor = conn.cursor()

        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        conn.close()
        if row:
            user_id, stored_password = row
            # Verifica la contraseña usando bcrypt
            if bcrypt.checkpw(password.encode(), stored_password):
                self.dict[username] = user_id
                return True
        return False

    def add_user(self, username, password, data_address):
        try:
            conn = sqlite3.connect(self.DB_file)
            cursor = conn.cursor()
            # Hashea la contraseña antes de almacenarla
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            cursor.execute("INSERT INTO users (username, password, data_address) VALUES (?, ?, ?)", 
                        (username, hashed_password, data_address))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"An error occurred while adding a user: {e}")
            return False
        
    def print_all_database(self):
        try:
            conn = sqlite3.connect(self.DB_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, username, password, data_address FROM users")
            rows = cursor.fetchall()
            
            conn.close()
            
            if rows:
                for row in rows:
                    user_id, username, password, data_address = row
                    print(f"ID: {user_id}, Username: {username}, Password: {password}, Data Address: {data_address}")
                return True
            else:
                print("No users found in the database.")
                return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False