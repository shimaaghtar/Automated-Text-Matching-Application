import os
import sys
import pandas as pd
from src.exception.exception import ProjectException
from src.logging import logger

"""
    A class for cleaning and preprocessing internal and external product datasets.
"""
class DataCleaning:

    """
        Initializes the DataCleaning class with paths to internal and external datasets.

        :param data_internal_path: Path to the internal product CSV file.
        :param data_external_path: Path to the external product CSV file.
    """
    def __init__(self,data_internal_path,data_external_path):
        self.data_internal_path = data_internal_path
        self.data_external_path = data_external_path

    """
        Cleans the internal and external datasets by:
        - Removing empty rows.
        - Removing duplicate rows.
        - Storing cleaned data in the `cleanedData` directory.
        
        :return: Paths to the cleaned internal and external datasets (CSV files).
    """    
    def data_cleaning(self):
        logger.logging.info("Data cleaning started") 
        try:
            # Read datasets from CSV files
            data_internal_df = pd.read_csv(self.data_internal_path)
            data_external_df = pd.read_csv(self.data_external_path)
            logger.logging.info("Internal and External Datasets read before cleaning") 
            
            # Remove completely empty rows from both datasets
            data_internal_df = data_internal_df.dropna(how='all')
            data_external_df = data_external_df.dropna(how='all')

            # Remove duplicate rows from both datasets
            data_internal_df = data_internal_df.drop_duplicates()
            data_external_df = data_external_df.drop_duplicates()

            logger.logging.info("Internal and External Dataset cleaned")

            # Define paths to save the cleaned datasets
            clean_internal_data_path: str = os.path.join('cleanedData','clean_internal_data.csv')
            clean_external_data_path: str = os.path.join('cleanedData','clean_external_data.csv')
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(clean_internal_data_path),exist_ok=True)
            os.makedirs(os.path.dirname(clean_external_data_path),exist_ok=True)
         
            # Save cleaned datasets to CSV files
            data_internal_df.to_csv(clean_internal_data_path, index=False)
            data_external_df.to_csv(clean_external_data_path, index=False)
            
            logger.logging.info("Cleaned Internal and External Datasets stored in clean_data folder")
       
            return clean_internal_data_path,clean_external_data_path
        
        except Exception as e:
            # Raise a custom exception in case of an error
            raise ProjectException(e,sys) 

        