import streamlit as st
import time
import requests
 
API_URL = "http://127.0.0.1:8001/api/api/chat-llm"
 
# Initialize session state variables if not already set
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
 
# Add the initial greeting message if it's not already there
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": "Hello, I am your financial assistant. How may I help you?"})
 
# Display all chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
 
# User input section
user_input = st.chat_input("Ask your financial question...")
 
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
 
                with requests.post(API_URL, json={"query": user_input}, params=params, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=None):
                        decoded_chunk = chunk.decode()
                        if "[[SESSION::" in decoded_chunk:
                            # Extract session data
                            parts = decoded_chunk.strip("[]").split("::")
                            if len(parts) == 3:
                                st.session_state.user_id = parts[1]
                                st.session_state.session_id = parts[2]
                        else:
                            full_response += decoded_chunk
                            response_placeholder.markdown(full_response + "▌")  # Typing effect
 
                    response_placeholder.markdown(full_response)
 
            except Exception as e:
                full_response = f"Error fetching response: {e}"
                response_placeholder.markdown(full_response)
 
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})