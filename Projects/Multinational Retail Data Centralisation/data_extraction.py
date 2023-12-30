import tabula as ta
import pandas as pd

class DataExtractor () :
    def retrieve_pdf_data(link):
        link = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
        extracted_tables = ta.read_pdf(link,stream = True)
        combined_df = pd.concat(extracted_tables)
        return combined_df
    
    
    
de = DataExtractor()

pdf = de.retrieve_pdf_data()
print(pdf)