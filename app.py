# app.py (User Interface)
import streamlit as st
import pandas as pd
import os
from src.logging import logger
from src.exception.exception import ProjectException
from src.components.data_cleaning import DataCleaning
from src.components.find_match import FindMatch



def main():
    """
    Main function to run the Streamlit application for text matching.
    """
    st.set_page_config(page_title="Text Matching Application", layout="wide")
    
    # Set up the Streamlit UI layout and title
    
    st.title("🔍 Text Matching Application")
    st.markdown("### Upload two CSV files to match text fields.")

    # File uploaders for internal and external data
    col1, col2 = st.columns(2)
    with col1:
        internal_file = st.file_uploader("Upload Internal Data (Data_Internal.csv)", type=["csv"])
    with col2:
        external_file = st.file_uploader("Upload External Data (Data_External.csv)", type=["csv"])
    
    # Create a temporary directory to store uploaded files
    os.makedirs("tempData",exist_ok=True)
    internal_path = os.path.join("tempData", "Data_Internal.csv")
    external_path = os.path.join("tempData", "Data_External.csv")

    if internal_file and external_file:
        st.success("Files uploaded successfully!")

        try:
        # Save uploaded files to a temporary directory
            with open(internal_path, "wb") as f:
                f.write(internal_file.getbuffer())
                logger.logging.info("Data Ingestion started")
            with open(external_path, "wb") as f:
                f.write(external_file.getbuffer())
        except Exception as e:
                raise ProjectException(f"Error saving uploaded files: {str(e)}",e)
        
        with st.spinner("Processing matches..."):
            try:
                result_df =pd.DataFrame()

                # Perform data cleaning
                DC_object = DataCleaning(internal_path,external_path)
                cleaned_data_internal_path, cleaned_data_external_path = DC_object.data_cleaning()

                # Perform text matching
                FM_object = FindMatch(cleaned_data_internal_path,cleaned_data_external_path)
                result_df = FM_object.find_match()
                
                
            except Exception as e:
                    raise ProjectException(f"Error processing matches: {str(e)}",e)
            # Display the matching results
            st.success("Matching completed!")
            #st.table(result_df.reset_index(drop=True))
            st.dataframe(result_df)
            logger.logging.info("Matching completed - The result is displayed on the web page")
            
            try:
                # Provide a download button for matched results
                csv = result_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Results", data=csv, file_name="matched_product_names.csv", mime="text/csv")
            except Exception as e:
                raise ProjectException(f"Error creating download file: {str(e)}",e)    
            
if __name__ == "__main__":
    
    main()        
