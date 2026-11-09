import streamlit as st
from smartdocs.rag import index_pdf, answer_question

st.set_page_config(page_title="SmartDocs RAG Assistant", page_icon="📚", layout="centered")
st.title("📚 SmartDocs RAG Assistant")
st.caption("Ask questions about your PDF notes and see the pages used to answer.")

api_key = st.text_input("Gemini API key", type="password", help="Get a key from Google AI Studio.")
uploaded_files = st.file_uploader("Upload PDF documents", type=["pdf"], accept_multiple_files=True)

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []

if st.button("Process PDFs", type="primary", disabled=not uploaded_files or not api_key):
    try:
        with st.spinner("Reading PDFs and creating searchable chunks..."):
            st.session_state.indexed_files = []
            for pdf in uploaded_files:
                count = index_pdf(pdf.getvalue(), pdf.name, api_key)
                st.session_state.indexed_files.append((pdf.name, count))
        st.success("PDF processing completed.")
    except Exception as exc:
        st.error(f"Could not process the PDFs: {exc}")

if st.session_state.indexed_files:
    st.subheader("Processed documents")
    for name, count in st.session_state.indexed_files:
        st.write(f"• {name} — {count} text chunks")

st.divider()
st.subheader("Ask a question")
question = st.text_input("Your question", placeholder="What are the main topics in this document?")
if st.button("Get answer", disabled=not question.strip() or not api_key):
    try:
        with st.spinner("Searching your documents and preparing an answer..."):
            result, sources = answer_question(question, api_key)
        st.markdown("### Answer")
        st.write(result.answer)
        if sources:
            st.markdown("### Sources")
            for source in sources:
                st.write(f"• {source['file_name']} — page {source['page']}")
        else:
            st.info("No source pages were returned.")
    except Exception as exc:
        st.error(f"Could not answer the question: {exc}")

st.caption("This demo uses only the PDFs you upload. Answers can still be imperfect, so check the cited pages.")
