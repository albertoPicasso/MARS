import os

class Utils:
    
    def save_pdfs(self, container, files):
       
        for file in files:
            file_name = file.get('title')
            
            pdf_bytes = bytes.fromhex(file.get('content'))
            
            file_path = os.path.join(container, file_name)
            
            with open(file_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)

    