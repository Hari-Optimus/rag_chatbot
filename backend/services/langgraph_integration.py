from backend.services.chatbot_service import generate_embedding, query_cognitive_search, generate_llm_response
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, ValidationNode
from typing import Dict, TypedDict, Union, Sequence
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    Attributes:
        keys: A dictionary mapping node names to their outputs.
    """
    keys: Dict[str, Union[str, int, float, bool, Sequence[BaseMessage]]]

# Node to generate embedding
def generate_embedding_node(state: GraphState):
    """Generate embedding."""
    user_query = state['keys'].get("user_query")
    print(f"generate_embedding_node - user_query: {user_query}")  # Debug

    embedding = generate_embedding(user_query)  # Generate embedding using user_query
    print(embedding)
    if embedding:
        # Ensure we persist user_query and add the embedding to state
        state['keys']["embedding"] = embedding
        return state  # Return updated state
    state['keys']["error"] = "Embedding generation failed."
    return state  # Return state with error if embedding generation failed


# Node to perform cognitive search
def cognitive_search_node(state: GraphState):
    """Perform cognitive search."""
    user_query = state['keys'].get("user_query")  # Ensure user_query is preserved
    embedding = state['keys'].get("embedding")
    threshold = state['keys'].get("threshold", 0.7)
    documents = query_cognitive_search(embedding)
    print(documents)
    
    # Persist user_query in state to ensure it's available for later nodes
    state['keys']["user_query"] = user_query
    state['keys']["documents"] = documents
    
    print(f"cognitive_search_node - user_query: {user_query}")  # Debug
    return state  # Return state with documents added


# Node to generate LLM response
def llm_response_node(state: GraphState):
    """Generate the final LLM response."""
    user_query = state['keys'].get("user_query")  # Ensure user_query is preserved
    if user_query is None:
        return {"keys": {"response": "Error: No query provided."}}  # Return error if query is None
    
    documents = state['keys'].get("documents")
    response = generate_llm_response(user_query, documents)
    
    # Persist user_query in state
    state['keys']["user_query"] = user_query
    state['keys']["response"] = response
    
    print(f"llm_response_node - user_query: {user_query}, response: {response}")  # Debug
    return state  # Return state with final response


# Build the LangGraph flow for the chatbot
def build_chatbot_graph():
    """Build and return the LangGraph for the chatbot flow"""
    graph = StateGraph(GraphState)
    graph.add_node("generate_embedding", generate_embedding_node)
    graph.add_node("cognitive_search", cognitive_search_node)
    graph.add_node("llm_response", llm_response_node)

    # Set the flow sequence of execution
    graph.set_entry_point("generate_embedding")
    graph.add_edge("generate_embedding", "cognitive_search")
    graph.add_edge("cognitive_search", "llm_response")
    graph.add_edge("llm_response", END)

    return graph.compile()


# Run the LangGraph flow for the chatbot
def chatbot_response(user_query, threshold=0.7):
    """Run the LangGraph flow for the chatbot"""
    graph = build_chatbot_graph()

    # Create input data for the flow
    input_data = {
        "keys": {
            "user_query": user_query,
            "threshold": threshold
        }
    }

    # Execute the flow
    result = graph.invoke(input_data)
    print(f"Final Result: {result}")  # Debug to see final result

    # Extract the final response
    response = result.get('keys', {}).get('response')
    if response:
        return {"answer": response}
    else:
        return {"error": "Something went wrong in the flow."}
