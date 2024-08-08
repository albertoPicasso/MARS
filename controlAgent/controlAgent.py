from flask import Flask, session, request,jsonify
from databaseManager import DatabaseManager

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptoManager import CryptoManager
import base64
import hashlib
import uuid
import os 

class ControlAgent: 
    def __init__(self):
        self.app = Flask(__name__)    
        self.setup_routes()
        self.DBusers = DatabaseManager()
        
        
    def setup_routes(self):
        self.app.add_url_rule('/login', 'login', self.logIn, methods=['POST'])
        self.app.add_url_rule('/createNewDatabase', 'createNewDatabase', self.createNewDatabase, methods=['POST'])
            
    def logIn(self): 
        datos = request.get_json()
    
        # Extraer los valores
        user = datos.get('user')
        cryptpassword = datos.get('pass')
        password = CryptoManager.decrypt_text(cryptpassword)
        print (user, password)
        # Procesar los datos (esto es solo un ejemplo)
        # Puedes realizar autenticación o cualquier otra lógica aquí
        
        # Responder con un mensaje de éxito
        return jsonify({"message": "Datos recibidos con éxito"})
    
    def createNewDatabase(self):
        json = request.get_json()
    
        user = json.get('user')
        cryptpassword = json.get('pass')
        password = CryptoManager.decrypt_text(cryptpassword)
        database = json.get ('database')
        elementNames = json.get ('elementNames')
        content = json.get('content')
        
        if None in (user, cryptpassword, database, elementNames, content):
            missing_fields = [key for key in ['user', 'pass', 'database', 'elementNames', 'content'] if json.get(key) is None]
            return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400
        
        fileNames = elementNames.split('#')
        files = content.split('\n')
        
        folder_name = str(uuid.uuid4())
        os.makedirs(folder_name, exist_ok=True)
        save_path = os.path.join ("controlAgent",folder_name,fileNames[0])
        
        CryptoManager.decrypt_pdf(files[0], save_path)
            
        return "hi"


                
                
    def run(self):
        self.app.run(port=5006, debug=True)
        
        
    def delete_folder_and_contents(path):
        if os.path.exists(path):
            # Recursively delete all files and subdirectories
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    os.rmdir(dir_path)
            # Remove the main directory
            os.rmdir(path)
            print(f"The folder '{path}' and all its contents have been successfully deleted.")
        else:
            print(f"The folder '{path}' does not exist.")

if __name__ == '__main__':
    controlAgent = ControlAgent()
    controlAgent.run()