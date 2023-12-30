import tabula as ta
import pandas as pd
import yaml
from yaml.loader import SafeLoader
from sqlalchemy import create_engine,MetaData,Table
from database_utils import DatabaseConnector as dc
import requests
import time
from store_data import store_data as sd

header = {'x-api-key': 'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}

class DataExtractor () :
    @staticmethod
    def retrieve_pdf_data(link):
        link = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
        extracted_tables = ta.read_pdf(link, pages = "all")
        combined_df = pd.concat(extracted_tables)
        return combined_df
    @staticmethod
    def clean_card_data ():
        link = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
        data = DataExtractor.retrieve_pdf_data(link)
        data.dropna(inplace=True)
        pd.to_datetime(data['expiry_date'],errors='coerce')
        pd.to_datetime(data['date_payment_confirmed'], errors='coerce')
        data.drop_duplicates(inplace=True)
        
        return data
    
    @staticmethod
    def upload_to_de(self,df, table_name):
     df = DataExtractor.clean_card_data()
     table_name= 'dim_card_details'
     engine = dc.upload_db_engine()
     try:
         df.to_sql (table_name, engine, if_exists='replace', index=False)
         print(f"Data uploaded successfully to table '{table_name}' in the database.")
     except Exception as e:
            print(f"Error uploading data to table '{table_name}': {str(e)}")
    
@staticmethod
def retrieve_store_data(endpoint):
        url = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/{store_number}'
        headers = {'x-api-key': 'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}
        r = requests.get(url, headers=headers)
        
        if r.status_code == 200:
            number_stores = 451
            store_data_list = []
            
            for store_number in range(number_stores):
                store_url = f"{url}{store_number}"
                response = requests.get(store_url, headers=headers)
                
                if response.status_code == 200:
                    store_data = response.json()
                    store_data_list.append(store_data)
                else:
                    print(f"Failed to retrieve data for store number {store_number}")
            
            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(store_data_list)
            return df
        else:
            print("Failed to fetch data from the API")
            return None
store_data_df = DataExtractor.retrieve_store_data('https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/')
print(store_data_df)