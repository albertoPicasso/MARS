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
        else:
            pass

    def create_tables(self):
        self.db.create_tables([Databases])
        pass

    def add_entry(self, database_id: str, status_value: str = StatusEnum.processing):
        
        entry =  {'database_id': database_id, 'status': status_value}
        try:
            self.db.connect()
            with self.db.atomic():  
                Databases.create(**entry)
        except Exception as e:
            #print(f"An error occurred while adding databases: {e}")
            pass
        finally:
            self.db.close()

    def get_all_entries(self):
        self.db.connect()  
        try:
            entries = Databases.select() 
            return [(entry.database_id, entry.status) for entry in entries]
        except Exception as e:
            return []
        finally:
            self.db.close() 

    def entry_exists(self, database_id: str) -> bool:
            self.db.connect() 
            try:
                exists = Databases.select().where(Databases.database_id == database_id).exists()
                return exists
            except Exception as e:
                #print(f"Error checking existence of entry: {e}")
                return False
            finally:
                self.db.close()

    def update_entry_status(self, database_id: str, new_status: str) -> bool:
        
        if new_status not in [status.value for status in StatusEnum]:
            return False
    
        self.db.connect() 
        try:
            query = Databases.update(status=new_status).where(Databases.database_id == database_id)
            if query.execute():
                print(f"Updated entry {database_id} to status '{new_status}'.")
                return True
            else:
                print(f"No entry found with database_id: {database_id}.")
                return False
        except Exception as e:
            print(f"An error occurred while updating the status: {e}")
            return False
        finally:
            self.db.close()

    def get_database_status(self, database_id: str): 
        
        self.db.connect() 
        status = Databases.select().where(Databases.database_id == database_id).get()
        self.db.close()
        return status.status


# Función principal donde se gestionan las operaciones
def main():
    # Inicializar la base de datos
    my_db = StatusDatabaseManager()

    # Añadir entradas válidas
    my_db.add_entry('db4', StatusEnum.ready)        # Agregar estado 'ready'
    my_db.add_entry('db5', StatusEnum.processing)   # Agregar estado 'processing'
    my_db.add_entry('db6', StatusEnum.error)        # Agregar estado 'error'

    # Intentar añadir una entrada con un estado inválido
    my_db.add_entry('db4', 'invalid_status')  # Este lanzará un error
    
    # Obtener y mostrar todas las entradas
    entries = my_db.get_all_entries()
    print("All entries in the database:")
    for entry in entries:
        print(entry)
    
# Ejecutar el programa
if __name__ == "__main__":
    main()
