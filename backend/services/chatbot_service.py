from openai import AzureOpenAI
import requests
from backend.core.config import Config


search_headers = {
    "Content-Type": "application/json",
    "api-key": Config.AZURE_SEARCH_KEY
}
search_params = {"api-version": Config.AZURE_SEARCH_API_VERSION}

openai_client = AzureOpenAI(
    api_key=Config.AZURE_OPENAI_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
)

openai_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Config.AZURE_OPENAI_API_KEY}"
}


def generate_embedding(text):
    """Generate embeddings using Azure OpenAI"""
    client = AzureOpenAI(
        api_key=Config.AZURE_OPENAI_API_KEY,
        api_version="2024-02-01",
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
    )

    response = client.embeddings.create(
        input=text,
        model=Config.EMBEDDING_DEPLOYMENT_NAME
    )

    if response and response.data:
        return response.data[0].embedding
    else:
        print("Embedding generation failed.")
        return None

def query_cognitive_search(query_vector, threshold=0.7):
    """Retrieve relevant documents without using the score field."""
    url = f"{Config.AZURE_SEARCH_ENDPOINT}/indexes/{Config.INDEX_NAME}/docs/search?api-version=2024-11-01-Preview"
    
    search_payload = {
        "search": "*", 
        "vectorQueries": [
            {
                "kind": "vector", 
                "vector": query_vector,  
                "k": 1,  # Retrieve top 5 documents
                "fields": "chunkVector"  # Specify the vector field
            }
        ],
        "select": "title,chunk",  # Removed the 'score' field from the select clause
        "queryType": "semantic",
        "semanticConfiguration": "my-semantic-config"
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": Config.AZURE_SEARCH_KEY
    }

    response = requests.post(url, json=search_payload, headers=headers)

    if response.status_code == 200:
        documents = response.json().get("value", [])
        return documents  # No filtering by score, return all documents
    else:
        print(f"Search request failed: {response.text}")
        return []





def handle_query(user_query):
    """Generate embedding & retrieve relevant policy documents"""
    query_vector = generate_embedding(user_query)  
    if not query_vector:
        return {"error": "Embedding generation failed."}

    documents = query_cognitive_search(query_vector)  

    return documents


def generate_llm_response(query, documents):
    """Use Azure OpenAI to generate a response based on retrieved policy documents"""
    if not documents:
        return "I couldn't find relevant policy information."

    context = "\n".join([f"{doc['title']}: {doc['chunk']}" for doc in documents])
    
    # Now adjust prompts for policy-specific queries
    prompt = f"""
    You are a legal assistant trained to understand and provide information from policy documents. 

    Context:
    {context}

    Question: {query}

    - Answer the question based on the provided context. 
    - If the question is unrelated to the context, reply: "I couldn't find relevant information."
    """
    print(prompt)

    response = openai_client.chat.completions.create(
        model="gpt-4o",  # You might choose a different model if needed
        messages=[
            {"role": "system", "content": "You are a legal assistant trained on policy documents."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300 # Adjust max_tokens based on expected answer length
    )

    return response.choices[0].message.content

