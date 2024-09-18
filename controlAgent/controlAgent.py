from flask import Flask, request,jsonify, abort
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
        self.DBusers.update_databaseID(username='al', database_number=1, new_databaseID="culoAJJAJAJ")
        self.DBusers.show_database()
        
        
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
        
        result = self.DBusers.verify_user(user, password)
        ## Not auth user
        if (not result):
            abort(403, description="Invalid credentials")
            
        ## Not al necessary fields
        if None in (user, cryptpassword, database, elementNames, content):
            missing_fields = [key for key in ['user', 'pass', 'database', 'elementNames', 'content'] if json.get(key) is None]
            return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400
        
        ## Decrypt info
        fileNames = elementNames.split('#')
        files = content.split('\n')
        
        folder_name = str(uuid.uuid4())
        folder_path = os.path.join("controlAgent", folder_name)
        os.makedirs(folder_path)
        
        for i in range(len(files) - 1):
            save_path = os.path.join ("controlAgent",folder_name,fileNames[i])
            CryptoManager.decrypt_pdf(files[i], save_path)
            
        ##Send to db Agent to create Database
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

        response = requests.post(URL, json=data)
            
        self.delete_directory(folder_path)    
        return "hi"


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
                
    def run(self):
        self.app.run(port=5006, debug=True)
        
        


if __name__ == '__main__':
    controlAgent = ControlAgent()
    controlAgent.run()