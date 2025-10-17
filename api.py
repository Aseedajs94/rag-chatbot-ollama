"""FastAPI Backend for RAG Chatbot - Separates Backend from Frontend"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os
import shutil

from rag_engine import RAGEngine
from document_loader import DocumentLoader
from config import config

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="RESTful API for Document Q&A using RAG (Retrieval-Augmented Generation)",
    version="1.0.0"
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG components
rag_engine = RAGEngine()
document_loader = DocumentLoader()

# Try to load existing vector store on startup
rag_engine.load_existing_vectorstore()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

class UploadResponse(BaseModel):
    message: str
    total_chunks: int
    files_processed: int

class StatsResponse(BaseModel):
    total_chunks: int
    collection_name: str
    ollama_model: str
    embedding_model: str

class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    vectorstore_loaded: bool


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info"""
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    # Check if Ollama is accessible
    ollama_connected = True
    try:
        # Simple test query
        test_result = rag_engine.llm.invoke("test")
        ollama_connected = True
    except:
        ollama_connected = False

    vectorstore_loaded = rag_engine.vectorstore is not None

    return {
        "status": "healthy" if ollama_connected else "degraded",
        "ollama_connected": ollama_connected,
        "vectorstore_loaded": vectorstore_loaded
    }


@app.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and process documents to build the knowledge base

    Supports: PDF, TXT, DOCX, MD files
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    temp_files = []
    try:
        # Save uploaded files temporarily
        for uploaded_file in files:
            # Validate file extension
            file_ext = os.path.splitext(uploaded_file.filename)[1].lower()
            if file_ext not in config.SUPPORTED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_ext}. Supported: {config.SUPPORTED_EXTENSIONS}"
                )

            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                shutil.copyfileobj(uploaded_file.file, temp_file)
                temp_files.append(temp_file.name)

        # Process documents
        chunks = document_loader.process_documents(temp_files)

        if not chunks:
            raise HTTPException(status_code=400, detail="No content extracted from documents")

        # Create/update vector store
        total_chunks = rag_engine.create_vectorstore(chunks)

        return {
            "message": "Documents processed successfully",
            "total_chunks": total_chunks,
            "files_processed": len(files)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


@app.post("/query", response_model=QueryResponse, tags=["Q&A"])
async def query_documents(request: QueryRequest):
    """
    Ask a question about the uploaded documents

    Returns answer with source citations
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # Query the RAG system
        result = rag_engine.query(request.question)

        # Format sources for JSON response
        sources = []
        for doc in result['sources']:
            sources.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })

        return {
            "answer": result['answer'],
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_statistics():
    """Get database and system statistics"""
    stats = rag_engine.get_stats()

    return {
        "total_chunks": stats.get('total_chunks', 0),
        "collection_name": config.COLLECTION_NAME,
        "ollama_model": config.OLLAMA_MODEL,
        "embedding_model": "nomic-embed-text"
    }


@app.delete("/clear", tags=["Database"])
async def clear_database():
    """Clear all documents from the vector database"""
    try:
        success = rag_engine.clear_database()

        if success:
            return {"message": "Database cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")


@app.get("/config", tags=["Configuration"])
async def get_configuration():
    """Get current system configuration"""
    return {
        "ollama_base_url": config.OLLAMA_BASE_URL,
        "ollama_model": config.OLLAMA_MODEL,
        "collection_name": config.COLLECTION_NAME,
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
        "top_k_results": config.TOP_K_RESULTS,
        "supported_extensions": config.SUPPORTED_EXTENSIONS
    }


# For running with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
