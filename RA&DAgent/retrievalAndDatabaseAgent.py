from flask import Flask, render_template, request, jsonify, redirect, url_for
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
        json = request.get_json()
    
        elementNames = json.get ('elementNames')
        content = json.get('content')
        
        if None in (elementNames, content):
            missing_fields = [key for key in ['elementNames', 'content'] if json.get(key) is None]
            return jsonify({"error": "Faltan argumentos en el JSON", "missing_fields": missing_fields}), 400
        
        fileNames = elementNames.split('#')
        files = content.split('\n')
        
        ## Folder name will be used as database name too 
        folder_name = str(uuid.uuid4())
        folder_path = os.path.join("RA&DAgent", folder_name)
        os.makedirs(folder_path)
        
        for i in range(len(files) - 1):
            save_path = os.path.join ("RA&DAgent",folder_name,fileNames[i])
            CryptoManager.decrypt_pdf(files[i], save_path)
            
        print (folder_path, folder_name)
        
        self.database_manager.create_database(folder_path, folder_name)
        
        
        
        
        
        return "hi"
        
    
    
    
    
    def run(self):
        self.app.run(port=5007, debug=True)
        
        
if __name__ == '__main__':
    rab = retrievalAndDatabaseAgent()
    rab.run()
    