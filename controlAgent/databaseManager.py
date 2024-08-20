import sqlite3
import os 
import bcrypt

#Classe pour gérer la base de données
class DatabaseManager:
    #Constructeur
    def __init__(self): 
        self.DB_file = "controlAgent/users.db"
        self.dict = dict()
        self.initialize_database()    
        
    #Fonction pour initialiser la base de données   
    def initialize_database(self):
        db_filename = self.DB_file
        CREATE_USERS_TABLE_QUERY = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        """
        
        CREATE_DATABASES_TABLE_QUERY = """
            CREATE TABLE IF NOT EXISTS databases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idUser INTEGER,
                numdb INTEGER,
                idDB TEXT,
                FOREIGN KEY(idUser) REFERENCES users(id)
            );
        """
        
        if not os.path.exists(db_filename):
            conn = sqlite3.connect(db_filename)
            cursor = conn.cursor()
            cursor.execute(CREATE_USERS_TABLE_QUERY)
            cursor.execute(CREATE_DATABASES_TABLE_QUERY)
            conn.commit()
            conn.close()
            self.insert_users()
        
    #méthode pour insérer de nouveaux utilisateurs (comme ils ne connaissent rien aux mots de passe, je les définis en leur nom)
    def insert_users(self):
        self.add_user('al', 'veryDifficultPass')
      
    #méthode pour créer des conteneurs
    def create_containers(self, folder_name):
        if os.path.exists(folder_name):
            for root, dirs, files in os.walk(folder_name, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(folder_name)
        os.makedirs(folder_name)
        
    #méthode pour vérifier un utilisateur (par exemple, en utilisant le nom d'utilisateur "; DROP TABLE Users" sans virgules, il renvoie false)
    def verify_user(self, username, password):
        conn = sqlite3.connect(self.DB_file)
        cursor = conn.cursor()

        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        conn.close()
        if row:
            user_id, stored_password = row
            if bcrypt.checkpw(password.encode(), stored_password):
                self.dict[username] = user_id
                return True
        return False

    #méthode pour ajouter un utilisateur
    def add_user(self, username, password):
        try:
            conn = sqlite3.connect(self.DB_file)
            cursor = conn.cursor()
            
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                           (username, hashed_password))
            
            user_id = cursor.lastrowid
            
            for numdb in range(1, 4):
                cursor.execute("INSERT INTO databases (idUser, numdb, idDB) VALUES (?, ?, NULL)", 
                               (user_id, numdb))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"An error occurred while adding a user: {e}")
            return False
        
    #méthode pour afficher la base de données
    def show_database(self):
        try:
            conn = sqlite3.connect(self.DB_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, username, password FROM users")
            users = cursor.fetchall()
            
            if users:
                for user in users:
                    user_id, username, password = user
                    print(f"User ID: {user_id}, Username: {username}, Password: {password}")
                    
                    cursor.execute("SELECT id, idUser, numdb, idDB FROM databases WHERE idUser = ?", (user_id,))
                    databases = cursor.fetchall()
                    
                    if databases:
                        for db_entry in databases:
                            db_id, idUser, numdb, idDB = db_entry
                            print(f"  Database ID: {db_id}, idUser: {idUser}, numdb: {numdb}, idDB: {idDB}")
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
            if conn:
                conn.close()