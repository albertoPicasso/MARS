from statusDatabaseManager import StatusEnum, StatusDatabaseManager

from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from cryptoManager import CryptoManager
from databasesManager import DatabasesManager

import os 
import uuid
import threading

class retrievalAndDatabaseAgent: 
    
    def __init__(self): 
        self.app = Flask(__name__)
        self.setup_routes()
        self.database_manager = DatabasesManager()
        self.status_database = StatusDatabaseManager()
    
    def setup_routes(self):
        self.app.add_url_rule('/createvectordatabase', 'createvectordatabase', self.create_vector_database, methods=['POST'])
        self.app.add_url_rule('/deletevectordatabase', 'deletevectordatabase', self.delete_vector_database, methods=['POST'])
    
    def create_vector_database(self):
        """
        Creates a new vector database from the provided encrypted PDF content.

        This function processes a request to create a vector database by:
            1. Extracting `elementNames` and `content` from the incoming JSON request.
            2. Validating that all required fields are present; returns a 400 error if any are missing.
            3. Decrypting the provided encrypted PDF content and saving the resulting files to a temporary directory.
            4. Calling `self.database_manager.create_database` to create the vector database using the saved files.
            5. Returning a response containing the `database_id` corresponding to the newly created database.

        Process:
            - Extracts `elementNames` and `content` from the JSON request.
            - Validates the presence of required fields and handles missing fields by returning an error response.
            - Decrypts the PDF files and saves them in a uniquely named temporary directory.
            - Updates the status of the database entry to indicate that it is in the processing stage.
            - Creates the vector database in a separate thread for asynchronous processing.

        Returns:
            Response: A JSON response indicating the status of the database creation.
                    - 200 OK with `database_id` if the creation is successful.
                    - 400 Bad Request if required fields are missing.

        Request JSON Structure:
            {
                "elementNames": str,        # Names of the elements/files, separated by '#'
                "content": str              # Encrypted PDF content, separated by newlines
            }

        Notes:
            - The temporary folder for storing decrypted files is created in the 'RA&DAgent' directory.
            - The PDF files are decrypted using `CryptoManager.decrypt_pdf` before being processed by the database manager.
            - A unique folder name is generated for each new database creation process to avoid conflicts.
        """
        
        json = request.get_json()
    
        elementNames = json.get ('elementNames')
        content = json.get('content')
        
        if None in (elementNames, content):
            missing_fields = [key for key in ['elementNames', 'content'] if json.get(key) is None]
            return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400
        
        fileNames = elementNames.split('#')
        files = content.split('\n')
        
        folder_name = str(uuid.uuid4())
        folder_path = os.path.join("RA&DAgent", folder_name)
        os.makedirs(folder_path)
        
        for i in range(len(files) - 1):           
            save_path = os.path.join ("RA&DAgent",folder_name,fileNames[i])
            CryptoManager.decrypt_pdf(files[i], save_path)
            
        self.status_database.add_entry(database_id=folder_name, status_value=StatusEnum.processing)
        #Create a thread to this func
        thread = threading.Thread(target=self.database_manager.create_database, args=(folder_path, folder_name))
        thread.start()
        cypher_database_name = CryptoManager.encrypt_text(folder_name)
        response = make_response(jsonify({"database_id": cypher_database_name}), 200)
        return response
    
    
    def delete_vector_database(self): 
        """
        Deletes a vector database entry by updating its status to 'deleted'.

        This function processes a request to delete a database by:
            1. Extracting the encrypted database ID from the incoming JSON request.
            2. Decrypting the encrypted database ID to get the actual database ID.
            3. Updating the status of the database entry in the local database to 'deleted'.
            4. Responding with a success message if the operation is successful.

        Args:
            None: This function extracts all necessary information from the incoming request's JSON payload.

        Process:
            1. Extracts `encrypted_database_id` from the JSON request.
            2. Decrypts `encrypted_database_id` using `CryptoManager.decrypt_text()` to obtain the actual `database_id`.
            3. Updates the status of the database entry in the local database to `deleted` by calling `self.status_database.update_entry_status()`.
            4. Returns a JSON response indicating success.

        Returns:
            Response: A JSON response with a 200 OK status indicating that the database deletion was processed.
        """
        json = request.get_json()
        encrypted_database_id  = json.get ('encrypted_database_id')
        database_id = CryptoManager.decrypt_text(encrypted_database_id)
        self.status_database.update_entry_status(database_id=database_id, new_status=StatusEnum.deleted)
        
        response = make_response(jsonify({"OK": "OK"}), 200)
            
        return response
    
    
    
    def run(self):
        self.app.run(port=5007, debug=True)
        
        
if __name__ == '__main__':
    rad = retrievalAndDatabaseAgent()
    rad.run()
    