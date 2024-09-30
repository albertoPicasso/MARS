from peewee import CharField, SqliteDatabase, Model
from enum import Enum
import os

class StatusEnum(str, Enum):
    ready = "ready"
    processing = "processing"
    error = "error"
    deleted = "deleted"

class Databases(Model):
    database_id = CharField(primary_key=True, max_length=100)
    status = CharField(choices=[(status.value, status.value) for status in StatusEnum])

    class Meta:
        database = SqliteDatabase('RADAgent/status_database.db')  

class StatusDatabaseManager:
    
    def __init__(self):
        self.db = Databases._meta.database
        self.create_database()

    def create_database(self):
        if not os.path.exists(self.db.database):
            self.db.connect()
            self.create_tables()
            self.db.close()
        
    def create_tables(self):
        self.db.create_tables([Databases])
        

    def add_entry(self, database_id: str, status_value: str = StatusEnum.processing):
        entry = {'database_id': database_id, 'status': status_value}
        self.db.connect()
        with self.db.atomic():
            Databases.create(**entry)
        self.db.close()


    def get_all_entries(self):
        self.db.connect()
        entries = Databases.select()
        self.db.close()
        return [(entry.database_id, entry.status) for entry in entries]


    def entry_exists(self, database_id: str) -> bool:
        self.db.connect()
        exists = Databases.select().where(Databases.database_id == database_id).exists()
        self.db.close()
        return exists


    def update_entry_status(self, database_id: str, new_status: str) -> bool:
        if new_status not in [status.value for status in StatusEnum]:
            return False

        self.db.connect()
        query = Databases.update(status=new_status).where(Databases.database_id == database_id)
        result = query.execute()
        self.db.close()  
        return result > 0 

    def get_database_status(self, database_id: str): 
        
        self.db.connect() 
        status = Databases.select().where(Databases.database_id == database_id).get()
        self.db.close()
        return status.status

