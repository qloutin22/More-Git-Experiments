import yaml
from yaml.loader import SafeLoader
from sqlalchemy import create_engine,MetaData,Table
import pandas as pd
import re
import numpy as np

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
        if table_name in list(metadata.tables):
            table = Table(table_name, metadata, autoload_with=engine)
            return pd.read_sql_table(table_name, engine)
        else:
            print(f"Table '{table_name}' does not exist.")
            return None
   
   @staticmethod
   def clean_user_data():
        table_name = 'legacy_users'
        user_data = DatabaseConnector().read_rds_table(table_name)
        #user_data.dropna(inplace=True)
        pd.to_datetime(user_data['date_of_birth'],errors='coerce')
        pd.to_datetime(user_data['join_date'], errors='coerce')
        user_data.drop_duplicates(inplace=True)
        user_data['first_name'] = user_data['first_name'].astype(str)
        user_data['first_name'] = user_data['first_name'].str.slice(0, 255)  
        user_data['last_name'] = user_data['last_name'].astype(str)
        user_data['last_name'] = user_data['last_name'].str.slice(0, 255)    
        user_data['date_of_birth'] = pd.to_datetime(user_data['date_of_birth'],errors='coerce')  
        user_data['country_code'] = user_data['country_code'].astype('string')  
        user_data['user_uuid'] = user_data['user_uuid'].astype('string') 
        user_data.drop_duplicates(subset=['user_uuid'], inplace=True)   
        user_data['join_date'] = pd.to_datetime(user_data['join_date'],errors='coerce')  
        
        return user_data
    


   @staticmethod
   def upload_to_db(self,df, table_name):
     df = DatabaseConnector.clean_user_data()
     table_name= 'dim_users'
     engine = DatabaseConnector.upload_db_engine()
     try:
         df.to_sql(table_name, engine, if_exists='replace', index=False)
         print(f"Data uploaded successfully to table '{table_name}' in the database.")
     except Exception as e:
            print(f"Error uploading data to table '{table_name}': {str(e)}")
   
   @staticmethod
   def upload_db_engine():
     with open(r'C:\Users\quann\OneDrive\Desktop\Data Engineering\Projects\Multinational Retail Data Centralisation\upload_creds.yaml', 'r') as file:
          db_credentials = yaml.load(file, Loader = SafeLoader)
     db_url = f"postgresql://{db_credentials['RDS_USER']}:{db_credentials['RDS_PASSWORD']}@{db_credentials['RDS_HOST']}:{db_credentials['RDS_PORT']}/{db_credentials['RDS_DATABASE']}"
     engine = create_engine(db_url)
     return engine
     
     
db = DatabaseConnector()

"""Prints the data base credentials"""
#credentials = db.read_db_creds()
#print("Database Credentials:", credentials)

"""Returns the search engine"""
#search_egine = db.init_db_engine()
#print(search_egine)

"""Lists all tables in a search engine """
"""
if __name__ == "__main__":
  tables = db.list_db_tables()
  print("List of tables:", tables)
  """

"""Prints all tables ..."""
"""
if __name__ == "__main__":
 table_name_to_read = 'orders_table'
 table_reader = db.read_rds_table(table_name_to_read)
 if table_reader is not None:
   print(f"DataFrame for '{table_name_to_read}':")
   print (pd.DataFrame(table_reader))
   """
   
    
"""Prints clean user data""" 
"""
clean_data = db.clean_user_data()
print(clean_data)
"""
"""
df = db.clean_user_data()
table_name = 'legacy_users'
db.upload_to_db(df,table_name)
"""

"""Code to upload data to pgAdmin 4 database"""
"""
user_data = db.read_rds_table('legacy_users')
cleaned_user_data = db.clean_user_data()
print(cleaned_user_data)
table_name = 'dim_users'
db.upload_to_db('self', user_data,table_name)
"""

