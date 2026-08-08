import streamlit as st
from indexer import index_repo
from rag_engine import ask_question

st.set_page_config(page_title="Codebase Onboarding Assistant", layout="wide")
st.title("🧠 Codebase Onboarding Assistant")

tab1, tab2 = st.tabs(["📥 Index a Repo", "💬 Ask Questions"])

with tab1:
    github_url = st.text_input("GitHub repo URL", "https://github.com/tiangolo/full-stack-fastapi-template")
    if st.button("Index Codebase"):
        with st.spinner("Cloning, parsing, and embedding... this takes a minute"):
            result = index_repo(github_url)
        st.success(f"Indexed {result['chunks']} code chunks from {result['files']} files")

with tab2:
    question = st.text_input("Ask a question about the codebase", "Where is authentication handled?")
    if st.button("Ask"):
        with st.spinner("Thinking..."):
            result = ask_question(question)
        st.markdown("### Answer")
        st.write(result["answer"])
        st.markdown("### Sources")
        for s in result["sources"]:
            meta = s["metadata"]
            with st.expander(f"{meta['file_path']} — {meta['name']} (lines {meta['start_line']}-{meta['end_line']})"):
                st.code(s["document"], language="python")
                st.caption(f"Recent commits: {meta['commits']}")