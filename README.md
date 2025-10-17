# RAG Chatbot with Ollama

A Retrieval-Augmented Generation (RAG) chatbot that allows you to ask questions about your documents using local AI.

## 🚀 Features

- **Document Q&A**: Ask questions about uploaded documents
- **Multiple Formats**: Supports PDF, TXT, DOCX, Markdown
- **Local AI**: Uses Ollama for privacy (no cloud APIs)
- **Vector Search**: ChromaDB for semantic search
- **Fast Embeddings**: Lightweight local embeddings
- **Chat Interface**: Clean Streamlit UI with chat history
- **Source Citations**: Shows which document chunks were used

## 🛠️ Tech Stack

- **LLM**: Ollama (llama3.2:latest)
- **Vector DB**: ChromaDB
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Framework**: LangChain
- **UI**: Streamlit

## 📋 Prerequisites

1. **Python 3.13+**
2. **Ollama** installed and running
   ```bash
   # Install from: https://ollama.ai
   ollama pull llama3.2
   ```

## 🔧 Installation

1. **Clone/Navigate to project**
   ```bash
   cd D:\PycharmProjects\rag-chatbot-ollama
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Ollama is running**
   ```bash
   ollama list
   ```

## 🎯 Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Upload documents**
   - Click "Browse files" in sidebar
   - Select PDF, TXT, DOCX, or MD files
   - Click "Process Documents"

3. **Ask questions**
   - Type your question in the chat input
   - Get AI-powered answers with sources
   - View source documents used for each answer

## 📁 Project Structure

```
rag-chatbot-ollama/
├── app.py                 # Streamlit UI
├── rag_engine.py          # Core RAG logic
├── document_loader.py     # Document processing
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── README.md              # Documentation
└── chroma_db/            # Vector database (auto-created)
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
OLLAMA_MODEL = "llama3.2:latest"  # Change model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Change embeddings
CHUNK_SIZE = 500  # Document chunk size
TOP_K_RESULTS = 3  # Number of sources to retrieve
```

## 🔥 Performance Tips

1. **Use faster models**: tinyllama for speed
2. **Adjust chunk size**: Smaller = faster, less context
3. **Reduce top-k**: Fewer sources = faster responses
4. **Use local embeddings**: No internet required

## 🐛 Troubleshooting

**Ollama not connecting?**
- Check Ollama is running: `ollama list`
- Verify URL in config.py: `http://localhost:11434`

**Slow responses?**
- Use smaller model (tinyllama)
- Reduce chunk size and top-k
- Close other applications

**Import errors?**
- Reinstall dependencies: `pip install -r requirements.txt`

## 📊 Example Use Cases

- **Research**: Query academic papers
- **Documentation**: Ask about technical docs
- **Legal**: Search contracts and agreements
- **Knowledge Base**: Company wiki Q&A
- **Books**: Ask questions about ebooks

## 🎓 Phase 3 Project Requirements

✅ Custom Chatbot Q&A (RAG Application)
✅ LangChain integration
✅ ChromaDB vector database
✅ Ollama (local LLM)
✅ Streamlit UI
✅ Document upload and processing
✅ Source citations

## 🚀 Next Steps

- Add more document formats (Excel, CSV)
- Implement conversation memory
- Add document management (delete specific docs)
- Export chat history
- Multi-language support
- Custom prompts for different use cases

## 📝 License

MIT License - Feel free to use for your Phase 3 project!
