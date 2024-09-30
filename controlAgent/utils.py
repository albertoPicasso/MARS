import os 

class Utils: 
    
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