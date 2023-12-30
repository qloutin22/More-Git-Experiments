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
        r = requests.get(url,headers=headers)
        data = r.json()
        number_stores = 451
        for data in range(number_stores):
            url = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/'
            store_url = f"{url}{data}"
            #print(store_url)
            x = requests.get(store_url,headers=headers)
            store_data = x.json()
            #print(store_data)
            
            
        
        
        
        
    




"""de = DataExtractor()"""


"""Returns Pandas data fram from a pdf"""
"""
pdf = de.retrieve_pdf_data()
print(pdf)
"""
"""Retruen clean data"""
"""
clean_data = de.clean_card_data()
print(clean_data)

"""
"upload deails users card details to pg admin 4"
"""
user_data = de.clean_card_data()
table_name = "dim_card_details"
de.upload_to_de('self', user_data,table_name)
"""

"""Returns the amount of stores and a statues code"""
"""
header_dictionary = {'x-api-key': 'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}
stores_endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores'

number_of_stores = de.list_number_of_stores(stores_endpoint, header_dictionary)
print(f"Number of stores: {number_of_stores}")

"""
endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details'
header = {'x-api-key': 'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}
store_number = 451

rd = DataExtractor.retrieve_store_data(endpoint)
df = pd.DataFrame(sd)
print(sd)



# Example: Selecting specific columns (assuming keys are consistent across dictionaries)
#selected_keys = ['index','address','longitude', 'lat', 'locality', 'store_code', 'staff_numbers', 'opening_date','store_type', 'latitude', 'country_code','continent']
#store_df = pd.DataFrame([{key: data[key] for key in selected_keys} for data in rd])
#print(store_df)




