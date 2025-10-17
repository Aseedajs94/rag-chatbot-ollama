# RAG Chatbot API Documentation

## Overview

RESTful API for Document Q&A using RAG (Retrieval-Augmented Generation) with FastAPI backend.

**Base URL:** `http://localhost:8000`

**API Docs (Swagger):** `http://localhost:8000/docs`

**Alternative Docs (ReDoc):** `http://localhost:8000/redoc`

---

## Architecture

```
Frontend (React/HTML/Mobile)
        ↓ HTTP/REST
FastAPI Backend (api.py)
        ↓
RAG Engine (rag_engine.py)
        ↓
├─ Ollama (TinyLlama/Llama3.2)
└─ ChromaDB (Vector Database)
```

---

## API Endpoints

### 1. Health Check

**GET** `/health`

Check API and dependencies health status.

**Response:**
```json
{
  "status": "healthy",
  "ollama_connected": true,
  "vectorstore_loaded": true
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 2. Upload Documents

**POST** `/upload`

Upload and process documents to build the knowledge base.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Files (PDF, TXT, DOCX, MD)

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt"
```

**Python Example:**
```python
import requests

files = [
    ('files', open('document1.pdf', 'rb')),
    ('files', open('document2.txt', 'rb'))
]

response = requests.post('http://localhost:8000/upload', files=files)
print(response.json())
```

**Response:**
```json
{
  "message": "Documents processed successfully",
  "total_chunks": 45,
  "files_processed": 2
}
```

**Status Codes:**
- `200 OK` - Documents processed successfully
- `400 Bad Request` - Invalid file format or no files provided
- `500 Internal Server Error` - Processing failed

---

### 3. Query Documents

**POST** `/query`

Ask a question about the uploaded documents.

**Request:**
```json
{
  "question": "What are the main features of the product?"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main features?"}'
```

**Python Example:**
```python
import requests

payload = {"question": "What are the main features of the product?"}
response = requests.post('http://localhost:8000/query', json=payload)
print(response.json())
```

**Response:**
```json
{
  "answer": "The main features include...",
  "sources": [
    {
      "content": "Feature description from document...",
      "metadata": {
        "source": "document1.pdf",
        "page": 1
      }
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Query successful
- `400 Bad Request` - Empty question
- `500 Internal Server Error` - Query processing failed

---

### 4. Get Statistics

**GET** `/stats`

Get database and system statistics.

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/stats"
```

**Response:**
```json
{
  "total_chunks": 45,
  "collection_name": "document_qa",
  "ollama_model": "llama3.2:latest",
  "embedding_model": "nomic-embed-text"
}
```

**Status Codes:**
- `200 OK` - Statistics retrieved

---

### 5. Clear Database

**DELETE** `/clear`

Clear all documents from the vector database.

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8000/clear"
```

**Response:**
```json
{
  "message": "Database cleared successfully"
}
```

**Status Codes:**
- `200 OK` - Database cleared
- `500 Internal Server Error` - Clear operation failed

---

### 6. Get Configuration

**GET** `/config`

Get current system configuration.

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/config"
```

**Response:**
```json
{
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "llama3.2:latest",
  "collection_name": "document_qa",
  "chunk_size": 500,
  "chunk_overlap": 50,
  "top_k_results": 3,
  "supported_extensions": [".pdf", ".txt", ".docx", ".md"]
}
```

**Status Codes:**
- `200 OK` - Configuration retrieved

---

## Running the API

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running
ollama serve

# Pull required models
ollama pull llama3.2:latest
ollama pull nomic-embed-text
```

### Start the API Server

```bash
# Option 1: Using Python
python api.py

# Option 2: Using Uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Frontend Integration

### JavaScript/React Example

```javascript
// Upload documents
async function uploadDocuments(files) {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  const response = await fetch('http://localhost:8000/upload', {
    method: 'POST',
    body: formData
  });

  return await response.json();
}

// Query documents
async function queryDocuments(question) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });

  return await response.json();
}

// Usage
const result = await queryDocuments("What are the key points?");
console.log(result.answer);
```

### HTML Form Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>RAG Chatbot</title>
</head>
<body>
    <h1>Document Q&A</h1>

    <!-- Upload Form -->
    <form id="uploadForm">
        <input type="file" multiple id="fileInput" accept=".pdf,.txt,.docx,.md">
        <button type="submit">Upload Documents</button>
    </form>

    <!-- Query Form -->
    <form id="queryForm">
        <input type="text" id="question" placeholder="Ask a question...">
        <button type="submit">Ask</button>
    </form>

    <div id="answer"></div>

    <script>
        // Upload handler
        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData();
            const files = document.getElementById('fileInput').files;

            for (let file of files) {
                formData.append('files', file);
            }

            const response = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            alert(result.message);
        };

        // Query handler
        document.getElementById('queryForm').onsubmit = async (e) => {
            e.preventDefault();
            const question = document.getElementById('question').value;

            const response = await fetch('http://localhost:8000/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            const result = await response.json();
            document.getElementById('answer').innerHTML = `
                <h3>Answer:</h3>
                <p>${result.answer}</p>
                <h4>Sources:</h4>
                <ul>
                    ${result.sources.map(s => `<li>${s.content.substring(0, 100)}...</li>`).join('')}
                </ul>
            `;
        };
    </script>
</body>
</html>
```

---

## Error Handling

All endpoints return standard HTTP status codes and JSON error messages:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `500` - Internal Server Error

---

## CORS Configuration

The API has CORS enabled for all origins (`*`) by default. For production, update `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Considerations

- **Chunk Size:** Configured to 500 characters (adjustable in `config.py`)
- **Top-K Results:** Returns top 3 most relevant chunks
- **Model:** Uses Llama3.2 (fast, lightweight)
- **Embedding:** nomic-embed-text (efficient)

**Typical Response Times:**
- Upload (10-page PDF): 5-10 seconds
- Query: 2-5 seconds

---

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Database Issues
```bash
# Clear the database via API
curl -X DELETE http://localhost:8000/clear

# Or manually delete the ChromaDB directory
rm -rf chroma_db/
```

### Port Already in Use
```bash
# Change port in api.py or use different port
uvicorn api:app --port 8001
```

---

## Security Best Practices

1. **API Authentication:** Add JWT/OAuth for production
2. **Rate Limiting:** Implement rate limiting to prevent abuse
3. **Input Validation:** Already implemented via Pydantic models
4. **File Size Limits:** Configure max file size in FastAPI
5. **HTTPS:** Use reverse proxy (nginx) with SSL certificates

---

## Next Steps

- [ ] Add authentication (JWT tokens)
- [ ] Implement rate limiting
- [ ] Add request logging
- [ ] Create frontend UI (React/Vue)
- [ ] Add file size validation
- [ ] Implement pagination for large result sets
- [ ] Add caching for frequent queries

---

*API Documentation for RAG Chatbot v1.0*
