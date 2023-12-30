import tabula as ta
import pandas as pd

class DataExtractor():
    def retrieve_pdf_data(self, link):
        extracted_tables = ta.read_pdf(link, pages='all', multiple_tables=True)
        combined_df = pd.concat(extracted_tables)
        return combined_df

# Create an instance of DataExtractor
data_extractor = DataExtractor()

# Call the retrieve_pdf_data method providing the PDF link
pdf_link = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
result_df = data_extractor.retrieve_pdf_data(pdf_link)

