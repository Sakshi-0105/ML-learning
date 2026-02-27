from email import message
import streamlit as st
from connect_memory_with_llm import qa_chain
import time

def main():
    st.title("Ask Ai")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    prompt = st.chat_input("Pass your prompt here")

    if prompt:
        # Display user message
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role': 'user', "content": prompt})

        # Show assistant message with loading indicator
        with st.chat_message('assistant'):
            # Method 1: Simple spinner
            with st.spinner('Thinking...'):
                response = qa_chain.invoke({'query': prompt})
            
            # Display the response
            st.markdown(response['result'])
        
        # Save assistant response
        st.session_state.messages.append({'role': 'assistant', "content": response['result']})


def main_with_status():
    """Alternative version with status updates"""
    st.title("Ask Ai")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    prompt = st.chat_input("Pass your prompt here")

    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role': 'user', "content": prompt})

        with st.chat_message('assistant'):
            # Method 2: Status container with updates
            status_container = st.status("Processing your request...", expanded=True)
            
            with status_container:
                st.write("🔍 Analyzing your question...")
                st.write("🤖 Consulting AI model...")
                
                response = qa_chain.invoke({'query': prompt})
                
                st.write("✅ Response ready!")
            
            status_container.update(label="Complete!", state="complete", expanded=False)
            st.markdown(response['result'])
        
        st.session_state.messages.append({'role': 'assistant', "content": response['result']})


def main_with_streaming():
    """Version with animated typing effect"""
    st.title("Ask Ai")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    prompt = st.chat_input("Pass your prompt here")

    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role': 'user', "content": prompt})

        with st.chat_message('assistant'):
            message_placeholder = st.empty()
            
            # Show loading animation
            message_placeholder.markdown("▌")
            
            # Get response
            response = qa_chain.invoke({'query': prompt})
            
            # Simulate streaming effect (optional)
            full_response = response['result']
            displayed_response = ""
            
            for char in full_response:
                displayed_response += char
                message_placeholder.markdown(displayed_response + "▌")
                time.sleep(0.01)  # Adjust speed as needed
            
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({'role': 'assistant', "content": response['result']})


def main_with_progress():
    """Version with progress bar"""
    st.title("Ask Ai")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    prompt = st.chat_input("Pass your prompt here")

    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role': 'user', "content": prompt})

        with st.chat_message('assistant'):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Processing query...")
            progress_bar.progress(30)
            
            response = qa_chain.invoke({'query': prompt})
            
            progress_bar.progress(100)
            status_text.text("Done!")
            time.sleep(0.5)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.markdown(response['result'])
        
        st.session_state.messages.append({'role': 'assistant', "content": response['result']})


if __name__ == '__main__':
    # Choose which version to run:
    # main()  # Simple spinner version
    # main_with_status()  # Status updates version
    # main_with_streaming()  # Typing animation version
    main_with_progress()  # Progress bar version