import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Enterprise AI Knowledge Assistant", layout="wide")
st.title("Enterprise AI Knowledge Assistant")

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

with st.sidebar:
    st.header("Documents")
    uploaded = st.file_uploader("Upload PDF, DOCX, TXT or CSV", type=["pdf", "docx", "txt", "csv"])
    if uploaded and st.button("Ingest document"):
        with st.spinner("Processing..."):
            r = requests.post(
                f"{API_URL}/documents/upload",
                files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                timeout=180,
            )
        st.write(r.json())

    st.subheader("Uploaded documents")
    try:
        docs = requests.get(f"{API_URL}/documents", timeout=10).json()
        for doc in docs:
            st.caption(f"{doc['document_name']} — {doc['chunks']} chunks")
    except Exception:
        st.warning("API unavailable.")

    if st.button("New conversation"):
        st.session_state.conversation_id = None
        st.rerun()

st.header("Ask your documents")
question = st.chat_input("Ask a question about your uploaded documents")

if question:
    st.chat_message("user").write(question)
    with st.spinner("Searching and generating..."):
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "question": question,
                "conversation_id": st.session_state.conversation_id,
            },
            timeout=180,
        )
    if response.ok:
        payload = response.json()
        st.session_state.conversation_id = payload["conversation_id"]
        st.chat_message("assistant").write(payload["answer"])
        with st.expander("Sources"):
            for i, source in enumerate(payload["sources"], 1):
                page = f", page {source['page']}" if source["page"] else ""
                st.markdown(f"**[S{i}] {source['document_name']}{page}** — score {source['score']}")
                st.write(source["text"])
    else:
        st.error(response.text)

st.header("Semantic search")
with st.form("search_form"):
    query = st.text_input("Search")
    submitted = st.form_submit_button("Search")
if submitted and query:
    response = requests.post(f"{API_URL}/search", json={"query": query}, timeout=60)
    if response.ok:
        for item in response.json():
            st.markdown(f"**{item['document_name']}** — score {item['score']}")
            st.write(item["text"])
    else:
        st.error(response.text)
