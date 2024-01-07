from database_utils import DatabaseConnector
import pandas as pd
from sqlalchemy import create_engine,MetaData,Table
import requests

class DataCleaning :

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
   def clean_orders_data():
        table_name = 'orders_table'
        user_data = DatabaseConnector.read_rds_table(table_name)
        columns_to_remove = ['first_name', 'last_name','1']
        user_data.drop(columns=columns_to_remove, inplace=True, errors='ignore')
        user_data.drop_duplicates(inplace=True)
        user_data['date_uuid'] = user_data['date_uuid'].astype('string')# --uuid
        user_data['user_uuid'] = user_data['user_uuid'].astype('string')#  --uuid
        #user_data['card_number'] = user_data['card_number'].astype('string')  
        user_data['store_code'] = user_data['store_code'].astype('string')  #m
        user_data['product_code'] = user_data['product_code'].astype('string') #m 
        user_data['product_quantity'] = user_data['product_quantity'].astype('int16')  

        return user_data
    
   @staticmethod
   def upload_to_db_2(df, table_name):
     df = DataCleaning.clean_orders_data()
     table_name= 'orders_table'
     engine = DatabaseConnector.upload_db_engine()
     try:
         df.to_sql(table_name, engine, if_exists='replace', index=False)
         print(f"Data uploaded successfully to table '{table_name}' in the database.")
     except Exception as e:
            print(f"Error uploading data to table '{table_name}': {str(e)}")
            
   @staticmethod
   def upload_to_json(json_url):
    resp = requests.get('https://data-handling-public.s3.eu-west-1.amazonaws.com/date_details.json')
    txt = resp.json()
    data =pd.DataFrame(txt)
    #data.dropna(inplace=True)
    #data.drop_duplicates(inplace=True)

    
    return data

   @staticmethod
   def upload_to_db_3(df, table_name):
     json_url = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/date_details.json'
     df = DataCleaning.upload_to_json(json_url)
     table_name= 'dim_date_times'
     engine = DatabaseConnector.upload_db_engine()
     try:
         df.to_sql(table_name, engine, if_exists='replace', index=False)
         print(f"Data uploaded successfully to table '{table_name}' in the database.")
     except Exception as e:
            print(f"Error uploading data to table '{table_name}': {str(e)}")
    
    
    




   

dc = DataCleaning()

"""
data_cleaner = dc.clean_orders_data()
print(data_cleaner)
"""


"""
if __name__ == "__main__":
 table_name_to_read = 'orders_table'
 table_reader = DatabaseConnector.read_rds_table(table_name_to_read)
 if table_reader is not None:
   print(f"DataFrame for '{table_name_to_read}':")
   print(table_reader)
"""
"""upload orders table"""


"""upload to pg admin 4 """
"""
user_data=dc.clean_orders_data()
table_name = "orders_table"
upload_db = dc.upload_to_db_2(user_data,table_name)
"""
"""extract and clean json file"""
"""
dc = DataCleaning()
json_url = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/date_details.json'
x = dc.upload_to_json(json_url)
print(x)
"""
"""
json_url = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/date_details.json'
user_data=DataCleaning.upload_to_json(json_url)
table_name = "dim_date_times"
upload_db = DataCleaning.upload_to_db_3(user_data,table_name)
"""