import tabula as ta
import pandas as pd
import yaml
from yaml.loader import SafeLoader
from sqlalchemy import create_engine,MetaData,Table
from database_utils import DatabaseConnector as dc
import requests
import boto3
from io import StringIO
import re


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
        #data.dropna(inplace=True)
        pd.to_datetime(data['expiry_date'], errors='coerce')
        pd.to_datetime(data['date_payment_confirmed'], errors='coerce',format='%Y-%m-%d')
        data.drop_duplicates(inplace=True)
        data['card_number'] = data['card_number'].astype('string')
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
        headers = {'x-api-key': 'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}
        store_data_list = []
        
        for store_number in range(451):  
            store_url = f"{endpoint}/{store_number}"
            response = requests.get(store_url, headers=headers)
            
            if response.status_code == 200:
                store_data = response.json()
                store_data_list.append(store_data)
            else:
                print(f"Failed to retrieve data for store number {store_number}")
        df = pd.DataFrame(store_data_list)
        return df
    
    @staticmethod
    def called_clean_store_data():
        endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details'
        user_data = DataExtractor.retrieve_store_data(endpoint)
        #user_data.dropna(inplace=True)
        user_data.drop_duplicates(inplace=True)
        user_data['longitude'] = user_data['longitude'].astype('string') 
        user_data['locality'] = user_data['locality'].astype('string') 
        user_data['store_code'] = user_data['store_code'].astype('string')
        user_data.drop_duplicates(subset=['store_code'], inplace=True)
        user_data['staff_numbers'] = user_data['staff_numbers'].astype('string' )
        #user_data['opening_date'] = pd.to_datetime(user_data['opening_date'],errors='coerce') 
        user_data['store_type'] = user_data['store_type'].astype('string') 
        user_data['latitude'] = user_data['latitude'].astype('string')
        user_data['country_code'] = user_data['country_code'].astype('string')
        user_data['continent'] = user_data['continent'].astype('string') 
        user_data['opening_date'] = pd.to_datetime(user_data['opening_date'],format='%Y-%m-%d',errors='coerce')
        #user_data['opening_date'] = pd.to_datetime(user_data['opening_date'],errors='coerce')
        
        return user_data
    
    @staticmethod
    def upload_to_db(self,df, table_name):
     df = DataExtractor.called_clean_store_data()
     table_name= 'dim_store_details'
     engine = DataExtractor.upload_db_engine()
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
 
    @staticmethod
    def extract_from_s3(s3_address):
        s3 = boto3.client('s3')
        bucket_name = s3_address.split('//')[1].split('/')[0]
        file_path = '/'.join(s3_address.split('//')[1].split('/')[1:])
        obj = s3.get_object(Bucket=bucket_name, Key=file_path)
        data = obj['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(data))
        return df
    
    @staticmethod
    def convert_product_weights(products_df):
        products_df.dropna(subset=['weight'], inplace=True)
        def clean_and_convert_weight(weight):
            pattern = r'(\d*\.?\d+)'
            match = re.search(pattern, weight)
            if match:
                value = float(match.group())  
                unit = weight[match.end():].strip().lower() 
                if unit == 'kg':
                    if value < 1:
                        return value *10
                    return value
                elif unit == 'g':
                    return value * 0.001  
                elif unit == 'ml':
                    return value * 0.001 
                elif unit == 'oz':
                    return value * 0.0283495  
                else:
                    return None 
            else:
                return None  
            
        products_df['weight'] = products_df['weight'].astype('string')  
        #products_df['weight'] = products_df['weight'].apply(lambda x: re.sub(r'[^\d\.]', '', x))  
        products_df['weight_in_kg'] = products_df['weight'].apply(clean_and_convert_weight)
        #products_df = products_df.dropna(subset=['weight_in_kg'])
        

        return products_df
    @staticmethod
    def clean_user_data():
        s3_address = 's3://data-handling-public/products.csv'
        products_df = de.extract_from_s3(s3_address)
        user_data = de.convert_product_weights(products_df)
        user_data.dropna(inplace=True)
        user_data['date_added'] = pd.to_datetime(user_data['date_added'],errors='coerce')
        #user_data.drop_duplicates(inplace=True)
        user_data['product_code'] = user_data['product_code'].astype('string')
        #user_data['expiry_date'] = pd.to_datetime(user_data['expiry_date'], format='%Y-%m-%d')
        user_data['expiry_date'] = pd.to_datetime(user_data['expiry_date'],errors='coerce')
        user_data['expiry_date'] = pd.to_datetime(user_data['expiry_date'], format='%Y-%m-%d')


        return user_data

    @staticmethod
    def upload_to_db_2(df, table_name):
     df = de.clean_user_data()
     table_name= 'dim_products'
     engine = de.upload_db_engine()
     try:
         df.to_sql(table_name, engine, if_exists='replace', index=False)
         print(f"Data uploaded successfully to table '{table_name}' in the database.")
     except Exception as e:
            print(f"Error uploading data to table '{table_name}': {str(e)}")
   
        



        
        



de = DataExtractor()


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
"""Returns pandas data fram from a list of dictonaries"""
"""
endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details'
header = {'x-api-key': 'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}
store_number = 451

rd = DataExtractor.retrieve_store_data(endpoint)
df = pd.DataFrame(sd)
print(rd)
"""

"""Code to clean store data"""
"""
clean_store_data = de.called_clean_store_data()
print(clean_store_data)
"""

"""upload to database"""


user_data=de.called_clean_store_data()
table_name = "dim_store_details"
upload_db = de.upload_to_db('self', user_data,table_name)


"""prints addresses"""
"""
s3_address= 's3://data-handling-public/products.csv'
s3_address_ = de._parse_s3_address(s3_address)
print(s3_address_)
"""
"""convert to database"""
"""
s3_address= 's3://data-handling-public/products.csv'
extract = de.extract_from_s3(s3_address)
print(extract)
"""

"""clean user data"""
"""
s3_address= 's3://data-handling-public/products.csv'
products_df = de.extract_from_s3(s3_address)
cleaned_products_data = de.convert_product_weights(products_df)
print(cleaned_products_data)  
"""
"""

s3_address= 's3://data-handling-public/products.csv'
products_df = de.extract_from_s3(s3_address)
user_data = de.convert_product_weights(products_df)
#cleaned_user_data = de.clean_user_data()
table_name = 'dim_products'
de.upload_to_db_2(user_data,table_name)

"""


