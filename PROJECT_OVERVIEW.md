# RAG Chatbot - Technical Overview

## System Architecture

### High-Level Flow
```
User Upload Documents → Document Processing → Chunking → Embedding → Vector Storage → Query → Retrieval → LLM Answer
```

---

## Application Flow

### 1. UI Layer (Streamlit)
**File:** `app.py`

**Main Components:**
- `st.set_page_config()` - Application configuration
- Document uploader interface
- Chat interface
- Session state management

**Flow:**
1. User uploads documents (PDF, TXT, DOCX, MD)
2. Documents validated and sent to document loader
3. Progress displayed during processing
4. Chat interface activated after processing
5. Questions sent to RAG engine
6. Answers displayed with source citations

---

### 2. Backend API Layer (Optional FastAPI)
**File:** `api.py`

**Class:** `FastAPI` app

**Key Endpoints:**
- `POST /upload` - Upload and process documents
- `POST /query` - Ask questions
- `GET /health` - Health check
- `GET /stats` - Database statistics
- `DELETE /clear` - Clear database
- `GET /config` - Get configuration

**Flow:**
1. Receives HTTP requests from frontend
2. Validates input using Pydantic models
3. Routes to appropriate RAG engine methods
4. Returns JSON responses with CORS support

---

### 3. Document Processing Layer
**File:** `document_loader.py`

**Class:** `DocumentLoader`

**Key Methods:**
- `load_document()` - Load single document
- `process_documents()` - Batch process documents
- `split_documents()` - Split into chunks

**Supported Formats:**
- PDF (PyPDFLoader)
- TXT (TextLoader)
- DOCX (Docx2txtLoader)
- Markdown (UnstructuredMarkdownLoader)

**Flow:**
1. Receives file path(s)
2. Detects file type by extension
3. Loads document using appropriate loader
4. Splits into chunks (500 chars, 50 overlap)
5. Returns list of document chunks

---

### 4. RAG Engine Layer
**File:** `rag_engine.py`

**Class:** `RAGEngine`

**Key Methods:**
- `create_vectorstore()` - Build vector database
- `load_existing_vectorstore()` - Load saved database
- `query()` - Query documents
- `get_stats()` - Get database statistics
- `clear_database()` - Clear all data

**Flow:**
1. Initialize embeddings (OllamaEmbeddings)
2. Initialize LLM (OllamaLLM)
3. Create ChromaDB vector store
4. Set up RetrievalQA chain
5. Process queries and return answers

---

### 5. Configuration Layer
**File:** `config.py`

**Class:** `Config`

**Key Settings:**
- Ollama base URL
- Model names (LLM + Embeddings)
- ChromaDB settings
- Chunk size/overlap
- Top-K results

---

## AI Models Used

### 1. Llama 3.2 (3B parameters)
- **Purpose:** Question answering and text generation
- **Model:** `llama3.2:latest`
- **Platform:** Ollama (local inference)
- **Tasks:**
  - Answer questions based on context
  - Generate coherent responses
  - Maintain conversation context

**Configuration:**
```python
model = "llama3.2:latest"
temperature = 0.0  # Deterministic answers
```

### 2. Nomic Embed Text
- **Purpose:** Text embeddings for semantic search
- **Model:** `nomic-embed-text`
- **Platform:** Ollama
- **Tasks:**
  - Convert text to vector embeddings
  - Enable semantic similarity search
  - Match queries to relevant documents

**Configuration:**
```python
model = "nomic-embed-text"
base_url = "http://localhost:11434"
```

---

## Key Packages & Dependencies

### Core Frameworks
- **streamlit** - Web UI framework
- **fastapi** - REST API framework
- **uvicorn** - ASGI server for FastAPI
- **python-multipart** - File upload support

### LangChain Stack
- **langchain** - LLM orchestration framework
- **langchain-community** - Community integrations
- **langchain-ollama** - Ollama integration

### Vector Database
- **chromadb** - Vector database for embeddings

### Document Processing
- **pypdf** - PDF document parsing
- **python-docx** - Word document parsing
- **openpyxl** - Excel document support (optional)
- **markdown** - Markdown processing
- **docx2txt** - DOCX text extraction

### Utilities
- **python-dotenv** - Environment variable management
- **pydantic** - Data validation (FastAPI)

---

## Complete Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                      (Streamlit Web UI)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📤 File Upload  │  💬 Chat Interface  │  📊 Database Stats    │
│                                                                 │
│  • Upload Documents (PDF/TXT/DOCX/MD)                          │
│  • Ask Questions in Chat                                       │
│  • View Answers with Sources                                   │
│  • Clear Database                                              │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Upload Files
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSING                          │
│                   (DocumentLoader)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Format Detection → Loader Selection → Text Extraction         │
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │   PDF   │  │   TXT   │  │  DOCX   │  │   MD    │         │
│  │PyPDFLoad│  │TextLoad │  │Docx2txt │  │ Unstruct│         │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘         │
│       │            │             │            │               │
│       └────────────┴─────────────┴────────────┘               │
│                          │                                     │
│                          ▼                                     │
│              RecursiveCharacterTextSplitter                    │
│              (Chunk Size: 500, Overlap: 50)                   │
│                          │                                     │
│                          ▼                                     │
│              List of Document Chunks                           │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Document Chunks
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EMBEDDING LAYER                            │
│                   (Ollama Embeddings)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Text Chunk → Nomic Embed Model → Vector (Embedding)           │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │ Nomic-Embed-Text │  Model: nomic-embed-text                │
│  │  via Ollama      │  Dimensions: 768                         │
│  │                  │  Type: Sentence embeddings               │
│  └────────┬─────────┘                                          │
│           │                                                     │
│           ▼                                                     │
│  Vector Embeddings (768-dimensional)                           │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Vectors + Metadata
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   VECTOR STORAGE LAYER                          │
│                      (ChromaDB)                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Persistent Vector Database                                     │
│                                                                 │
│  ┌────────────────────────────────────────────┐                │
│  │  Collection: document_qa                   │                │
│  │  Storage: ./chroma_db/                     │                │
│  │                                             │                │
│  │  Documents: [Chunk 1, Chunk 2, ...]       │                │
│  │  Embeddings: [Vec 1, Vec 2, ...]          │                │
│  │  Metadata: [{source, page}, ...]          │                │
│  └────────────────────────────────────────────┘                │
│                                                                 │
│  Capabilities:                                                  │
│  • Similarity Search (Cosine Similarity)                       │
│  • Top-K Retrieval (Default: 3)                               │
│  • Persistent Storage                                          │
│  • Metadata Filtering                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ User Question
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      QUERY PROCESSING                           │
│                      (RAG Engine)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Question Embedding                                     │
│  ┌──────────────────────────────────────┐                      │
│  │ "What is the main topic?" →          │                      │
│  │ Nomic Embed → Query Vector           │                      │
│  └──────────────────┬───────────────────┘                      │
│                     │                                           │
│                     ▼                                           │
│  Step 2: Similarity Search                                      │
│  ┌──────────────────────────────────────┐                      │
│  │ Compare Query Vector with All Chunks │                      │
│  │ Retrieve Top 3 Most Similar          │                      │
│  └──────────────────┬───────────────────┘                      │
│                     │                                           │
│                     ▼                                           │
│  Step 3: Context Building                                       │
│  ┌──────────────────────────────────────┐                      │
│  │ Relevant Chunk 1                     │                      │
│  │ Relevant Chunk 2                     │                      │
│  │ Relevant Chunk 3                     │                      │
│  └──────────────────┬───────────────────┘                      │
│                     │                                           │
│                     ▼                                           │
│  Step 4: Prompt Construction                                    │
│  ┌──────────────────────────────────────┐                      │
│  │ Context: [Retrieved Chunks]          │                      │
│  │ Question: [User Question]            │                      │
│  │ Instructions: Answer based on context│                      │
│  └──────────────────┬───────────────────┘                      │
│                     │                                           │
│                     ▼                                           │
│                 Send to LLM                                     │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Prompt
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM INFERENCE                              │
│                  (Llama 3.2 via Ollama)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────┐                      │
│  │   Llama 3.2 (3B Parameters)          │                      │
│  │                                       │                      │
│  │   Model: llama3.2:latest             │                      │
│  │   Temperature: 0.0 (Deterministic)   │                      │
│  │   Platform: Ollama                   │                      │
│  │   URL: http://localhost:11434        │                      │
│  │                                       │                      │
│  │   Input: Context + Question          │                      │
│  │   Output: Generated Answer           │                      │
│  └──────────────────┬───────────────────┘                      │
│                     │                                           │
│                     ▼                                           │
│  Generated Answer:                                              │
│  "The main topic is..."                                        │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Answer + Sources
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RESPONSE FORMATTING                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────┐                      │
│  │ Answer: [Generated Text]             │                      │
│  │                                       │                      │
│  │ Sources:                              │                      │
│  │   1. [Document Chunk 1 + Metadata]   │                      │
│  │   2. [Document Chunk 2 + Metadata]   │                      │
│  │   3. [Document Chunk 3 + Metadata]   │                      │
│  └──────────────────┬───────────────────┘                      │
│                     │                                           │
│                     ▼                                           │
│              Display to User                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Summary

### Document Upload Flow
```
User Upload → File Validation → Document Loading → Text Extraction →
Chunking → Embedding → Vector Storage → Success Message
```

### Query Flow
```
User Question → Question Embedding → Similarity Search →
Retrieve Top-K → Build Context → LLM Inference → Format Response → Display Answer
```

---

## Architecture Patterns

### 1. Retrieval-Augmented Generation (RAG)
- Combines information retrieval with text generation
- Reduces hallucinations by grounding answers in documents
- Provides source citations for transparency

### 2. Vector Search
- Semantic similarity using embeddings
- Fast nearest neighbor search
- Scalable to large document collections

### 3. Modular Design
- Separate concerns (UI, processing, storage, inference)
- Easy to swap components (different LLMs, databases)
- Testable and maintainable

---

## Configuration

**File:** `config.py`

```python
class Config:
    # Ollama Settings
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "llama3.2:latest"

    # Embedding Model
    EMBEDDING_MODEL = "nomic-embed-text"

    # ChromaDB Settings
    CHROMA_PERSIST_DIR = "./chroma_db"
    COLLECTION_NAME = "document_qa"

    # Document Processing
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50

    # RAG Settings
    TOP_K_RESULTS = 3

    # Supported File Types
    SUPPORTED_EXTENSIONS = ['.pdf', '.txt', '.docx', '.md']
```

---

## Performance Characteristics

### Processing Times
- **Document Upload (10-page PDF):** 5-10 seconds
  - Parsing: 1-2s
  - Chunking: <1s
  - Embedding: 3-5s
  - Storage: <1s

- **Query Response:** 2-5 seconds
  - Embedding query: <1s
  - Similarity search: <1s
  - LLM inference: 2-3s
  - Response formatting: <1s

### Resource Usage
- **RAM:** ~2GB
  - Llama 3.2: ~1.5GB
  - ChromaDB: ~200MB
  - Application: ~300MB

- **Disk:** ~5GB
  - Models: ~4GB
  - ChromaDB: Variable (depends on documents)
  - Dependencies: ~1GB

---

## Key Features

1. **Multi-Format Support** - PDF, TXT, DOCX, Markdown
2. **Persistent Storage** - Documents remain after restart
3. **Source Citations** - Transparency in answers
4. **Semantic Search** - Understanding, not just keywords
5. **Local Processing** - No external API calls
6. **Privacy First** - All data stays on your machine
7. **Scalable** - Handle large document collections
8. **REST API** - Easy integration with any frontend

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Web UI |
| **API** | FastAPI | REST endpoints (optional) |
| **Orchestration** | LangChain | RAG pipeline |
| **LLM** | Llama 3.2 (Ollama) | Question answering |
| **Embeddings** | Nomic Embed Text (Ollama) | Text vectorization |
| **Vector DB** | ChromaDB | Similarity search |
| **Doc Processing** | PyPDF, python-docx | Document parsing |
| **Server** | Uvicorn | ASGI server |

---

## System Requirements

**Minimum:**
- Python 3.10+
- 4GB RAM
- 10GB disk space
- Ollama installed

**Recommended:**
- Python 3.13
- 8GB RAM
- 20GB disk space
- SSD storage

---

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### API + Frontend Separation
```bash
# Terminal 1: Backend
python api.py

# Terminal 2: Frontend
streamlit run app.py
```

### Production (Docker)
```bash
docker-compose up -d
```

---

## Future Enhancements

- [ ] Multi-user support with authentication
- [ ] Document version control
- [ ] Advanced filters (date, source, etc.)
- [ ] Multiple language support
- [ ] Streaming responses
- [ ] Conversation history persistence
- [ ] File upload size limits
- [ ] Rate limiting
- [ ] Analytics dashboard
- [ ] Export conversations

---

*RAG Chatbot Technical Overview v1.0*
