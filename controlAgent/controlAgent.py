from flask import Flask, request,jsonify, abort, make_response
from databaseManager import DatabaseManager
from cryptoManager import CryptoManager
from configClasses.radConfig import RadConfig
from configClasses.generationConfig import GenerationConfig
import uuid
import os 
import requests
import json

class ControlAgent: 
    
    def __init__(self):
        self.app = Flask(__name__)            
        self.setup_routes()
        self.DBusers = DatabaseManager()
        self.radConfig = RadConfig()
        self.generationConfig = GenerationConfig()
        #self.DBusers.show_database()
        
    def setup_routes(self):
        self.app.add_url_rule('/createNewDatabase', 'createNewDatabase', self.createNewDatabase, methods=['POST'])
        self.app.add_url_rule('/processMessage', 'processMessage', self.process_message, methods=['POST'])
            
    def createNewDatabase(self):
        """
        Create a new database in RAD agent by processing encrypted JSON data containing user credentials and file information.
        Futhermore it update users databases

        This endpoint receives encrypted data in the `cipherData` field, which includes user credentials and 
        a list of files to be uploaded. The expected structure of the decrypted JSON is as follows:
        
        - `user`: The username for authentication (string).
        - `pass`: The password for authentication (string).
        - `database`: Identifier for the target database slot (string).
        - `files`: List of files to be uploaded (array of strings, where each string is a file name and file content).

        The function decrypts the `cipherData`, verifies the user's credentials, and if the verification is successful, 
        it creates a new folder for the files, saves the uploaded PDF files, and sends the data to create a new vector database. 
        If a database already exists in the specified slot, it will be deleted and updated accordingly.

        ---
        parameters:
        - name: cipherData
            in: body
            required: true
            description: Encrypted JSON string that contains user credentials and file information.
            schema:
            type: object
            properties:
                cipherData:
                type: string
                description: The encrypted data representing user credentials and a list of files to be uploaded.

        responses:
        200:
            description: Database created successfully and status updated.
            schema:
            type: object
            properties:
                Status:
                type: string
                example: "ok"
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
        403:
            description: Invalid user credentials.
            schema:
            type: object
            properties:
                message:
                type: string
                example: "Invalid credentials"
        500:
            description: Internal server error occurred during processing.
            schema:
            type: object
            properties:
                message:
                type: string
                example: "Error in Control Agent"
        """

        try:
            encrypted_data = request.get_json()

            if isinstance(encrypted_data, str):
                encrypted_data = json.loads(encrypted_data)

            cipher_text = encrypted_data.get('cipherData')
            decrypted_data = CryptoManager.decrypt_text(cipher_text)
            data = json.loads(decrypted_data)
    
            required_fields = ['user', 'pass', 'database', 'files']
            missing_fields = [field for field in required_fields if data.get(field) is None]

            if missing_fields:
                return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400

            user = data["user"]
            password = data ["pass"]
            database_slot = data ["database"]
            files = data ["files"]
        
            result = self.DBusers.verify_user(user, password)
            
            ## Not auth user
            if (not result):
                abort(403, description="Invalid credentials")
            
            folder_name = str(uuid.uuid4())
            folder_path = os.path.join("controlAgent", folder_name)
            os.makedirs(folder_path)
            
            self.save_pdfs(container=folder_path, files=files)
            
            endpoint = "/createvectordatabase"
            URL = f"{self.radConfig.ip}{endpoint}"
            
            uploadPath = folder_path
            
            filesList = []
            for file in os.listdir(uploadPath):
                filePath = os.path.join(uploadPath, file)
                if os.path.isfile(filePath) and file.lower().endswith('.pdf'):          
                    
                    with open(filePath, 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                        auxName = file.split(os.sep)
                        name = auxName[-1]
                        file_data = {
                            "title": name,
                            "content": pdf_bytes.hex()  
                        }
                    filesList.append(file_data)

            data = {
                "files": filesList
            }
            
            json_data = json.dumps(data)
            
            cipherData = CryptoManager.encrypt_text(json_data, self.radConfig.cypherPass)
            data_to_send = {"cipherData": cipherData}
            
            response = requests.post(URL, json=data_to_send)

            ##Update users database to include new database 
            if response.status_code == 200:
                #extact data from json
                data = response.json()
                cipherData = data.get("cipherData")
                decrypted_data  = CryptoManager.decrypt_text(cipherData, self.radConfig.cypherPass)
                data = json.loads(decrypted_data)
                database_id = data["database_id"]
                
                #if slot already have a database delete it to avoid leftovers
                database_number = self.get_database_number(database_slot)
                has_assigned = self.DBusers.has_assigned_db(user, database_number)
                if (has_assigned):
                    self._delete_database(user=user, database_number=database_number)
                    
                self.DBusers.update_databaseID(username=user, database_number=database_number, new_databaseID=database_id)
                self.delete_directory(folder_path)
                
                #No cipher content bc only need to check status code
                response = make_response(jsonify({"Status": "ok"}), 200)
                return response
            else:
                response = make_response(jsonify({"Status": "Fail"}), 500)
                return response

        except Exception as e: 
            return jsonify({"message": "Error in Control Agent"}), 500  
        

    def _delete_database(self, user, database_number ):   
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
    
        data = {
            "database_id": database_id
        }
        
        json_data = json.dumps(data)
        
        cipherData = CryptoManager.encrypt_text(json_data, self.radConfig.cypherPass)
        data_to_send = {"cipherData": cipherData}
        
        response = requests.post(URL, json=data_to_send)
        
        if (not (response.status_code == 200)):
            raise RuntimeError("Error: deleting database  Reason: {}".format(response))
        
   
   
   
    def process_message(self):
        """
        Process a user message and retrieve context for message generation.

        This endpoint receives encrypted data in the `cipherData` field, which contains user credentials 
        and chat history. The expected structure of the decrypted JSON is as follows:
        
        - `user`: The username for authentication (string).
        - `pass`: The password for authentication (string).
        - `database`: Identifier for the target database slot (string).
        - `chat`: JSON string representing the chat history (array of messages).

        The function decrypts the `cipherData`, verifies the user's credentials, retrieves the last message 
        from the chat history, and sends a request to get the context for that message. It then sends the 
        entire chat history along with the context to generate a response. If the verification fails or 
        if any required fields are missing, appropriate error messages are returned.

        ---
        parameters:
        - name: cipherData
            in: body
            required: true
            description: Encrypted JSON string that contains user credentials and chat history.
            schema:
            type: object
            properties:
                cipherData:
                type: string
                description: The encrypted data representing user credentials and chat history.

        responses:
        200:
            description: Message processed successfully and response generated.
            schema:
            type: object
            properties:
                cipher_response:
                type: string
                description: The encrypted response from the generation agent.
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
        403:
            description: Invalid user credentials.
            schema:
            type: object
            properties:
                message:
                type: string
                example: "Invalid credentials"
        500:
            description: Internal server error occurred during processing.
            schema:
            type: object
            properties:
                message:
                type: string
                example: "Error in Control Agent"
        """
        try:
            endpoint = "/getretrievalcontext"
            URL = f"{self.radConfig.ip}{endpoint}"

            encrypted_data = request.get_json()

            if isinstance(encrypted_data, str):
                encrypted_data = json.loads(encrypted_data)

            cipher_text = encrypted_data.get('cipherData')
            decrypted_data = CryptoManager.decrypt_text(cipher_text)
            
            data = json.loads(decrypted_data)
            
            required_fields = ['user', 'pass', 'database', 'chat']
            missing_fields = [field for field in required_fields if data.get(field) is None]

            if missing_fields:
                return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400

    
            user = data.get('user')
            password = data.get('pass')
            chat = data.get("chat")
            database_slot = data.get("database")
            database_slot_number = self.get_database_number(database_slot)
                
            result = self.DBusers.verify_user(user, password)
            
            if not result:
                abort(403, description="Invalid credentials")
                
            messages = json.loads(chat)
            database = self.DBusers.get_database_id_by_user_and_numdb(username=user, numdb=database_slot_number)
            
            #Get retrieval of a last user message
            
            last_message = messages[-1].get("text")
                
                #Prepare data to send
            data = {
                "last_message":last_message,
                "database": database
            }
            
            json_data = json.dumps(data)
            cipherData = CryptoManager.encrypt_text(json_data, self.radConfig.cypherPass)
            data_to_send = {"cipherData": cipherData}
            
            context = requests.post(URL, json=data_to_send)
            
                #Get response data
            if context.status_code == 200:
                data = context.json()
                cipher_data = data['cipherData']
                decrypted_data = CryptoManager.decrypt_text(cipher_data, self.radConfig.cypherPass)
                
            else:
                response = make_response(jsonify({"Status": "Fail"}), 500)
                return response
                
            ##Generate response from generator Agent

                #Prepare data to send
            data = {
                "chat" : messages,
                "context": decrypted_data
            }
            
            json_data = json.dumps(data)
            cipherData = CryptoManager.encrypt_text(json_data, self.generationConfig.cypherPass)
            data_to_send = {"cipherData": cipherData}

                #Prepare URL
            endpoint = "/generationwithmessagehistory"
            URL = f"{self.generationConfig.ip}{endpoint}"  
            
                #Send
            generation = requests.post(URL, json=data_to_send)
            
            if generation.status_code == 200:
                data = generation.json()  
                ciphered_generation = data['cipher_response'] 
                generation = CryptoManager.decrypt_text(ciphered_generation, self.generationConfig.cypherPass)
                ciphered_generation = CryptoManager.encrypt_text(generation)
                return jsonify({"cipher_response": ciphered_generation}), 200
            else:
                        response = make_response(jsonify({"Status": "Fail"}), 500)
                        return response

        except Exception as e: 
            return jsonify({"message": "Error in Control Agent"}), 500    
         
         
         
         
         
         
            
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
            

    def save_pdfs(self, container, files):
       
        for file in files:
            file_name = file.get('title')
            
            pdf_bytes = bytes.fromhex(file.get('content'))
            
            file_path = os.path.join(container, file_name)
            
            with open(file_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)

        
    
            
    def run(self):
        self.app.run(port=5006, debug=True)
        
        


if __name__ == '__main__':
    controlAgent = ControlAgent()
    controlAgent.run()