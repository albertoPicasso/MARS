import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

class CryptoManager: 
    
    def encrypt_text(plain_text: str, key_string: str = "9f8e7d6c5b4a32109f8e7d6c5b4a3210") -> str:
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


    def decrypt_text(ciphertext_base64: str, key_string = "9f8e7d6c5b4a32109f8e7d6c5b4a3210") -> str:
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
    
    
    def encrypt_pdf(file_path: str, key_string: str = "19f8e7d6c5b4a32109f8e7d6c5b4a3210") -> str:
        with open(file_path, 'rb') as file:
            pdf_bytes = file.read()
                
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        encrypted_base64 = CryptoManager.encrypt_text(pdf_base64, key_string)

        return encrypted_base64
    
    
    def decrypt_pdf(encrypted_base64: str,  output_file_path: str, key_string = "9f8e7d6c5b4a32109f8e7d6c5b4a3210") -> None:
        decrypted_base64 = CryptoManager.decrypt_text(encrypted_base64, key_string)
        
        pdf_bytes = base64.b64decode(decrypted_base64)
        
        with open(output_file_path, 'wb') as file:
            file.write(pdf_bytes)
