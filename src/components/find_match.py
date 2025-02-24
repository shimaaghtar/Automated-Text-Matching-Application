import pandas as pd
import os,sys
import json
from itertools import chain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pinecone import Pinecone,ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from src.logging import logger
from src.exception.exception import ProjectException
from io import StringIO

"""
    Class responsible for matching external product names with internal product names
    using vector similarity search and LLM validation.
"""
class FindMatch:

    """
        Initializes the class with paths to cleaned internal and external datasets.
        :param clean_data_internal_path: Path to cleaned internal product dataset (CSV file.
        :param clean_data_external_path: Path to cleaned external product dataset (CSV file).
    """
    def __init__(self,clean_data_internal_path,clean_data_external_path):
        
        try:
            self.internal_df = pd.read_csv(clean_data_internal_path)
            self.external_df = pd.read_csv(clean_data_external_path)
        except Exception as e:
            # Raise a custom exception in case of an error
            raise ProjectException(e,sys)    

    """
        Stores internal product  embeddings in Pinecone in batches.
        :param vectors: List of vector embeddings.
        :param pinecone: Pinecone instance.
        :param index_name: Name of the Pinecone index.
        :param batch_size: Number of records to upsert at a time.
    """
    def _batch_upsert(self, vectors,pinecone,index_name, batch_size=100):
        for i in range(0, len(self.internal_df), batch_size):
            batch = [
            (str(idx), vectors[idx], {"search_text": self.internal_df.iloc[idx]["search_text"]})
            for idx in range(i, min(i + batch_size, len(self.internal_df)))
            ]
            index = pinecone.Index(index_name)
            index.upsert(batch)  #  Upsert batch to Pinecone
            logger.logging.info(f"*** Upserted {i + batch_size}/{len(self.internal_df)} records")

    """
        Finds the most similar internal product for each external product using Pinecone vector search.
        :param external_list: List of external product names.
        :param embeddings: OpenAI embeddings instance.
        :param pinecone: Pinecone instance.
        :param index_name: Pinecone index name.
        :return: List of matched internal product names.
        """
    def _find_most_similar_internal_name(self,external_list,embeddings,pinecone,index_name):
        
        ## Found the matched internal products of each external products
        internal_product_for_query = []
        index = pinecone.Index(index_name)
        for external_text in external_list:
            query_embedding = embeddings.embed_query(external_text)  
            results = index.query(
                vector=query_embedding,  
                top_k=1,
                include_values=False,
                include_metadata=True
            )
            matched_internal_products = [match['metadata']['search_text'] for match in results['matches']]
            internal_product_for_query.extend(matched_internal_products) 
        return internal_product_for_query       
    
    """
        Embeds and stores internal product names in Pinecone.
        :param embeddings: OpenAI embeddings instance.
        :param pinecone: Pinecone instance.
        :return: Name of the created Pinecone index.
    """
    def _store_internal_products_embeddings(self,embeddings,pinecone):

        cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
        region = os.environ.get('PINECONE_REGION') or 'us-east-1'
        spec = ServerlessSpec(cloud=cloud, region=region)
        index_name = "text-matching1"
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(name=index_name, metric="cosine", dimension=1536,spec=spec)
        index = pinecone.Index(index_name)
        internal_vectors = embeddings.embed_documents(self.internal_df["search_text"].tolist())
        BATCH_SIZE = 200
        self._batch_upsert(internal_vectors,pinecone,index_name, BATCH_SIZE)
        return index_name
    
    """
        Uses GPT-4 to validate the best-matched internal product based on Manufacturer, Name, and Size.
        :param llm: LLM instance (GPT-4 via LangChain).
        :param external_list: List of external products.
        :param internal_product_for_query: List of best-matched internal products from Pinecone.
        :return: LLM response containing matched results.
    """
    def _validate_match_with_llm(self,llm,external_list,internal_product_for_query):
        
        prompt_template = PromptTemplate(
            input_variables=["external_products", "internal_products"],
            template='''You are a product owner. You have two lists of product names: Internal products and External products.
            Your task is to compare each **external product** with all **internal products** to determine if there is a match.

                ### **Matching Criteria:**
                    - **Manufacturer:** Normalize by removing extra spaces and converting to lowercase. Both Manufacturer must be identical for a match.
                    - **Name:** Normalize by removing extra spaces and converting to lowercase. Both name must be identical for a match.
                    - **Size:** Both sizes must be identical for a match.
                 
                ### **Expected tabular output seperated by comma **
                  -if no matches are found, return empty table. The index column is excluded from the table. The table header is ["External_Product_Name","Internal_Product_Name"].The table includes the below columns and contents:
                    - `"External_Product_Name"`: The external product name.
                    - `"Internal_Product_Name"`: NULL if (the Manufacturer or Name or size are not identical) ; otherwise, return the matched internal product name before the first comma
                          
                ### **Here are the products to match:**
                    - **External Products:** {external_products}
                    - **Internal Products:** {internal_products}

                ** Do not include any explanations.**'''
        )
        prompt = prompt_template.format(external_products= external_list, internal_products=internal_product_for_query)
        messages = [{"role": "user", "content": prompt}]
        response = llm.invoke(messages)
        return response.content
        
    """
        Executes the full matching process: embedding, vector search, and LLM validation.
        :return: DataFrame of matched products.
    """
    def find_match(self):
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        pinecone_api_key=os.getenv("PINECONE_API_KEY")
        pinecone = Pinecone(api_key=pinecone_api_key)
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        llm = ChatOpenAI(model="gpt-4-turbo", api_key=openai_api_key,temperature=0,top_p=0)

        # Merge NAME, OCS_NAME, LONG_NAME into one search column 
        self.internal_df["search_text"] = self.internal_df[["NAME", "OCS_NAME", "LONG_NAME"]].fillna("").agg(", ".join, axis=1)
        index_name = "text-matching1"
        index_name = self._store_internal_products_embeddings(embeddings,pinecone)
        logger.logging.info("Embedded Internal Product Name is stored in Pinecone Vector DB") 
        
        external_list = self.external_df["PRODUCT_NAME"].to_list()
        
        similar_internal_product_for_validation = self._find_most_similar_internal_name(external_list,embeddings,pinecone,index_name)
        logger.logging.info("The most similar External products to Internal produts are retrieved from vectore DB") 
        response = self._validate_match_with_llm(llm,external_list,similar_internal_product_for_validation)
        logger.logging.info("Final match list is validated by LLM") 
        result_df = pd.read_csv(StringIO(response.lstrip("```plaintext").rstrip("```")))
        result_df = result_df.fillna("NULL")
        logger.logging.info("LLM output is converted to dataframe") 
        return result_df

        


    
    
         

