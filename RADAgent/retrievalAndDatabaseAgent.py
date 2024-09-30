from statusDatabaseManager import StatusEnum, StatusDatabaseManager

from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from cryptoManager import CryptoManager
from databasesManager import DatabasesManager

import os 
import uuid
import threading
import json

class retrievalAndDatabaseAgent: 
    
    def __init__(self): 
        self.app = Flask(__name__)
        self.setup_routes()
        self.database_manager = DatabasesManager()
        self.status_database = StatusDatabaseManager()
        
    
    def setup_routes(self):
        self.app.add_url_rule('/createvectordatabase', 'createvectordatabase', self.create_vector_database, methods=['POST'])
        self.app.add_url_rule('/deletevectordatabase', 'deletevectordatabase', self.delete_vector_database, methods=['POST'])
        self.app.add_url_rule('/getretrievalcontext', 'getretrievalcontext', self.get_retrieval_context, methods=['POST'])
         
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
        
        encrypted_data = request.get_json()

        if isinstance(encrypted_data, str):
            encrypted_data = json.loads(encrypted_data)

        cipher_text = encrypted_data.get('cipherData')
        decrypted_data = CryptoManager.decrypt_text(cipher_text)
        data = json.loads(decrypted_data)
        
        required_fields = ['files']
        missing_fields = [field for field in required_fields if data.get(field) is None]

        if missing_fields:
            return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400

        files = data ["files"]
        
        folder_name = str(uuid.uuid4())
        folder_path = os.path.join("RA&DAgent", folder_name)
        os.makedirs(folder_path)
        
        self.save_pdfs(container=folder_path, files=files)
            
        self.status_database.add_entry(database_id=folder_name, status_value=StatusEnum.processing)
        #Create a thread to this func
        thread = threading.Thread(target=self.database_manager.create_database, args=(folder_path, folder_name))
        thread.start()
        
        data = {
            "database_id": folder_name
        }
        
        json_data = json.dumps(data)
        
        cipherData = CryptoManager.encrypt_text(json_data)
        data_to_send = {"cipherData": cipherData}
        
        response = data_to_send, 200
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
        encrypted_data = request.get_json()

        if isinstance(encrypted_data, str):
            encrypted_data = json.loads(encrypted_data)

        cipher_text = encrypted_data.get('cipherData')
        decrypted_data = CryptoManager.decrypt_text(cipher_text)
        data = json.loads(decrypted_data)
        database_id = data["database_id"]
        
        self.status_database.update_entry_status(database_id=database_id, new_status=StatusEnum.deleted)
        
        response = make_response(jsonify({"OK": "OK"}), 200)
            
        return response
    
    
    def get_retrieval_context(self):
        """
        Retrieves the retrieval context based on encrypted input data.

        This function processes a JSON request containing encrypted data. It decrypts the 
        cipher text to extract the last message and the database identifier. It then checks 
        the status of the specified database to determine if it is ready for retrieval. If the 
        database is in a state that is not ready, it responds with an appropriate error message. 
        If the database is ready, it retrieves the relevant documents from the database context, 
        encrypts this context, and returns it in the response.

        Returns:
            Response: A Flask response object containing either:
                - A JSON object with the encrypted context under the key "cipherData" if 
                the operation is successful.
                - An error message in JSON format if the database status is not ready.

        Raises:
            ValueError: If the decrypted data does not contain expected fields.
        """
    
        encrypted_data = request.get_json()

        if isinstance(encrypted_data, str):
            encrypted_data = json.loads(encrypted_data)

        cipher_text = encrypted_data.get('cipherData')
        decrypted_data = CryptoManager.decrypt_text(cipher_text)
        
        data = json.loads(decrypted_data)
        
        message = data.get('last_message')
        database = data.get('database')
        
        database_status = self.status_database.get_database_status(database_id=database)
        
        if (database_status != StatusEnum.ready):
            if (database_status != StatusEnum.deleted):
                response = make_response(jsonify({"Error": "Deleted Database"}), 503)
            if (database_status != StatusEnum.processing):
                response = make_response(jsonify({"Error": "Processing Database"}), 503)
            return response
        
        context = self.database_manager.get_context(database_name=database, query_text=message)
        context_json = json.dumps([{"page_content": doc.page_content, "metadata": doc.metadata} for doc in context])
        cipherData = CryptoManager.encrypt_text(context_json)
        response = make_response(jsonify({"cipherData": cipherData}), 200)
        return response
    
    
    def save_pdfs(self, container, files):
       
        for file in files:
            file_name = file.get('title')
            
            pdf_bytes = bytes.fromhex(file.get('content'))
            
            file_path = os.path.join(container, file_name)
            
            with open(file_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)

    
    
    def run(self):
        self.app.run(port=5007, debug=True)
        
        
if __name__ == '__main__':
    rad = retrievalAndDatabaseAgent()
    rad.run()
    