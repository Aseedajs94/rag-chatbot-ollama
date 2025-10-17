"""RAG Chatbot - Streamlit UI"""

import streamlit as st
import os
import tempfile
from rag_engine import RAGEngine
from document_loader import DocumentLoader
from config import config

# Page config
st.set_page_config(
    page_title="RAG Chatbot with Ollama",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = RAGEngine()
    st.session_state.doc_loader = DocumentLoader()
    st.session_state.messages = []
    st.session_state.documents_loaded = False

# Try to load existing database
if not st.session_state.documents_loaded:
    if st.session_state.rag_engine.load_existing_vectorstore():
        st.session_state.documents_loaded = True

# Header
st.title("🤖 RAG Chatbot with Ollama")
st.markdown("**Ask questions about your documents using AI**")

# Sidebar for document upload
with st.sidebar:
    st.header("📄 Document Management")

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=['pdf', 'txt', 'docx', 'md'],
        accept_multiple_files=True,
        help="Upload PDF, TXT, DOCX, or Markdown files"
    )

    if uploaded_files:
        if st.button("Process Documents", type="primary", use_container_width=True):
            with st.spinner("Processing documents..."):
                try:
                    # Save uploaded files temporarily
                    temp_paths = []
                    for uploaded_file in uploaded_files:
                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=os.path.splitext(uploaded_file.name)[1]
                        ) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            temp_paths.append(tmp_file.name)

                    # Process documents
                    chunks = st.session_state.doc_loader.process_documents(temp_paths)

                    # Create vector store
                    num_chunks = st.session_state.rag_engine.create_vectorstore(chunks)

                    # Clean up temp files
                    for path in temp_paths:
                        try:
                            os.unlink(path)
                        except:
                            pass

                    st.session_state.documents_loaded = True
                    st.success(f"✅ Processed {len(uploaded_files)} documents into {num_chunks} chunks!")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.divider()

    # Database stats
    if st.session_state.documents_loaded:
        stats = st.session_state.rag_engine.get_stats()
        st.metric("Total Chunks", stats['total_chunks'])

        if st.button("Clear Database", use_container_width=True):
            if st.session_state.rag_engine.clear_database():
                st.session_state.documents_loaded = False
                st.session_state.messages = []
                st.success("Database cleared!")
                st.rerun()

    st.divider()

    # Settings
    st.subheader("⚙️ Settings")
    st.text(f"Model: {config.OLLAMA_MODEL}")
    st.text(f"Embeddings: {config.EMBEDDING_MODEL}")
    st.text(f"Top-K: {config.TOP_K_RESULTS}")

# Main chat interface
if not st.session_state.documents_loaded:
    st.info("👈 Upload documents in the sidebar to get started!")
else:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.rag_engine.query(prompt)

                # Display answer
                st.markdown(result['answer'])

                # Display sources if available
                if result['sources']:
                    with st.expander("📚 Sources"):
                        for i, doc in enumerate(result['sources'], 1):
                            st.markdown(f"**Source {i}:**")
                            st.text(doc.page_content[:200] + "...")
                            st.divider()

        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": result['answer']
        })

# Footer
st.divider()
st.caption("RAG Chatbot powered by Ollama, LangChain, and ChromaDB")
