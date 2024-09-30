from flask import Flask, render_template, request, jsonify, redirect, url_for
from configClasses.controlConfig import ControlConfig
from cryptoManager import CryptoManager
import os
import requests
import json
from utils import Utils



class ViewAgent:
    
    def __init__(self):
        self.app = Flask(__name__)
        self.configure_upload_folder()
        self.setup_routes()
        self.database = "aaa" 
        self.messages = {
            'db1':[],
            'db2':[],
            'db3':[],
            }
        self.utils = Utils()
        self.controlConfig = ControlConfig()
        
    def configure_upload_folder(self):
        self.UPLOAD_FOLDER = 'viewAgent/uploads/'
        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)

    def setup_routes(self):
        #Return HTML files
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/uploadFile', 'upload_file', self.upload_file)                 
        
        #Request control server
        self.app.add_url_rule('/send_message', 'send_message', self.send_message, methods=['POST']) 
        self.app.add_url_rule('/upload', 'upload', self.upload, methods=['POST'])
        
        #States control
        self.app.add_url_rule('/clear_messages', 'clear_messages', self.clear_messages, methods=['POST']) 
        

    ##HTML returns
    def home(self):
        return render_template('index.html')
 
    def upload_file(self):
        db_name = request.args.get('db')
        if db_name not in ['DB1', 'DB2', 'DB3']:
            return "Base de datos no válida", 400
        self.database = db_name.lower()
        return render_template('uploadFile.html')

    ## Features

    def upload(self):
        if 'file' not in request.files:
            return 'No file part', 400
        files = request.files.getlist('file')
        for file in files:
            if file.filename == '':
                return 'No selected file', 400
            if file:
                file.save(os.path.join(self.app.config['UPLOAD_FOLDER'], file.filename))
        '''
            Send to: 
                endpoint = "/createNewDatabase"
                logInPath = f"{self.controlAgentIP}{endpoint}"
                
            Data to send: 
                userName
                Pass
                DatabaseNumber
                Documents
        '''
        endpoint = "/createNewDatabase"
        URL = f"{self.controlConfig.ip}{endpoint}"
        
        uploadPath = os.path.join("viewAgent", "uploads")

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
                        "content": pdf_bytes.hex()  # Almacena las páginas como una lista
                    }
                filesList.append(file_data)

        
        data = {
            "user":self.controlConfig.user,
            "pass":self.controlConfig.password,
            "database": self.database,
            "files":filesList
        }

        json_data = json.dumps(data)
        
        cipherData = CryptoManager.encrypt_text(json_data, self.controlConfig.cypherPass)
        data_to_send = {"cipherData": cipherData}
        
        response = requests.post(URL, json=data_to_send)
        delete_path = os.path.join("viewAgent", "uploads")
        self.utils.empty_directory(delete_path)
        self.database = "aaa"
        
        #Close uploader tab 
        return render_template('close_windows.html')

    def send_message(self):
        try: 
            endpoint = "/processMessage"
            URL = f"{self.controlConfig.ip}{endpoint}"
            print (URL)
            
            user_message = request.json.get('message')
            currentDB = request.json.get('currentDB')
            
            self.messages[currentDB].append({'type': 'HumanMessage', 'text': user_message})
            
            ''' 
            Steps: 
                1- Create a Json contains al messages
                2- Cypher Json with Cyphertext
                3- Send to control and wait response
                4- Add response to database
                5- return response to js file     
            '''
            json_chat = self.utils.get_messages_as_json(currentDB, self.messages)
            
            
            data = {
                "user":self.controlConfig.user,
                "pass":self.controlConfig.password,
                "chat":json_chat, 
                "database":currentDB
            }
            json_data = json.dumps(data)
            
            cipherData = CryptoManager.encrypt_text(json_data, self.controlConfig.cypherPass)
            data_to_send = {"cipherData": cipherData}
            
            generation = requests.post(URL, json=data_to_send)
            
            if generation.status_code == 200:
                data = generation.json()  
                ciphered_generation = data['cipher_response'] 
                generation_json = CryptoManager.decrypt_text(ciphered_generation, self.controlConfig.cypherPass)
                generation = json.loads(generation_json)
                text = generation["generation"]
                response_message = self.utils.parse_message(text) 
                
                self.messages[currentDB].append({'type': 'AIMessage', 'text': response_message})
                return jsonify({'response': response_message}), 200
            else:
                response_message = "Internal error please refresh website :(.\n If it doest work please check Agent Satus"
                response_message = self.utils.parse_message(response_message)
                self.messages[currentDB].append({'type': 'AIMessage', 'text': response_message})
                return jsonify({'response': response_message}), 500

            
            
        except Exception as e: 
            print (e)
            response_message = "Internal error please refresh website :(. If it doest work please check Agent Satus"
            response_message = self.utils.parse_message(response_message)
            self.messages[currentDB].append({'type': 'AIMessage', 'text': response_message})
            return jsonify({'response': response_message}), 500

    
    def clear_messages(self):
        self.messages['db1'] = []
        self.messages['db2'] = []
        self.messages['db3'] = []
        
        return jsonify({'status': 'Messages cleared successfully'})


    def run(self):
        self.app.run(port=5005, debug=True)

if __name__ == '__main__':
    my_app = ViewAgent()
    my_app.run()
