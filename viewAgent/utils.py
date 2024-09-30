import os 
import json
import re

class Utils: 
    
    def parse_message(self, message):
        message = re.sub(r'(?<!\\)\*\*(.*?)\*\*', r'<strong>\1</strong>', message)
        message = message.replace(r'\*\*', '**')  
        return message
    
    def empty_directory(self, path):
        """Empty a directory of all its contents without deleting the directory itself."""
        if os.path.exists(path):
            if os.path.isdir(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        self.empty_directory(item_path)
                        os.rmdir(item_path)
                    else:
                        os.remove(item_path)
            
            
    def get_messages_as_json(self, db, messages):
        if db in messages:
            db_json = json.dumps(messages[db])
            return db_json
        else:
            return None
        