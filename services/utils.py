import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import streamlit as st

load_dotenv()

openai_client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
)

def init_session_state(force_reset=False):
    if force_reset or "uploaded_filename" not in st.session_state:
        st.session_state["uploaded_filename"] = None
    if force_reset or "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "너는 SI RFP 문서를 이해하고 대답해주는 어시스턴트야."}
        ]
    if force_reset or "summaries" not in st.session_state:
        st.session_state["summaries"] = None
    if force_reset or "chunks" not in st.session_state:
        st.session_state["chunks"] = None
    if force_reset or "tab_option" not in st.session_state:
        st.session_state["tab_option"] = "📄 요약"

def get_embedding(text, model):
    return openai_client.embeddings.create(input=text, model=model).data[0].embedding

def load_prompt_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()