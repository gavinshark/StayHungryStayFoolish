"""
Tests for RAGChain Module

Tests the RAG chain implementation using mocked LLM and vector store.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.documents import Document
from hypothesis import given, settings, strategies as st

from src.rag_chain import RAGChain
from src.models import RAGResponse
from src.vector_store import VectorStoreManager


class TestRAGChainInit:
    """Tests for RAGChain initialization"""
    
    def test_init_with_empty_api_key_raises_error(self):
        """Test that empty API key raises ValueError"""
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = True
        
        with pytest.raises(ValueError, match="API key cannot be empty"):
            RAGChain(mock_vsm, api_key="")
    
    def test_init_with_whitespace_api_key_raises_error(self):
        """Test that whitespace-only API key raises ValueError"""
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = True
        
        with pytest.raises(ValueError, match="API key cannot be empty"):
            RAGChain(mock_vsm, api_key="   ")
    
    def test_init_with_invalid_k_raises_error(self):
        """Test that k <= 0 raises ValueError"""
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = True
        
        with pytest.raises(ValueError, match="k must be greater than 0"):
            RAGChain(mock_vsm, api_key="test-key", k=0)
        
        with pytest.raises(ValueError, match="k must be greater than 0"):
            RAGChain(mock_vsm, api_key="test-key", k=-1)
    
    def test_init_with_uninitialized_vector_store_raises_error(self):
        """Test that uninitialized vector store raises ValueError"""
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = False
        
        with pytest.raises(ValueError, match="Vector store not initialized"):
            RAGChain(mock_vsm, api_key="test-key")
    
    @patch('src.rag_chain.ChatOpenAI')
    @patch('src.rag_chain.RetrievalQA')
    def test_init_creates_chain_with_correct_config(self, mock_retrieval_qa, mock_chat_openai):
        """Test that initialization creates chain with correct configuration"""
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = True
        mock_retriever = Mock()
        mock_vsm.as_retriever.return_value = mock_retriever
        
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        mock_chain = Mock()
        mock_retrieval_qa.from_chain_type.return_value = mock_chain
        
        rag_chain = RAGChain(
            mock_vsm,
            api_key="test-api-key",
            model="gpt-4",
            k=5
        )
        
        # Verify ChatOpenAI was called with correct parameters
        mock_chat_openai.assert_called_once_with(api_key="test-api-key", model="gpt-4")
        
        # Verify as_retriever was called with correct k
        mock_vsm.as_retriever.assert_called_once_with(k=5)
        
        # Verify RetrievalQA.from_chain_type was called with correct parameters
        mock_retrieval_qa.from_chain_type.assert_called_once_with(
            llm=mock_llm,
            chain_type="stuff",
            retriever=mock_retriever,
            return_source_documents=True
        )
        
        assert rag_chain.k == 5
        assert rag_chain.llm == mock_llm
        assert rag_chain.retriever == mock_retriever
        assert rag_chain.chain == mock_chain


class TestRAGChainQuery:
    """Tests for RAGChain.query method"""
    
    @patch('src.rag_chain.ChatOpenAI')
    @patch('src.rag_chain.RetrievalQA')
    def test_query_with_empty_question_raises_error(self, mock_retrieval_qa, mock_chat_openai):
        """Test that empty question raises ValueError"""
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = True
        mock_vsm.as_retriever.return_value = Mock()
        
        rag_chain = RAGChain(mock_vsm, api_key="test-key")
        
        with pytest.raises(ValueError, match="Question cannot be empty"):
            rag_chain.query("")
        
        with pytest.raises(ValueError, match="Question cannot be empty"):
            rag_chain.query("   ")
    
    @patch('src.rag_chain.ChatOpenAI')
    @patch('src.rag_chain.RetrievalQA')
    def test_query_returns_rag_response(self, mock_retrieval_qa, mock_chat_openai):
        """Test that query returns a properly structured RAGResponse"""
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = True
        mock_vsm.as_retriever.return_value = Mock()
        
        # Create mock source documents
        mock_doc1 = Document(page_content="Context 1 about RAG")
        mock_doc2 = Document(page_content="Context 2 about evaluation")
        
        # Setup mock chain response
        mock_chain = Mock()
        mock_chain.invoke.return_value = {
            "query": "What is RAG?",
            "result": "RAG is Retrieval-Augmented Generation.",
            "source_documents": [mock_doc1, mock_doc2]
        }
        mock_retrieval_qa.from_chain_type.return_value = mock_chain
        
        rag_chain = RAGChain(mock_vsm, api_key="test-key")
        response = rag_chain.query("What is RAG?")
        
        # Verify response structure
        assert isinstance(response, RAGResponse)
        assert response.question == "What is RAG?"
        assert response.answer == "RAG is Retrieval-Augmented Generation."
        assert response.contexts == ["Context 1 about RAG", "Context 2 about evaluation"]
        assert response.source_documents == [mock_doc1, mock_doc2]
    
    @patch('src.rag_chain.ChatOpenAI')
    @patch('src.rag_chain.RetrievalQA')
    def test_query_handles_empty_source_documents(self, mock_retrieval_qa, mock_chat_openai):
        """Test that query handles case with no source documents"""
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = True
        mock_vsm.as_retriever.return_value = Mock()
        
        # Setup mock chain response with no source documents
        mock_chain = Mock()
        mock_chain.invoke.return_value = {
            "query": "What is RAG?",
            "result": "I don't have enough context to answer.",
            "source_documents": []
        }
        mock_retrieval_qa.from_chain_type.return_value = mock_chain
        
        rag_chain = RAGChain(mock_vsm, api_key="test-key")
        response = rag_chain.query("What is RAG?")
        
        assert response.contexts == []
        assert response.source_documents == []
    
    @patch('src.rag_chain.ChatOpenAI')
    @patch('src.rag_chain.RetrievalQA')
    def test_query_invokes_chain_with_correct_input(self, mock_retrieval_qa, mock_chat_openai):
        """Test that query invokes chain with correct input format"""
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = True
        mock_vsm.as_retriever.return_value = Mock()
        
        mock_chain = Mock()
        mock_chain.invoke.return_value = {
            "result": "Answer",
            "source_documents": []
        }
        mock_retrieval_qa.from_chain_type.return_value = mock_chain
        
        rag_chain = RAGChain(mock_vsm, api_key="test-key")
        rag_chain.query("Test question")
        
        # Verify chain was invoked with correct input
        mock_chain.invoke.assert_called_once_with({"query": "Test question"})


class TestRAGResponse:
    """Tests for RAGResponse dataclass"""
    
    def test_rag_response_creation(self):
        """Test RAGResponse can be created with all fields"""
        doc = Document(page_content="Test content")
        response = RAGResponse(
            question="What is RAG?",
            answer="RAG is a technique.",
            contexts=["Context 1", "Context 2"],
            source_documents=[doc]
        )
        
        assert response.question == "What is RAG?"
        assert response.answer == "RAG is a technique."
        assert response.contexts == ["Context 1", "Context 2"]
        assert response.source_documents == [doc]


# =============================================================================
# Property-Based Tests
# =============================================================================

class TestRAGChainPropertyTests:
    """
    Property-based tests for RAGChain
    
    **Feature: ragas-evaluation-demo, Property 8: RAG Response Context Inclusion**
    **Validates: Requirements 4.1**
    """
    
    @settings(max_examples=100)
    @given(
        question=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
        answer=st.text(min_size=1, max_size=500),
        num_docs=st.integers(min_value=0, max_value=10),
        doc_contents=st.lists(
            st.text(min_size=1, max_size=300).filter(lambda x: x.strip()),
            min_size=0,
            max_size=10
        )
    )
    @patch('src.rag_chain.ChatOpenAI')
    @patch('src.rag_chain.RetrievalQA')
    def test_property_8_rag_response_context_inclusion(
        self,
        mock_retrieval_qa,
        mock_chat_openai,
        question,
        answer,
        num_docs,
        doc_contents
    ):
        """
        **Feature: ragas-evaluation-demo, Property 8: RAG Response Context Inclusion**
        
        For any RAGChain query, the returned RAGResponse should contain contexts
        that match the source_documents content.
        
        **Validates: Requirements 4.1**
        
        This property verifies that:
        1. The contexts list in RAGResponse contains exactly the page_content
           from each source_document
        2. The order of contexts matches the order of source_documents
        3. The number of contexts equals the number of source_documents
        """
        # Setup mock vector store manager
        mock_vsm = Mock(spec=VectorStoreManager)
        mock_vsm.is_initialized = True
        mock_vsm.as_retriever.return_value = Mock()
        
        # Generate source documents from doc_contents (limited by num_docs)
        actual_num_docs = min(num_docs, len(doc_contents))
        source_documents = [
            Document(page_content=content)
            for content in doc_contents[:actual_num_docs]
        ]
        
        # Setup mock chain response
        mock_chain = Mock()
        mock_chain.invoke.return_value = {
            "query": question,
            "result": answer,
            "source_documents": source_documents
        }
        mock_retrieval_qa.from_chain_type.return_value = mock_chain
        
        # Create RAGChain and execute query
        rag_chain = RAGChain(mock_vsm, api_key="test-api-key")
        response = rag_chain.query(question)
        
        # Property 8 Verification: contexts should match source_documents content
        # 1. Number of contexts should equal number of source_documents
        assert len(response.contexts) == len(response.source_documents), \
            f"Number of contexts ({len(response.contexts)}) should equal " \
            f"number of source_documents ({len(response.source_documents)})"
        
        # 2. Each context should match the corresponding source_document's page_content
        for i, (context, doc) in enumerate(zip(response.contexts, response.source_documents)):
            assert context == doc.page_content, \
                f"Context at index {i} ('{context}') should match " \
                f"source_document page_content ('{doc.page_content}')"
        
        # 3. Verify contexts list is exactly the page_content from source_documents
        expected_contexts = [doc.page_content for doc in response.source_documents]
        assert response.contexts == expected_contexts, \
            f"Contexts {response.contexts} should exactly match " \
            f"source_documents content {expected_contexts}"
