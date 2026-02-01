import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/query"

st.set_page_config(page_title="Agentic RAG Assistant", layout="centered")

st.title("🤖 Agentic RAG System")
st.caption("Ask questions across company documents using AI agents")

query = st.text_area("Enter your question:")

if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a question")
    else:
        with st.spinner("Thinking..."):
            response = requests.post(
                API_URL,
                json={"question": query},
                timeout=60
            )

        if response.status_code == 200:
            st.success("Answer")
            st.write(response.json()["answer"])
        else:
            st.error("Something went wrong")
