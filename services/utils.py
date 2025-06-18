import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import streamlit as st

openai_client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
)

def init_session_state():
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "너는 SI RFP 문서를 이해하고 대답해주는 어시스턴트야."}
        ]
    if "summaries" not in st.session_state:
        st.session_state.summaries = None
    if "chunks" not in st.session_state:
        st.session_state.chunks = None

def get_embedding(text, model):
    return openai_client.embeddings.create(input=text, model=model).data[0].embedding
