"""
RAGAS Evaluation Demo - Source Package

This package contains the core components for the RAGAS evaluation demo:
- document_processor: Document loading and text chunking
- vector_store: Vector storage and retrieval using FAISS
- rag_chain: RAG chain implementation using LangChain
- evaluator: RAGAS evaluation framework integration
- models: Data models for RAG responses and evaluation
"""

__version__ = "0.1.0"

from .models import RAGResponse, EvaluationSample, EvaluationResult
from .document_processor import DocumentProcessor
from .vector_store import VectorStoreManager
from .rag_chain import RAGChain

__all__ = [
    "RAGResponse",
    "EvaluationSample",
    "EvaluationResult",
    "DocumentProcessor",
    "VectorStoreManager",
    "RAGChain",
]
