from azure.cosmos import CosmosClient, PartitionKey
from backend.core.config import Config

# CosmosDB setup
COSMOS_DB_URI = Config.COSMOS_DB_URI
COSMOS_DB_KEY = Config.COSMOS_DB_KEY
COSMOS_DB_DATABASE = Config.COSMOS_DB_DATABASE
COSMOS_DB_CONTAINER = Config.COSMOS_DB_CONTAINER
# Initialize Cosmos DB client
client = CosmosClient(COSMOS_DB_URI, COSMOS_DB_KEY)

# Create database (if it does not exist)
database = client.create_database_if_not_exists(COSMOS_DB_DATABASE)

# Create container (if it does not exist)
container = database.create_container_if_not_exists(
    id=COSMOS_DB_CONTAINER,
    partition_key=PartitionKey(path="/user_id"),  # Using user_id as the partition key
    offer_throughput=400  # Define throughput (this can be adjusted based on expected usage)
)
