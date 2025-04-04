import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_API_KEY")
    AZURE_SEARCH_API_VERSION = os.getenv("AZURE_SEARCH_API_VERSION")
    
    BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
    BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
    
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    
    EMBEDDING_DEPLOYMENT_NAME = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
    
    COG_SERVICE_NAME = os.getenv("COG_SERVICES_NAME")
    COG_SERVICES_KEY = os.getenv("COG_SERVICES_KEY")

    DATASOURCE_NAME = os.getenv("DATASOURCE_NAME")
    INDEX_NAME = os.getenv("INDEX_NAME")
    SKILLSET_NAME = os.getenv("SKILLSET_NAME")
    INDEXER_NAME = os.getenv("INDEXER_NAME")
   
