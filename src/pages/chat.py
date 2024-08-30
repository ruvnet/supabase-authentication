import streamlit as st
import openai
import os
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext, load_index_from_storage

# Initialize session state
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = {}

if "model" not in st.session_state:
    st.session_state.model = "gpt-4o"

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

if "top_p" not in st.session_state:
    st.session_state.top_p = 1.0

# Set up OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

def print_data_contents():
    data_dir = "./data"
    st.sidebar.write("Contents of ./data directory:")
    for filename in os.listdir(data_dir):
        file_path = os.path.join(data_dir, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
                st.sidebar.text_area(f"Contents of {filename}:", content, height=200)

@st.cache_resource(show_spinner=False)
def load_data():
    if os.path.exists("./index"):
        storage_context = StorageContext.from_defaults(persist_dir="./index")
        index = load_index_from_storage(storage_context)
    else:
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        st.sidebar.write(f"Number of documents loaded: {len(docs)}")
        if docs:
            for i, doc in enumerate(docs):
                st.sidebar.write(f"Document {i+1} content (truncated):\n{doc.text[:200]}...")
        Settings.llm = OpenAI(model=st.session_state.model, temperature=st.session_state.temperature)
        index = VectorStoreIndex.from_documents(docs)
        index.storage_context.persist("./index")
    return index

index = load_data()

def update_chat_engine():
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_question",
        verbose=True,
        streaming=True,
        llm=OpenAI(model=st.session_state.model, temperature=st.session_state.temperature, top_p=st.session_state.top_p)
    )

if "chat_engine" not in st.session_state:
    update_chat_engine()

def generate_response(prompt):
    name = st.session_state.user_name
    context = st.session_state.conversation_context
    system_prompt = f"""You are a friendly and helpful AI assistant named AI Assistant.
    You have a conversation history and can remember details about the user.
    The user's name is {name if name else 'unknown'}.
    Current context: {context}
    You should use this information to personalize your responses.
    If you don't know something about the user, admit that you don't know rather than making assumptions.
    Always be polite, engaging, and try to keep the conversation flowing naturally.
    When the user shares information about themselves, acknowledge it and remember it for future use.
    """

    if "my name is" in prompt.lower():
        name = prompt.lower().split("my name is")[-1].strip()
        st.session_state.user_name = name
        context['name'] = name
        return f"Nice to meet you, {name}! I'll remember that. How can I assist you today?"

    if "live in" in prompt.lower() or "from" in prompt.lower():
        location = prompt.lower().split("live in")[-1].strip() if "live in" in prompt.lower() else prompt.lower().split("from")[-1].strip()
        context["location"] = location
        return f"Thank you for letting me know that you're from {location}, {name}. I'll remember that for future conversations. Is there anything specific about {location} you'd like to discuss?"

    if "what's my name" in prompt.lower() or "what is my name" in prompt.lower():
        if name:
            return f"Your name is {name}. I remember it because you told me earlier!"
        else:
            return "I'm sorry, but I don't know your name yet. Would you like to tell me?"

    if "where do i live" in prompt.lower() or "where am i from" in prompt.lower():
        if "location" in context:
            return f"Based on what you've told me, you live in {context['location']}. Is there anything specific about {context['location']} you'd like to know?"
        else:
            return "I'm sorry, but I don't have any information about where you live. Would you like to tell me?"

    if "tell me about yourself" in prompt.lower():
        return "I'm an AI assistant created to help with a wide range of topics. I don't have personal experiences, but I'm here to assist you with information, answer questions, or discuss any topic you're interested in. Is there a particular subject you'd like to explore?"

    if "i like" in prompt.lower() or "my favorite" in prompt.lower():
        preference = prompt.lower().split("i like")[-1].strip() if "i like" in prompt.lower() else prompt.lower().split("my favorite")[-1].strip()
        context.setdefault("preferences", []).append(preference)
        return f"That's interesting, {name}! I'll remember that you like {preference}. Would you like to discuss more about it or explore related topics?"

    full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAI Assistant:"
    response_stream = st.session_state.chat_engine.stream_chat(full_prompt)
    return response_stream

def test_data_retrieval():
    test_query = "What are the main types of machine learning?"
    st.sidebar.write("Test Query:", test_query)
    response = generate_response(test_query)
    if isinstance(response, str):
        st.sidebar.write("Response:", response)
    else: # It's a stream
        full_response = ""
        for chunk in response.response_gen:
            full_response += chunk
        st.sidebar.write("Response:", full_response)

def chat():
    st.title("Memory-Enabled RAG Chatbot")

    if "conversation_context" not in st.session_state:
        st.session_state.conversation_context = {}

    # Sidebar for model settings and data verification
    st.sidebar.title("Model Settings and Data Verification")
    st.session_state.model = st.sidebar.selectbox(
        "Select Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        index=0
    )
    st.session_state.temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    st.session_state.top_p = st.sidebar.slider("Top P", 0.0, 1.0, 1.0, 0.1)

    # Update chat engine when settings change
    if st.sidebar.button("Apply Settings"):
        update_chat_engine()

    # Print data contents and test data retrieval
    print_data_contents()
    if st.sidebar.button("Test Data Retrieval"):
        test_data_retrieval()

    if not st.session_state.user_name:
        st.session_state.user_name = st.text_input("What's your name?")
        if st.session_state.user_name:
            st.session_state.conversation_context['name'] = st.session_state.user_name
            st.success(f"Nice to meet you, {st.session_state.user_name}!")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to talk about?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = generate_response(prompt)
            if isinstance(response, str):
                st.markdown(response)
                final_response = response
            else: # It's a stream
                response_placeholder = st.empty()
                full_response = ""
                for chunk in response.response_gen:
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
                final_response = full_response

        st.session_state.messages.append({"role": "assistant", "content": final_response})

if __name__ == "__main__":
    chat()