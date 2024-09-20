from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from cryptoManager import CryptoManager
from databasesManager import DatabasesManager
import os 
import uuid

class retrievalAndDatabaseAgent: 
    
    def __init__(self): 
        self.app = Flask(__name__)
        self.setup_routes()
        self.database_manager = DatabasesManager()
        
    
    def setup_routes(self):
        self.app.add_url_rule('/createvectordatabase', 'createvectordatabase', self.create_vector_database, methods=['POST'])
    
    
    def create_vector_database(self):
        """
        Creates a new vector database from the provided encrypted PDF content.

        This function processes a request to create a vector database by decrypting 
        provided content and saving it to a temporary directory. It then delegates 
        the creation of the vector database to a database manager.

        Process:
            1. Extracts `elementNames` and `content` from the JSON request.
            2. Validates that all required fields are present in the request.
            3. Decrypts the provided encrypted PDF content and saves the files to a temporary folder.
            4. Calls `self.database_manager.create_database` to create the database using 
            the saved files in the temporary directory.
            5. Returns a response with the generated `database_id` corresponding to the 
            created database.

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
            - The PDF files are decrypted using `CryptoManager.decrypt_pdf` before being processed 
            by the database manager.

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
            
        print (folder_path, folder_name)
        
        self.database_manager.create_database(folder_path, folder_name)

        response = make_response(jsonify({"database_id": folder_name}), 200)
        return response
        
        
    
    
    
    
    def run(self):
        self.app.run(port=5007, debug=True)
        
        
if __name__ == '__main__':
    rad = retrievalAndDatabaseAgent()
    rad.run()
    