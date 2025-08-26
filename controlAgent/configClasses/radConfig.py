from dataclasses import dataclass, field
import os

@dataclass
class RadConfig: 
    ip: str = field(default="")
    cypherPass: str = field(default="")
    
    def __post_init__(self):
        # 'controlAgent',
        file_path = os.path.join('configFiles', 'radInfo.txt')
        config = dict()
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(':', 1)
                config[key] = value
                
        
        self.ip = config.get('ip', 'http://default_ip')
        self.cypherPass = config.get('cypherPass', 'default_cypherPass')
        
        
ra = RadConfig()
