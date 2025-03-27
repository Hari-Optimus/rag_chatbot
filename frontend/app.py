import streamlit as st
import time
import requests
import uuid
API_URL = "http://127.0.0.1:8000/api/chat-llm"

# API_URL_CLEAR = "http://127.0.0.1:8000/api/clear-database"

# # Add a button to clear the database
# if st.button("Clear All Data"):
#     try:
#         response = requests.post(API_URL_CLEAR)

#         if response.status_code == 200:
#             st.success("All data has been deleted successfully.")
#         else:
#             st.error(f"Failed to clear the database: {response.text}")

#     except Exception as e:
#         st.error(f"Error occurred while clearing the database: {e}")
# Initialize session state variables if not already set
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
 
# Add the initial greeting message if it's not already there
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": "Hello, I am your Policy assistant. How may I help you?"})
 
# Display all chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
 
# User input section
user_input = st.chat_input("Ask your Policy related question...")
 
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
 
    bot_placeholder = st.chat_message("assistant")
    response_placeholder = bot_placeholder.empty()
    full_response = ""
 
    with bot_placeholder:
        with st.spinner("Thinking..."):
            try:
                params = {}
                if st.session_state.user_id and st.session_state.session_id:
                    params = {"user_id": st.session_state.user_id, "session_id": st.session_state.session_id}
 
                with requests.post(API_URL, json={"query": user_input, "user_id": st.session_state.user_id,"session_id": st.session_state.session_id}, stream=True) as r:
                    r.raise_for_status()

                    # Extract the 'answer' field from the response JSON
                    response_data = r.json()  # Parsing the JSON response
                    answer = response_data.get("answer", "Sorry, I couldn't find an answer.")

                    # **Chunking behavior** as per your previous approach:
                    full_response = ""
                    for chunk in answer:
                        full_response += chunk  # Append each chunk progressively
                        response_placeholder.markdown(full_response + "▌")  # Display the response with typing effect

                    # After all chunks are displayed, remove the typing cursor
                    response_placeholder.markdown(full_response)
 
            except Exception as e:
                full_response = f"Error fetching response: {e}"
                response_placeholder.markdown(full_response)
 
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})