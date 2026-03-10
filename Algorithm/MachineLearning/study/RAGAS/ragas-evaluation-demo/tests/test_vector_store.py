"""
Unit Tests for VectorStoreManager

Tests the vector storage and retrieval functionality.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from langchain_core.documents import Document
from hypothesis import given, settings, strategies as st, assume

from src.vector_store import VectorStoreManager


class TestVectorStoreManagerInit:
    """Tests for VectorStoreManager initialization"""
    
    def test_init_with_valid_api_key(self):
        """Test initialization with a valid API key"""
        with patch('src.vector_store.OpenAIEmbeddings') as mock_embeddings:
            manager = VectorStoreManager(api_key="test-api-key")
            
            assert manager.embeddings is not None
            assert manager.vector_store is None
            mock_embeddings.assert_called_once_with(api_key="test-api-key", model="text-embedding-v4")
    
    def test_init_with_empty_api_key_raises_error(self):
        """Test that empty API key raises ValueError"""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            VectorStoreManager(api_key="")
    
    def test_init_with_whitespace_api_key_raises_error(self):
        """Test that whitespace-only API key raises ValueError"""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            VectorStoreManager(api_key="   ")
    
    def test_is_initialized_false_after_init(self):
        """Test that is_initialized is False after initialization"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            manager = VectorStoreManager(api_key="test-api-key")
            assert manager.is_initialized is False


class TestVectorStoreManagerCreateFromDocuments:
    """Tests for create_from_documents method"""
    
    def test_create_from_documents_with_empty_list_raises_error(self):
        """Test that empty documents list raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            manager = VectorStoreManager(api_key="test-api-key")
            
            with pytest.raises(ValueError, match="Documents list cannot be empty"):
                manager.create_from_documents([])
    
    def test_create_from_documents_success(self):
        """Test successful creation of vector store from documents"""
        with patch('src.vector_store.OpenAIEmbeddings') as mock_embeddings_cls:
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_embeddings = Mock()
                mock_embeddings_cls.return_value = mock_embeddings
                
                mock_vector_store = Mock()
                mock_faiss.from_documents.return_value = mock_vector_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                documents = [
                    Document(page_content="Test content 1"),
                    Document(page_content="Test content 2")
                ]
                
                result = manager.create_from_documents(documents)
                
                assert result == mock_vector_store
                assert manager.vector_store == mock_vector_store
                assert manager.is_initialized is True
                mock_faiss.from_documents.assert_called_once_with(
                    documents=documents,
                    embedding=mock_embeddings
                )


class TestVectorStoreManagerAddDocuments:
    """Tests for add_documents method"""
    
    def test_add_documents_without_initialization_raises_error(self):
        """Test that adding documents without initialization raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            manager = VectorStoreManager(api_key="test-api-key")
            
            with pytest.raises(ValueError, match="Vector store not initialized"):
                manager.add_documents([Document(page_content="Test")])
    
    def test_add_documents_with_empty_list_raises_error(self):
        """Test that empty documents list raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_faiss.from_documents.return_value = Mock()
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Initial")])
                
                with pytest.raises(ValueError, match="Documents list cannot be empty"):
                    manager.add_documents([])
    
    def test_add_documents_success(self):
        """Test successful addition of documents"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_vector_store = Mock()
                mock_faiss.from_documents.return_value = mock_vector_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Initial")])
                
                new_docs = [Document(page_content="New content")]
                manager.add_documents(new_docs)
                
                mock_vector_store.add_documents.assert_called_once_with(new_docs)


class TestVectorStoreManagerSimilaritySearch:
    """Tests for similarity_search method"""
    
    def test_similarity_search_without_initialization_raises_error(self):
        """Test that searching without initialization raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            manager = VectorStoreManager(api_key="test-api-key")
            
            with pytest.raises(ValueError, match="Vector store not initialized"):
                manager.similarity_search("test query")
    
    def test_similarity_search_with_empty_query_raises_error(self):
        """Test that empty query raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_faiss.from_documents.return_value = Mock()
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                with pytest.raises(ValueError, match="Query cannot be empty"):
                    manager.similarity_search("")
    
    def test_similarity_search_with_whitespace_query_raises_error(self):
        """Test that whitespace-only query raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_faiss.from_documents.return_value = Mock()
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                with pytest.raises(ValueError, match="Query cannot be empty"):
                    manager.similarity_search("   ")
    
    def test_similarity_search_with_invalid_k_raises_error(self):
        """Test that k <= 0 raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_faiss.from_documents.return_value = Mock()
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                with pytest.raises(ValueError, match="k must be greater than 0"):
                    manager.similarity_search("query", k=0)
                
                with pytest.raises(ValueError, match="k must be greater than 0"):
                    manager.similarity_search("query", k=-1)
    
    def test_similarity_search_success(self):
        """Test successful similarity search"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_vector_store = Mock()
                expected_results = [
                    Document(page_content="Result 1"),
                    Document(page_content="Result 2")
                ]
                mock_vector_store.similarity_search.return_value = expected_results
                mock_faiss.from_documents.return_value = mock_vector_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                results = manager.similarity_search("test query", k=2)
                
                assert results == expected_results
                mock_vector_store.similarity_search.assert_called_once_with("test query", k=2)
    
    def test_similarity_search_default_k(self):
        """Test that default k is 4"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_vector_store = Mock()
                mock_vector_store.similarity_search.return_value = []
                mock_faiss.from_documents.return_value = mock_vector_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                manager.similarity_search("test query")
                
                mock_vector_store.similarity_search.assert_called_once_with("test query", k=4)


class TestVectorStoreManagerSimilaritySearchWithScore:
    """Tests for similarity_search_with_score method"""
    
    def test_similarity_search_with_score_success(self):
        """Test successful similarity search with scores"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_vector_store = Mock()
                doc1 = Document(page_content="Result 1")
                doc2 = Document(page_content="Result 2")
                expected_results = [(doc1, 0.1), (doc2, 0.2)]
                mock_vector_store.similarity_search_with_score.return_value = expected_results
                mock_faiss.from_documents.return_value = mock_vector_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                results = manager.similarity_search_with_score("test query", k=2)
                
                assert results == expected_results
                mock_vector_store.similarity_search_with_score.assert_called_once_with("test query", k=2)


class TestVectorStoreManagerSaveLoad:
    """Tests for save and load methods"""
    
    def test_save_without_initialization_raises_error(self):
        """Test that saving without initialization raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            manager = VectorStoreManager(api_key="test-api-key")
            
            with pytest.raises(ValueError, match="Vector store not initialized"):
                manager.save("/tmp/test_path")
    
    def test_save_with_empty_path_raises_error(self):
        """Test that empty path raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_faiss.from_documents.return_value = Mock()
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                with pytest.raises(ValueError, match="Path cannot be empty"):
                    manager.save("")
    
    def test_save_success(self, tmp_path):
        """Test successful save operation"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_vector_store = Mock()
                mock_faiss.from_documents.return_value = mock_vector_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                save_path = str(tmp_path / "vector_store")
                manager.save(save_path)
                
                mock_vector_store.save_local.assert_called_once_with(save_path)
                assert os.path.exists(save_path)
    
    def test_load_with_empty_path_raises_error(self):
        """Test that empty path raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            manager = VectorStoreManager(api_key="test-api-key")
            
            with pytest.raises(ValueError, match="Path cannot be empty"):
                manager.load("")
    
    def test_load_with_nonexistent_path_raises_error(self):
        """Test that non-existent path raises FileNotFoundError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            manager = VectorStoreManager(api_key="test-api-key")
            
            with pytest.raises(FileNotFoundError, match="Vector store path not found"):
                manager.load("/nonexistent/path")
    
    def test_load_success(self, tmp_path):
        """Test successful load operation"""
        with patch('src.vector_store.OpenAIEmbeddings') as mock_embeddings_cls:
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_embeddings = Mock()
                mock_embeddings_cls.return_value = mock_embeddings
                
                mock_loaded_store = Mock()
                mock_faiss.load_local.return_value = mock_loaded_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                
                # Create the directory to simulate existing vector store
                load_path = str(tmp_path / "vector_store")
                os.makedirs(load_path)
                
                manager.load(load_path)
                
                assert manager.vector_store == mock_loaded_store
                assert manager.is_initialized is True
                mock_faiss.load_local.assert_called_once_with(
                    load_path,
                    embeddings=mock_embeddings,
                    allow_dangerous_deserialization=True
                )


class TestVectorStoreManagerAsRetriever:
    """Tests for as_retriever method"""
    
    def test_as_retriever_without_initialization_raises_error(self):
        """Test that getting retriever without initialization raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            manager = VectorStoreManager(api_key="test-api-key")
            
            with pytest.raises(ValueError, match="Vector store not initialized"):
                manager.as_retriever()
    
    def test_as_retriever_with_invalid_k_raises_error(self):
        """Test that k <= 0 raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_faiss.from_documents.return_value = Mock()
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                with pytest.raises(ValueError, match="k must be greater than 0"):
                    manager.as_retriever(k=0)
    
    def test_as_retriever_success(self):
        """Test successful retriever creation"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_vector_store = Mock()
                mock_retriever = Mock()
                mock_vector_store.as_retriever.return_value = mock_retriever
                mock_faiss.from_documents.return_value = mock_vector_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                retriever = manager.as_retriever(k=5)
                
                assert retriever == mock_retriever
                mock_vector_store.as_retriever.assert_called_once_with(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                )
    
    def test_as_retriever_default_k(self):
        """Test that default k is 4"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_vector_store = Mock()
                mock_vector_store.as_retriever.return_value = Mock()
                mock_faiss.from_documents.return_value = mock_vector_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                manager.as_retriever()
                
                mock_vector_store.as_retriever.assert_called_once_with(
                    search_type="similarity",
                    search_kwargs={"k": 4}
                )


class TestVectorStoreManagerGetDocumentCount:
    """Tests for get_document_count method"""
    
    def test_get_document_count_without_initialization_raises_error(self):
        """Test that getting count without initialization raises ValueError"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            manager = VectorStoreManager(api_key="test-api-key")
            
            with pytest.raises(ValueError, match="Vector store not initialized"):
                manager.get_document_count()
    
    def test_get_document_count_success(self):
        """Test successful document count retrieval"""
        with patch('src.vector_store.OpenAIEmbeddings'):
            with patch('src.vector_store.FAISS') as mock_faiss:
                mock_vector_store = Mock()
                mock_index = Mock()
                mock_index.ntotal = 10
                mock_vector_store.index = mock_index
                mock_faiss.from_documents.return_value = mock_vector_store
                
                manager = VectorStoreManager(api_key="test-api-key")
                manager.create_from_documents([Document(page_content="Test")])
                
                count = manager.get_document_count()
                
                assert count == 10


# =============================================================================
# Property-Based Tests using Hypothesis
# =============================================================================

from langchain_core.embeddings import Embeddings


class DeterministicEmbeddings(Embeddings):
    """
    A deterministic embeddings implementation for testing.
    
    Returns consistent vectors based on the input text hash,
    ensuring reproducible similarity calculations.
    """
    
    def __init__(self, dimension: int = 128):
        """Initialize with a specific embedding dimension."""
        self.dimension = dimension
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate deterministic embeddings for a list of texts."""
        embeddings = []
        for text in texts:
            # Create a deterministic embedding based on text hash
            # Use a simple hash-based approach for reproducibility
            hash_val = hash(text) % (2**31)
            np.random.seed(hash_val)
            embedding = np.random.rand(self.dimension).tolist()
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> list[float]:
        """Generate deterministic embedding for a single query."""
        hash_val = hash(text) % (2**31)
        np.random.seed(hash_val)
        return np.random.rand(self.dimension).tolist()


class TestVectorStoreManagerProperties:
    """
    Property-based tests for VectorStoreManager.
    
    These tests verify universal properties that should hold across all valid inputs.
    Uses hypothesis for property-based testing with at least 100 iterations.
    Uses mock for OpenAI API - returns predefined embedding vectors.
    """
    
    @settings(max_examples=100)
    @given(
        doc_contents=st.lists(
            st.text(
                min_size=5,
                max_size=200,
                alphabet=st.characters(
                    whitelist_categories=('L', 'N', 'P', 'Z'),
                    blacklist_characters='\x00\r'
                )
            ),
            min_size=1,
            max_size=10
        ),
        query=st.text(
            min_size=3,
            max_size=100,
            alphabet=st.characters(
                whitelist_categories=('L', 'N', 'P', 'Z'),
                blacklist_characters='\x00\r'
            )
        )
    )
    def test_property_vector_store_round_trip(self, tmp_path_factory, doc_contents, query):
        """
        **Feature: ragas-evaluation-demo, Property 4: Vector Store Round-Trip**
        
        For any set of documents added to VectorStoreManager, saving to file and
        loading from file should preserve the ability to retrieve the same documents
        with identical similarity scores.
        
        **Validates: Requirements 2.2, 2.5**
        """
        # Skip empty or whitespace-only content
        doc_contents = [c for c in doc_contents if c.strip()]
        assume(len(doc_contents) >= 1)
        assume(query.strip())
        
        # Create deterministic embeddings
        deterministic_embeddings = DeterministicEmbeddings(dimension=128)
        
        with patch('src.vector_store.OpenAIEmbeddings', return_value=deterministic_embeddings):
            # Create documents
            documents = [Document(page_content=content) for content in doc_contents]
            
            # Create vector store manager and add documents
            manager1 = VectorStoreManager(api_key="test-api-key")
            manager1.create_from_documents(documents)
            
            # Perform similarity search before save
            k = min(4, len(documents))
            results_before = manager1.similarity_search_with_score(query, k=k)
            
            # Save to file
            tmp_path = tmp_path_factory.mktemp("vector_store")
            save_path = str(tmp_path / "test_store")
            manager1.save(save_path)
            
            # Create a new manager and load from file
            manager2 = VectorStoreManager(api_key="test-api-key")
            manager2.load(save_path)
            
            # Perform similarity search after load
            results_after = manager2.similarity_search_with_score(query, k=k)
            
            # Verify results are identical
            assert len(results_before) == len(results_after), \
                "Number of results should be the same before and after round-trip"
            
            # Compare document contents and scores
            for (doc_before, score_before), (doc_after, score_after) in zip(results_before, results_after):
                assert doc_before.page_content == doc_after.page_content, \
                    "Document content should be preserved after round-trip"
                assert abs(score_before - score_after) < 1e-6, \
                    f"Similarity scores should be identical: {score_before} vs {score_after}"
    
    @settings(max_examples=100)
    @given(
        first_batch_contents=st.lists(
            st.text(
                min_size=5,
                max_size=100,
                alphabet=st.characters(
                    whitelist_categories=('L', 'N', 'P', 'Z'),
                    blacklist_characters='\x00\r'
                )
            ),
            min_size=1,
            max_size=5
        ),
        second_batch_contents=st.lists(
            st.text(
                min_size=5,
                max_size=100,
                alphabet=st.characters(
                    whitelist_categories=('L', 'N', 'P', 'Z'),
                    blacklist_characters='\x00\r'
                )
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_property_incremental_document_addition(self, first_batch_contents, second_batch_contents):
        """
        **Feature: ragas-evaluation-demo, Property 5: Incremental Document Addition**
        
        For any sequence of add_documents operations with N and M documents respectively,
        the total number of documents in VectorStoreManager should equal N + M.
        
        **Validates: Requirements 2.3**
        """
        # Filter out empty or whitespace-only content
        first_batch_contents = [c for c in first_batch_contents if c.strip()]
        second_batch_contents = [c for c in second_batch_contents if c.strip()]
        
        assume(len(first_batch_contents) >= 1)
        assume(len(second_batch_contents) >= 1)
        
        # Create deterministic embeddings
        deterministic_embeddings = DeterministicEmbeddings(dimension=128)
        
        with patch('src.vector_store.OpenAIEmbeddings', return_value=deterministic_embeddings):
            # Create documents for both batches
            first_batch = [Document(page_content=content) for content in first_batch_contents]
            second_batch = [Document(page_content=content) for content in second_batch_contents]
            
            n = len(first_batch)
            m = len(second_batch)
            
            # Create vector store manager with first batch
            manager = VectorStoreManager(api_key="test-api-key")
            manager.create_from_documents(first_batch)
            
            # Verify initial count
            initial_count = manager.get_document_count()
            assert initial_count == n, \
                f"Initial document count should be {n}, got {initial_count}"
            
            # Add second batch
            manager.add_documents(second_batch)
            
            # Verify final count
            final_count = manager.get_document_count()
            expected_total = n + m
            
            assert final_count == expected_total, \
                f"Total document count should be {expected_total} (N={n} + M={m}), got {final_count}"
    
    @settings(max_examples=100)
    @given(
        doc_contents=st.lists(
            st.text(
                min_size=5,
                max_size=100,
                alphabet=st.characters(
                    whitelist_categories=('L', 'N', 'P', 'Z'),
                    blacklist_characters='\x00\r'
                )
            ),
            min_size=1,
            max_size=20
        ),
        k=st.integers(min_value=1, max_value=30),
        query=st.text(
            min_size=3,
            max_size=50,
            alphabet=st.characters(
                whitelist_categories=('L', 'N', 'P', 'Z'),
                blacklist_characters='\x00\r'
            )
        )
    )
    def test_property_top_k_retrieval_constraint(self, doc_contents, k, query):
        """
        **Feature: ragas-evaluation-demo, Property 6: Top-K Retrieval Constraint**
        
        For any query and parameter K, the VectorStoreManager.similarity_search
        should return exactly min(K, total_documents) results.
        
        **Validates: Requirements 3.2, 3.3**
        """
        # Filter out empty or whitespace-only content
        doc_contents = [c for c in doc_contents if c.strip()]
        assume(len(doc_contents) >= 1)
        assume(query.strip())
        
        # Create deterministic embeddings
        deterministic_embeddings = DeterministicEmbeddings(dimension=128)
        
        with patch('src.vector_store.OpenAIEmbeddings', return_value=deterministic_embeddings):
            # Create documents
            documents = [Document(page_content=content) for content in doc_contents]
            total_documents = len(documents)
            
            # Create vector store manager and add documents
            manager = VectorStoreManager(api_key="test-api-key")
            manager.create_from_documents(documents)
            
            # Perform similarity search
            results = manager.similarity_search(query, k=k)
            
            # Calculate expected result count
            expected_count = min(k, total_documents)
            
            # Verify result count
            assert len(results) == expected_count, \
                f"Expected {expected_count} results (min(K={k}, total={total_documents})), got {len(results)}"
    
    @settings(max_examples=100)
    @given(
        doc_contents=st.lists(
            st.text(
                min_size=5,
                max_size=200,
                alphabet=st.characters(
                    whitelist_categories=('L', 'N', 'P', 'Z'),
                    blacklist_characters='\x00\r'
                )
            ),
            min_size=1,
            max_size=10
        ),
        k=st.integers(min_value=1, max_value=10),
        query=st.text(
            min_size=3,
            max_size=100,
            alphabet=st.characters(
                whitelist_categories=('L', 'N', 'P', 'Z'),
                blacklist_characters='\x00\r'
            )
        )
    )
    def test_property_search_result_content_validity(self, doc_contents, k, query):
        """
        **Feature: ragas-evaluation-demo, Property 7: Search Result Content Validity**
        
        For any search result returned by VectorStoreManager, it should be a valid
        LangChain Document with non-empty page_content.
        
        **Validates: Requirements 3.4**
        """
        # Filter out empty or whitespace-only content
        doc_contents = [c for c in doc_contents if c.strip()]
        assume(len(doc_contents) >= 1)
        assume(query.strip())
        
        # Create deterministic embeddings
        deterministic_embeddings = DeterministicEmbeddings(dimension=128)
        
        with patch('src.vector_store.OpenAIEmbeddings', return_value=deterministic_embeddings):
            # Create documents
            documents = [Document(page_content=content) for content in doc_contents]
            
            # Create vector store manager and add documents
            manager = VectorStoreManager(api_key="test-api-key")
            manager.create_from_documents(documents)
            
            # Perform similarity search
            results = manager.similarity_search(query, k=k)
            
            # Verify each result is a valid LangChain Document with non-empty page_content
            for i, result in enumerate(results):
                # Check that result is a Document instance
                assert isinstance(result, Document), \
                    f"Result {i} should be a LangChain Document, got {type(result)}"
                
                # Check that page_content exists and is non-empty
                assert hasattr(result, 'page_content'), \
                    f"Result {i} should have page_content attribute"
                
                assert result.page_content is not None, \
                    f"Result {i} page_content should not be None"
                
                assert isinstance(result.page_content, str), \
                    f"Result {i} page_content should be a string, got {type(result.page_content)}"
                
                assert len(result.page_content) > 0, \
                    f"Result {i} page_content should be non-empty"
                
                assert result.page_content.strip(), \
                    f"Result {i} page_content should not be whitespace-only"
                
                # Verify the result content is from the original documents
                assert result.page_content in doc_contents, \
                    f"Result {i} page_content should be from the original documents"
