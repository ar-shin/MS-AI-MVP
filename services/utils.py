import streamlit as st

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "너는 SI RFP 문서를 이해하고 대답해주는 어시스턴트야."}
        ]
    if "summaries" not in st.session_state:
        st.session_state.summaries = None
    if "chunks" not in st.session_state:
        st.session_state.chunks = None