from flask import Flask, session, request,jsonify
from databaseManager import DatabaseManager

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import hashlib

import os 

class ControlAgent: 
    def __init__(self):
        self.app = Flask(__name__)    
        self.setup_routes()
        self.DBusers = DatabaseManager()
        
        
    def setup_routes(self):
        self.app.add_url_rule('/login', 'login', self.logIn, methods=['POST'])
            
            
            
    def logIn(self): 
        datos = request.get_json()
    
        # Extraer los valores
        user = datos.get('user')
        cryptpassword = datos.get('pass')
        password = self.decrypt_text(cryptpassword)
        print (user, password)
        # Procesar los datos (esto es solo un ejemplo)
        # Puedes realizar autenticación o cualquier otra lógica aquí
        
        # Responder con un mensaje de éxito
        return jsonify({"message": "Datos recibidos con éxito"})
    

    def decrypt_text(self, ciphertext_base64: str, key_string = "1234567890abcdef1234567890abcdef") -> str:
        key = hashlib.sha256(key_string.encode()).digest()

        ciphertext_combined = base64.b64decode(ciphertext_base64)

        iv = ciphertext_combined[:16]
        ciphertext = ciphertext_combined[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        padded_plain_text = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plain_text_bytes = unpadder.update(padded_plain_text) + unpadder.finalize()

        plain_text = plain_text_bytes.decode()

        return plain_text
                
                
    def run(self):
        self.app.run(port=5006, debug=True)

if __name__ == '__main__':
    controlAgent = ControlAgent()
    controlAgent.run()