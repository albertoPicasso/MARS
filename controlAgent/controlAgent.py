from flask import Flask, request,jsonify, abort, make_response
from databaseManager import DatabaseManager
from cryptoManager import CryptoManager
from configClasses.radConfig import RadConfig
import uuid
import os 
import requests

class ControlAgent: 
    
    def __init__(self):
        self.app = Flask(__name__)            
        self.setup_routes()
        self.DBusers = DatabaseManager()
        self.radConfig = RadConfig()
        #self.DBusers.show_database()
        
    def setup_routes(self):
        self.app.add_url_rule('/login', 'login', self.logIn, methods=['POST'])
        self.app.add_url_rule('/createNewDatabase', 'createNewDatabase', self.createNewDatabase, methods=['POST'])
            
     
    #Not in use RN, remainder to an old architecture        
    def logIn(self): 
        
        data = request.get_json()
        user = data.get('user')
        cryptpassword = data.get('pass')
        password = CryptoManager.decrypt_text(cryptpassword)
        return jsonify({"message": "Datos recibidos con éxito"})
    
    
    def createNewDatabase(self):
        """
        Creates a new database in the selected RA&D agent .

        This function handles a request to create a new database by verifying the user's 
        credentials, decrypting the provided content, and sending it to a remote system 
        for database creation. It also updates the local user database with the new 
        database information if the operation is successful.

        Process:
            1. Extracts user credentials, encrypted content, and other necessary data from the request.
            2. Verifies user credentials using the local database.
            3. Checks if all required fields are present in the request. If any are missing, returns a 400 error.
            4. Decrypts the provided PDF files and saves them to a temporary directory.
            5. Encrypts the files again with the selected RA&D agent's encryption key.
            6. Prepares the encrypted data and sends it to the remote system for database creation.
            7. If the database is successfully created remotely, extracts the database ID from the response.
            8. Checks if the user already has a database assigned to the specified slot.
                - If a database already exists in the slot, deletes it to avoid leftovers.
            9. Updates the local user database with the new database ID for the specified slot.
            10. Cleans up the temporary directory used to store decrypted files.
    
        Returns:
            Response: A JSON response indicating the status of the database creation. 
                    - 200 OK if successful, including the new database information.
                    - 403 Forbidden if user credentials are invalid.
                    - 400 Bad Request if required fields are missing.
                    - 500 Internal Server Error if the remote request fails.

        Raises:
            HTTPException: Raises a 403 error if the user is not authenticated.

        Request JSON Structure:
            {
                "user": str,                # Username for authentication
                "pass": str,                # Encrypted password for authentication
                "database": str,            # Name of the new database to be created
                "elementNames": str,        # Names of the elements/files, separated by '#'
                "content": str              # Encrypted PDF content, separated by newlines
            }

        Notes:
            - The temporary folder for storing decrypted files is created in the 'controlAgent' directory.
            - The PDF files are decrypted using `CryptoManager.decrypt_pdf` and later re-encrypted 
            using `CryptoManager.encrypt_pdf` before being sent to the remote server.

        """

        json = request.get_json()
    
        user = json.get('user')
        cryptpassword = json.get('pass')
        password = CryptoManager.decrypt_text(cryptpassword)
        database_slot = json.get ('database')
        elementNames = json.get ('elementNames')
        content = json.get('content')
        
        result = self.DBusers.verify_user(user, password)
        
        ## Not auth user
        if (not result):
            abort(403, description="Invalid credentials")
            
        ## Not al necessary fields
        if None in (user, cryptpassword, database_slot, elementNames, content):
            missing_fields = [key for key in ['user', 'pass', 'database', 'elementNames', 'content'] if json.get(key) is None]
            return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400
        
        ## Decrypt info
        fileNames = elementNames.split('#')
        files = content.split('\n')
        
        folder_name = str(uuid.uuid4())
        folder_path = os.path.join("controlAgent", folder_name)
        os.makedirs(folder_path)
        
        #Save pdfs in the container 
        for i in range(len(files) - 1):
            save_path = os.path.join ("controlAgent",folder_name,fileNames[i])
            CryptoManager.decrypt_pdf(files[i], save_path)
            
        ##Preprocess data 
        endpoint = "/createvectordatabase"
        URL = f"{self.radConfig.ip}{endpoint}"
        contentString=""
        elementNames = ""
        uploadPath = folder_path
        
        for file in os.listdir(uploadPath):
            filePath = os.path.join(uploadPath, file)
            if os.path.isfile(filePath) and file.lower().endswith('.pdf'):
                with open(filePath, 'rb') as file:
                    auxName = file.name.split(os.sep)
                    name = auxName[len(auxName) -1]
                    elementNames = elementNames + name + '#'
                    encryptedFile = CryptoManager.encrypt_pdf(filePath, self.radConfig.cypherPass)
                    contentStringaux = encryptedFile + '\n'
                    contentString = contentString + contentStringaux
               
          
        data = {
            "elementNames": elementNames,
            "content" : contentString
        }

        #Send request to RA&D to create new database 
        response = requests.post(URL, json=data)
        
        ##Update users database to include new database 
        if response.status_code == 200:
            #extact data from json
            data = response.json()
            database_id = data.get("database_id")
            
            #if slot already have a database delete it to avoid leftovers
            database_number = self.get_database_number(database_slot)
            has_assigned = self.DBusers.has_assigned_db(user, database_number)
            if (has_assigned):
                self.delete_database(user=user, database_number=database_number)
                
            self.DBusers.update_databaseID(username=user, database_number=database_number, new_databaseID=database_id)
            self.delete_directory(folder_path)
            response = make_response(jsonify({"Status": "ok"}), 200)
            return response
        else:
            response = make_response(jsonify({"Status": "Fail"}), 500)
            return response


    def delete_database(self, user, database_number ):   
        """
        Deletes a database from the selected RA&D agent for a specific user and database number.

        Args:
            user (str): The username of the user whose database needs to be deleted.
            database_number (int): The number of the database slot to be deleted.

        Returns:
            None: The function sends the request but does not return a specific response.
        """
        
        endpoint = "/deletevectordatabase"
        URL = f"{self.radConfig.ip}{endpoint}"  
        database_id = self.DBusers.get_database_id_by_user_and_numdb(user, database_number)
        encrypted_database_id = CryptoManager.encrypt_text(database_id, self.radConfig.cypherPass)
        
        data = {
            "encrypted_database_id": encrypted_database_id
        }
        
        response = requests.post(URL, json=data)
        
        
    #Aux functions
    def delete_directory(self, path):
        if os.path.exists(path):            
            if os.path.isdir(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        self.delete_directory(item_path)
                    else:
                        os.remove(item_path)
                os.rmdir(path) 
    
    
    def get_database_number(self, database_string:str): 
        match database_string: 
            case "db1":
                return 1
            case "db2":
                return 2
            case "db3":
                return 3
            case _: 
                return -1
            
    def run(self):
        self.app.run(port=5006, debug=True)
        
        


if __name__ == '__main__':
    controlAgent = ControlAgent()
    controlAgent.run()