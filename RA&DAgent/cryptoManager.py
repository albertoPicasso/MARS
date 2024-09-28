import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

class CryptoManager: 
    
    def encrypt_text(plain_text: str, key_string: str  = "fedcba0987654321fedcba0987654321") -> str:
        """
        Encrypts a plain text using AES encryption in CBC mode with PKCS7 padding.

        This function takes a plain text string and encrypts it using a symmetric key derived 
        from the provided key string. It generates a random initialization vector (IV) for 
        encryption and concatenates it with the ciphertext, which is then returned as a 
        base64 encoded string.

        Args:
            plain_text (str): The plain text string to be encrypted.
            key_string (str, optional): A string used to derive the encryption key. 
                                        Defaults to "fedcba0987654321fedcba0987654321".

        Returns:
            str: The base64 encoded string of the encrypted data, which includes the IV 
                concatenated with the ciphertext.

        Raises:
            ValueError: If the plain text is not a valid string.
        """
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


    def decrypt_text(ciphertext_base64: str, key_string = "fedcba0987654321fedcba0987654321") -> str:            
        """
        Decrypts a base64 encoded ciphertext using AES encryption in CBC mode.

        This function takes a base64 encoded ciphertext and decrypts it using a symmetric 
        key derived from the provided key string. It extracts the initialization vector (IV) 
        from the ciphertext and applies PKCS7 padding removal to retrieve the original plain text.

        Args:
            ciphertext_base64 (str): The base64 encoded string of the ciphertext to be decrypted.
            key_string (str, optional): A string used to derive the decryption key. 
                                        Defaults to "fedcba0987654321fedcba0987654321".

        Returns:
            str: The original plain text string that was encrypted.

        Raises:
            ValueError: If the input ciphertext is not a valid base64 encoded string.
        """
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
    
    
    def encrypt_pdf(file_path: str, key_string: str  = "fedcba0987654321fedcba0987654321") -> str:
        """
        Encrypts a PDF file and returns the encrypted data as a base64 encoded string.

        This function reads a PDF file from the specified file path, encodes its bytes 
        to base64, and then encrypts the base64 string using a symmetric key derived 
        from the provided key string.

        Args:
            file_path (str): The file path of the PDF file to be encrypted.
            key_string (str, optional): A string used to derive the encryption key. 
                                        Defaults to "fedcba0987654321fedcba0987654321".

        Returns:
            str: The base64 encoded string of the encrypted PDF data.

        Raises:
            FileNotFoundError: If the specified PDF file does not exist.
            ValueError: If the PDF file cannot be read or encrypted.
        """
        with open(file_path, 'rb') as file:
            pdf_bytes = file.read()
                
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        encrypted_base64 = CryptoManager.encrypt_text(pdf_base64, key_string)

        return encrypted_base64
    
    
    def decrypt_pdf(encrypted_base64: str,  output_file_path: str, key_string = "fedcba0987654321fedcba0987654321") -> None:
        """
        Decrypts a base64 encoded encrypted PDF data and saves it to a specified file.

        This function takes an encrypted base64 string, decrypts it using a symmetric key 
        derived from the provided key string, and then writes the decrypted bytes to a 
        specified output file path.

        Args:
            encrypted_base64 (str): The base64 encoded string of the encrypted PDF data to be decrypted.
            output_file_path (str): The file path where the decrypted PDF will be saved.
            key_string (str, optional): A string used to derive the decryption key. 
                                        Defaults to "fedcba0987654321fedcba0987654321".

        Returns:
            None

        Raises:
            ValueError: If the input encrypted base64 string is not valid or cannot be decrypted.
            IOError: If there is an error writing to the output file path.
        """
        decrypted_base64 = CryptoManager.decrypt_text(encrypted_base64, key_string)
        
        pdf_bytes = base64.b64decode(decrypted_base64)
        
        with open(output_file_path, 'wb') as file:
            file.write(pdf_bytes)
