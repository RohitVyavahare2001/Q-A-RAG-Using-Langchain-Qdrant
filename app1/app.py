import streamlit as st
import requests
import json
import uuid
from typing import Optional

# FastAPI endpoint URL
API_URL = "http://127.0.0.1:8000"

def main():
    st.title("Document Q&A System")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None:
            if st.button("Process Document"):
                with st.spinner("Processing document..."):
                    try:
                        files = {"file": uploaded_file}
                        response = requests.post(f"{API_URL}/upload-pdf/", files=files)
                        if response.status_code == 200:
                            st.success("Document uploaded and processed successfully!")
                            st.write(response.json())  # Show the response details
                        else:
                            st.error(f"Error processing document: {response.text}")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")

    # Main chat interface
    st.header("Chat with your Document")
    
    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your document"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Call chat API
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "question": prompt,
                    "session_id": st.session_state.session_id
                }
                st.write("Sending request:", payload)  # Debug info
                
                response = requests.post(
                    f"{API_URL}/chat/",
                    json=payload,
                    timeout=30  # Add timeout
                )
                
                st.write("Response status:", response.status_code)  # Debug info
                st.write("Response content:", response.text)  # Debug info
                
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    with st.chat_message("assistant"):
                        st.write(answer)
                else:
                    st.error(f"API Error: {response.text}")
            
            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the API. Is the server running?")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Chat history
    if st.button("Show Chat History"):
        try:
            response = requests.get(
                f"{API_URL}/chat-history/{st.session_state.session_id}"
            )
            if response.status_code == 200:
                history = response.json()
                st.subheader("Chat History")
                for entry in history:
                    st.text(f"Q: {entry['question']}")
                    st.text(f"A: {entry['answer']}")
                    st.text("---")
            else:
                st.error(f"Error fetching chat history: {response.text}")
        except Exception as e:
            st.error(f"Error fetching chat history: {str(e)}")

    # Debug information
    with st.expander("Debug Information"):
        st.write("Session ID:", st.session_state.session_id)
        st.write("API URL:", API_URL)
        st.write("Number of messages:", len(st.session_state.messages))

if __name__ == "__main__":
    main()