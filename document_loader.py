"""Document Loader - Handles multiple document formats"""

from typing import List
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader
)
from config import config

class DocumentLoader:
    """Load and process documents for RAG"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
        )

    def load_document(self, file_path: str):
        """Load a single document based on file type"""
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.pdf':
                loader = PyPDFLoader(file_path)
            elif ext == '.txt':
                loader = TextLoader(file_path)
            elif ext == '.docx':
                loader = Docx2txtLoader(file_path)
            elif ext == '.md':
                loader = UnstructuredMarkdownLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")

            documents = loader.load()
            return documents

        except Exception as e:
            raise Exception(f"Error loading {file_path}: {str(e)}")

    def split_documents(self, documents):
        """Split documents into chunks"""
        return self.text_splitter.split_documents(documents)

    def process_documents(self, file_paths: List[str]):
        """Process multiple documents"""
        all_docs = []

        for file_path in file_paths:
            docs = self.load_document(file_path)
            all_docs.extend(docs)

        # Split into chunks
        chunks = self.split_documents(all_docs)
        return chunks
