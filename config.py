"""Configuration for RAG Chatbot"""

class Config:
    # Ollama Settings
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "llama3.2:latest"  # Fast 3.2B model

    # Embedding Model
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast & lightweight

    # ChromaDB Settings
    CHROMA_PERSIST_DIR = "./chroma_db"
    COLLECTION_NAME = "document_qa"

    # Document Processing
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50

    # RAG Settings
    TOP_K_RESULTS = 3  # Number of relevant chunks to retrieve

    # Supported File Types
    SUPPORTED_EXTENSIONS = ['.pdf', '.txt', '.docx', '.md']

config = Config()
