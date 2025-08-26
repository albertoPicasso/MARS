from dataclasses import dataclass, field
import os

@dataclass
class ControlConfig: 
    ip: str = field(default="")
    cypherPass: str = field(default="")
    
    def __post_init__(self):
        #'viewAgent',
        file_path = os.path.join('configFiles', 'controlInfo.txt')
        config = dict()
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(':', 1)
                config[key] = value
                
        
        self.user = config.get('user', 'default_user')
        self.password = config.get('password', 'default_password')
        self.ip = config.get('ip', 'http://default_ip')
        self.cypherPass = config.get('cypherPass', 'default_cypherPass')
        

