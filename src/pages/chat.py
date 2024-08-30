import streamlit as st
import openai
import os
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings

def show_chat(user):
    st.title("Chat with the Streamlit docs, powered by LlamaIndex 💬🦙")
    st.info("Check out the full tutorial to build this app in our [blog post](https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/)", icon="📃")

    openai.api_key = os.environ.get("OPENAI_API_KEY")

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Hello {user.email}! Ask me a question about Streamlit's open-source Python library!",
            }
        ]

    @st.cache_resource(show_spinner=False)
    def load_data():
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        Settings.llm = OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.2,
            system_prompt="""You are an expert on 
            the Streamlit Python library and your 
            job is to answer technical questions. 
            Assume that all questions are related 
            to the Streamlit Python library. Keep 
            your answers technical and based on 
            facts – do not hallucinate features.""",
        )
        index = VectorStoreIndex.from_documents(docs)
        return index

    index = load_data()

    if "chat_engine" not in st.session_state.keys():
        st.session_state.chat_engine = index.as_chat_engine(
            chat_mode="condense_question", verbose=True, streaming=True
        )

    if prompt := st.chat_input("Ask a question"):
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            response_stream = st.session_state.chat_engine.stream_chat(prompt)
            st.write_stream(response_stream.response_gen)
            message = {"role": "assistant", "content": response_stream.response}
            st.session_state.messages.append(message)

# Make sure to include this line at the end of the file
__all__ = ['show_chat']