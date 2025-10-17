"""RAG Engine - Core Q&A system using LangChain, ChromaDB, and Ollama"""

from typing import List
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from config import config

class RAGEngine:
    """Retrieval-Augmented Generation Engine"""

    def __init__(self):
        """Initialize RAG components"""
        # Use Ollama for embeddings (no torch compatibility issues)
        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=config.OLLAMA_BASE_URL
        )

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR
        )

        # Initialize Ollama LLM
        self.llm = OllamaLLM(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.0  # Deterministic for Q&A
        )

        self.vectorstore = None
        self.qa_chain = None

    def create_vectorstore(self, documents):
        """Create or update vector store from documents"""
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=config.COLLECTION_NAME,
            persist_directory=config.CHROMA_PERSIST_DIR
        )
        self._setup_qa_chain()
        return len(documents)

    def load_existing_vectorstore(self):
        """Load existing vector store"""
        try:
            self.vectorstore = Chroma(
                collection_name=config.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=config.CHROMA_PERSIST_DIR
            )
            self._setup_qa_chain()
            return True
        except:
            return False

    def _setup_qa_chain(self):
        """Setup the QA chain with custom prompt"""
        prompt_template = """Use the following context to answer the question. If you cannot answer based on the context, say "I don't have enough information to answer this question."

Context: {context}

Question: {question}

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": config.TOP_K_RESULTS}
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )

    def query(self, question: str):
        """Query the RAG system"""
        if not self.qa_chain:
            return {
                'answer': 'No documents loaded. Please upload documents first.',
                'sources': []
            }

        try:
            result = self.qa_chain.invoke({"query": question})

            return {
                'answer': result['result'],
                'sources': result['source_documents']
            }
        except Exception as e:
            return {
                'answer': f'Error: {str(e)}',
                'sources': []
            }

    def get_stats(self):
        """Get collection statistics"""
        if not self.vectorstore:
            return {'total_chunks': 0}

        try:
            collection = self.vectorstore._collection
            return {
                'total_chunks': collection.count()
            }
        except:
            return {'total_chunks': 0}

    def clear_database(self):
        """Clear the vector database"""
        try:
            if self.vectorstore:
                self.vectorstore._client.delete_collection(config.COLLECTION_NAME)
                self.vectorstore = None
                self.qa_chain = None
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
