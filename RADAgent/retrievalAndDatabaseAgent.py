from statusDatabaseManager import StatusEnum, StatusDatabaseManager

from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from cryptoManager import CryptoManager
from databasesManager import DatabasesManager
from utils import Utils

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
        self.utils = Utils()
        
    
    def setup_routes(self):
        self.app.add_url_rule('/createvectordatabase', 'createvectordatabase', self.create_vector_database, methods=['POST'])
        self.app.add_url_rule('/deletevectordatabase', 'deletevectordatabase', self.delete_vector_database, methods=['POST'])
        self.app.add_url_rule('/getretrievalcontext', 'getretrievalcontext', self.get_retrieval_context, methods=['POST'])
         
    def create_vector_database(self):
        """
        Create a vector database from uploaded files.

        This endpoint receives encrypted data in the `cipherData` field, which contains a list of files 
        to be processed and stored in a new vector database. The expected structure of the decrypted JSON 
        is as follows:

        - `files`: List of files to be uploaded (array of strings, where each string is a file name).

        The function decrypts the `cipherData`, verifies the presence of required fields, creates a new folder 
        for the files, and saves the uploaded files. It then starts a background thread to create the database 
        while immediately responding with the unique database identifier. If any required fields are missing, 
        an error message is returned.

        ---
        parameters:
        - name: cipherData
            in: body
            required: true
            description: Encrypted JSON string that contains a list of files to be processed.
            schema:
            type: object
            properties:
                cipherData:
                type: string
                description: The encrypted data representing the list of files.

        responses:
        200:
            description: Vector database creation initiated successfully.
            schema:
            type: object
            properties:
                cipherData:
                type: string
                description: The encrypted identifier for the new database.
        400:
            description: Missing required fields in the JSON request.
            schema:
            type: object
            properties:
                error:
                type: string
                example: "Faltan argumentos en el JSON"
                missing_fields:
                type: array
                items:
                    type: string
        500:
            description: Internal server error occurred during processing.
            schema:
            type: object
            properties:
                message:
                type: string
                example: "Error in RAD Agent"
        """
       
        try:
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
            
            self.utils.save_pdfs(container=folder_path, files=files)
                
            self.status_database.add_entry(database_id=folder_name, status_value=StatusEnum.processing)
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
        
        except Exception as e: 
            return jsonify({"message": "Error in RAD Agent"}), 500    
    
    
    def delete_vector_database(self): 
        """
        Delete a vector database based on the provided database identifier.

        This endpoint receives encrypted data in the `cipherData` field, which contains the identifier 
        for the vector database to be deleted. The expected structure of the decrypted JSON is as follows:

        - `database_id`: Identifier for the database to be deleted (string).

        The function decrypts the `cipherData`, verifies the presence of required fields, updates the status 
        of the specified database to "deleted", and returns a success message. If any required fields are 
        missing, an error message is returned.

        ---
        parameters:
        - name: cipherData
            in: body
            required: true
            description: Encrypted JSON string that contains the database identifier.
            schema:
            type: object
            properties:
                cipherData:
                type: string
                description: The encrypted data representing the database identifier.

        responses:
        200:
            description: Database deletion initiated successfully.
            schema:
            type: object
            properties:
                OK:
                type: string
                example: "OK"
        400:
            description: Missing required fields in the JSON request.
            schema:
            type: object
            properties:
                error:
                type: string
                example: "Faltan argumentos en el JSON"
                missing_fields:
                type: array
                items:
                    type: string
        500:
            description: Internal server error occurred during processing.
            schema:
            type: object
            properties:
                message:
                type: string
                example: "Error in RAD Agent"
        """
        try: 
            encrypted_data = request.get_json()

            if isinstance(encrypted_data, str):
                encrypted_data = json.loads(encrypted_data)

            cipher_text = encrypted_data.get('cipherData')
            decrypted_data = CryptoManager.decrypt_text(cipher_text)
            data = json.loads(decrypted_data)
            
            required_fields = ['database_id', ]
            missing_fields = [field for field in required_fields if data.get(field) is None]

            if missing_fields:
                return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400

            database_id = data["database_id"]
            
            self.status_database.update_entry_status(database_id=database_id, new_status=StatusEnum.deleted)
            
            response = make_response(jsonify({"OK": "OK"}), 200)
                
            return response
    
        except Exception as e: 
            return jsonify({"message": "Error in RAD Agent"}), 500  
    
    def get_retrieval_context(self):
        """
        Retrieve context for a given message from a specified database.

        This endpoint receives encrypted data in the `cipherData` field, which contains the last message 
        to be processed and the identifier for the database from which to retrieve context. The expected 
        structure of the decrypted JSON is as follows:

        - `last_message`: The last message from the user (string).
        - `database`: Identifier for the database from which to retrieve context (string).

        The function decrypts the `cipherData`, verifies the presence of required fields, checks the status 
        of the specified database, and retrieves the relevant context if the database is ready. If the 
        database is either deleted or still processing, an appropriate error message is returned. Finally, 
        the context is encrypted and sent back in the response.

        ---
        parameters:
        - name: cipherData
            in: body
            required: true
            description: Encrypted JSON string that contains the last message and database identifier.
            schema:
            type: object
            properties:
                cipherData:
                type: string
                description: The encrypted data representing the last message and database identifier.

        responses:
        200:
            description: Context retrieved successfully.
            schema:
            type: object
            properties:
                cipherData:
                type: string
                description: The encrypted context data retrieved from the database.
        400:
            description: Missing required fields in the JSON request.
            schema:
            type: object
            properties:
                error:
                type: string
                example: "Faltan argumentos en el JSON"
                missing_fields:
                type: array
                items:
                    type: string
        503:
            description: The database is either deleted or still processing.
            schema:
            type: object
            properties:
                Error:
                type: string
                example: "Deleted Database" or "Processing Database"
        500:
            description: Internal server error occurred during processing.
            schema:
            type: object
            properties:
                message:
                type: string
                example: "Error in RAD Agent"
        """
        try: 
            encrypted_data = request.get_json()

            if isinstance(encrypted_data, str):
                encrypted_data = json.loads(encrypted_data)

            cipher_text = encrypted_data.get('cipherData')
            decrypted_data = CryptoManager.decrypt_text(cipher_text)
            
            data = json.loads(decrypted_data)
            
            required_fields = ['last_message' ,'database']
            missing_fields = [field for field in required_fields if data.get(field) is None]

            if missing_fields:
                return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400

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
        
        except Exception as e: 
            return jsonify({"message": "Error in RAD Agent"}), 500
    
    
    def run(self):
        self.app.run(port=5007, debug=True)
        
        
if __name__ == '__main__':
    rad = retrievalAndDatabaseAgent()
    rad.run()
    