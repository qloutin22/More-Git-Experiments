import yaml
from yaml.loader import SafeLoader
from sqlalchemy import create_engine,MetaData,Table
import pandas as pd

class DatabaseConnector():
  
   @staticmethod
   def read_db_creds():
     with open(r'C:\Users\quann\OneDrive\Desktop\Data Engineering\Projects\Multinational Retail Data Centralisation\db_creds.yaml', 'r') as file:
       db_creds = yaml.load(file, Loader = SafeLoader)
       return db_creds
     
   @staticmethod
   def init_db_engine():
     db_credentials = DatabaseConnector.read_db_creds()
     db_url = f"postgresql://{db_credentials['RDS_USER']}:{db_credentials['RDS_PASSWORD']}@{db_credentials['RDS_HOST']}:{db_credentials['RDS_PORT']}/{db_credentials['RDS_DATABASE']}"
     engine = create_engine(db_url)
     return engine
   
   @staticmethod
   def list_db_tables():
    engine = DatabaseConnector.init_db_engine()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table_names =  metadata.tables.keys()
    return table_names
  
   @staticmethod
   def read_rds_table(table_name):
        engine = DatabaseConnector.init_db_engine()
        metadata = MetaData()
        metadata.reflect(bind=engine)
        if table_name in metadata.tables:
            table = Table(table_name, metadata, autoload_with=engine)
            return pd.read_sql_table(table_name, engine)
        else:
            print(f"Table '{table_name}' does not exist.")
            return None
          
   @staticmethod
   def clean_user_data(user_data):
        user_data = user_data.dropna()
        user_data['date_column'] = pd.to_datetime(user_data['date_column'], errors='coerce')
        user_data['age'] = pd.to_numeric(user_data['age'], errors='coerce')
        user_data = user_data[user_data['age'] > 0] 
        return user_data
        
   def upload_to_db(self, df, table_name):
        df.to_sql(table_name, con=self.engine, if_exists='replace', index=False)
        print(f"Uploaded DataFrame to '{table_name}' table in the database.") 
     
     
      


db = DatabaseConnector()

credentials = db.read_db_creds()
print("Database Credentials:", credentials)

engine = db.init_db_engine()
print("Database Engine:", engine)

if __name__ == "__main__":
    tables = db.list_db_tables()
    print("List of tables:", tables)

if __name__ == "__main__":
    table_name_to_read = 'orders_table' 
    table_reader = db.read_rds_table(table_name_to_read)
    if table_reader is not None:
        print(f"DataFrame for '{table_name_to_read}':")
        print(table_reader)
 
 
#user_data =  table_reader     
#clean_data = DatabaseConnector.clean_user_data(user_data)
#print(clean_data)





