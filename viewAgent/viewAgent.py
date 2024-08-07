from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import requests
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class ViewAgent:
    def __init__(self):
        self.app = Flask(__name__)
        self.configure_upload_folder()
        self.database = "aaa"
        self.setup_routes()
        self.read_config()
        self.register_control_agent()
        


    def configure_upload_folder(self):
        self.UPLOAD_FOLDER = 'viewAgent/uploads/'
        self.app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)

    def setup_routes(self):
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/send_message', 'send_message', self.send_message, methods=['POST']) #chat message
        self.app.add_url_rule('/uploadFile', 'upload_file', self.upload_file)
        self.app.add_url_rule('/upload', 'upload', self.upload, methods=['POST'])
        
    def read_config(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, 'controlAgentInfo.txt')
        config = dict()
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(':', 1)
                config[key] = value
                
        self.passcode = config.get('password', 'default_passcode')
        self.controlAgentIP = config.get('ip', 'http://default_ip')
        self.user = config.get('user', 'default_user')
        self.passForCipher = config.get('cypherPass', 'default_cypherPass')

          
          
    ##No será necesaria en el futuro, solo para las pruebas en login           
    def register_control_agent (self):
        endpoint = "/login"
        logInPath = f"{self.controlAgentIP}{endpoint}"
        
        self.cipheredPass = self.encrypt_text(self.passcode,self.passForCipher)

        data = {
            "user":self.user,
            "pass":self.cipheredPass,
        }
        response = requests.post(logInPath, json=data)
        #Working here//////////////////////////////////////////////////////
        

        
    def encrypt_text(self, plain_text: str, key_string: str) -> str:
        key = hashlib.sha256(key_string.encode()).digest()
        
        iv = os.urandom(16)

        plain_text_bytes = plain_text.encode()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_plain_text = padder.update(plain_text_bytes) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(padded_plain_text) + encryptor.finalize()

        ciphertext_combined = iv + ciphertext
        ciphertext_base64 = base64.b64encode(ciphertext_combined).decode('utf-8')

        return ciphertext_base64




    def home(self):
        return render_template('index.html')

    def send_message(self):
        user_message = request.json.get('message')
        additional_param = request.json.get('currentDB')

        response_message = f"Echo: {user_message}, Param: {additional_param if additional_param is not None else 'None'}"
        return jsonify({'response': response_message})

    def upload_file(self):
        db_name = request.args.get('db')
        if db_name not in ['DB1', 'DB2', 'DB3']:
            return "Base de datos no válida", 400
        self.database = db_name.lower()
        return render_template('uploadFile.html')

    def upload(self):
        if 'file' not in request.files:
            return 'No file part', 400
        files = request.files.getlist('file')
        for file in files:
            if file.filename == '':
                return 'No selected file', 400
            if file:
                file.save(os.path.join(self.app.config['UPLOAD_FOLDER'], file.filename))

        # Aquí podrías llamar a algún agente de control para crear la base de datos vectorial
        self.database = "aaa"
        
        return render_template('close_windows.html')

    def run(self):
        self.app.run(port=5005, debug=True)

if __name__ == '__main__':
    my_app = ViewAgent()
    my_app.run()
