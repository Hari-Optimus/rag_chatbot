import json
import uuid
from fastapi import APIRouter, FastAPI, HTTPException, Depends
from azure.cosmos import CosmosClient, exceptions
from typing import Optional
from pydantic import BaseModel
from backend.services.langgraph_integration import chatbot_response
from backend.core.config import Config

# CosmosDB setup
COSMOS_DB_URI = Config.COSMOS_DB_URI
COSMOS_DB_KEY = Config.COSMOS_DB_KEY
COSMOS_DB_DATABASE = Config.COSMOS_DB_DATABASE
COSMOS_DB_CONTAINER = Config.COSMOS_DB_CONTAINER

client = CosmosClient(COSMOS_DB_URI, COSMOS_DB_KEY)
database = client.get_database_client(COSMOS_DB_DATABASE)
container = database.get_container_client(COSMOS_DB_CONTAINER)

router = APIRouter()
app = FastAPI()

class UserQuery(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

def store_message(user_id: str, session_id: str, role: str, content: str):
    """Store a conversation message in CosmosDB."""
    try:
        item = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'session_id': session_id,
            'role': role,
            'content': content
        }
        container.create_item(body=item)
    except exceptions.CosmosResourceExistsError:
        raise HTTPException(status_code=400, detail="Message already exists")

def get_messages(user_id: str, session_id: str):
    """Retrieve the conversation history for a given user_id and session_id."""
    query = f"SELECT * FROM c WHERE c.user_id = '{user_id}' AND c.session_id = '{session_id}' ORDER BY c.id"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    return items

@router.post("/chat-llm")
def chat_with_llm(user_query: UserQuery):
    """Handle chat requests and store messages in CosmosDB."""
    # Retrieve conversation history if user_id and session_id are present
    messages = []
    if user_query.user_id and user_query.session_id:
        messages = get_messages(user_query.user_id, user_query.session_id)
    
    print(user_query.user_id)
    print(user_query.session_id)
    print(messages)
    # Add user query to messages
    store_message(user_query.user_id, user_query.session_id, "user", user_query.query)
    
    # Prepare context for the chatbot
    context = "\n".join([msg['content'] for msg in messages])
    
    # Add messages to the state (used by LangGraph)
    previous_messages = [{"role": msg['role'], "content": msg['content']} for msg in messages]
    print(previous_messages)
    # Get the assistant's response
    print(user_query.query+"Test for query")
    answer = chatbot_response(user_query.query, context=context, previous_messages=previous_messages)
    
    
    # Store assistant response in CosmosDB
    store_message(user_query.user_id, user_query.session_id, "assistant", answer['answer'])
    
    
    return {"answer": answer['answer']}


# @router.post("/clear-database")
# def clear_database():
#     """Clear all the data in the CosmosDB container."""
#     try:
#         # Delete all items from the CosmosDB container
#         container.delete_all_items()
#         from azure.cosmos import CosmosClient, exceptions
#         query = "SELECT * FROM c"
#         items = list(container.query_items(query, enable_cross_partition_query=True))S
    
#         # Delete each item
#         for item in items:
#             container.delete_item(item, partition_key=item['user_id'])
    
#         print(f"All data from container has been deleted.")
#     except exceptions.CosmosResourceNotFoundError:
#         raise HTTPException(status_code=400, detail="Failed to clear the database")


