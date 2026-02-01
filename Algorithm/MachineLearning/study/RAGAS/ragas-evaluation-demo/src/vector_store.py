"""
Vector Store Manager Module

Handles vector storage and retrieval using LangChain FAISS.
Implements Requirements 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 3.4.
"""

import os
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever


class VectorStoreManager:
    """
    向量存储管理器，封装 LangChain FAISS 操作
    
    使用 OpenAI Embeddings 进行文本向量化，使用 FAISS 进行向量存储和检索。
    支持创建、增量添加、相似度搜索、持久化保存和加载等操作。
    
    Attributes:
        embeddings: OpenAI Embeddings 实例
        vector_store: FAISS 向量存储实例
    """
    
    def __init__(self, api_key: str, embedding_model: str = "text-embedding-v4", base_url: str = None):
        """
        初始化向量存储管理器
        
        Args:
            api_key: OpenAI API 密钥
            embedding_model: 嵌入模型名称，默认 "text-embedding-v4"
            base_url: API Base URL，可选
            
        Raises:
            ValueError: 如果 api_key 为空
            
        Validates:
            - Requirement 2.1: 使用嵌入模型将文本转换为向量
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        kwargs = {"api_key": api_key, "model": embedding_model}
        if base_url:
            kwargs["base_url"] = base_url
            # 对于非 OpenAI 的 API（如阿里云 DashScope），禁用 tokenization
            # 因为它们可能不支持 token 输入方式
            kwargs["check_embedding_ctx_length"] = False
        self.embeddings = OpenAIEmbeddings(**kwargs)
        self.vector_store: Optional[FAISS] = None
    
    def create_from_documents(self, documents: list[Document]) -> FAISS:
        """
        从文档创建向量存储
        
        使用 OpenAI Embeddings 将文档向量化，并创建 FAISS 向量存储。
        
        Args:
            documents: LangChain Document 列表
            
        Returns:
            FAISS 向量存储实例
            
        Raises:
            ValueError: 如果 documents 为空
            
        Validates:
            - Requirement 2.1: 使用嵌入模型将文本转换为向量
            - Requirement 2.2: 将向量数据存储在本地内存或文件中
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        # 使用 FAISS.from_documents 创建向量存储
        # 这会自动使用 embeddings 将文档向量化
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        return self.vector_store
    
    def add_documents(self, documents: list[Document]) -> None:
        """
        增量添加文档到向量存储
        
        将新文档向量化并添加到现有的向量存储中。
        
        Args:
            documents: LangChain Document 列表
            
        Raises:
            ValueError: 如果向量存储未初始化
            ValueError: 如果 documents 为空
            
        Validates:
            - Requirement 2.3: 支持增量添加新向量
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_from_documents first.")
        
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        # 使用 add_documents 方法增量添加文档
        self.vector_store.add_documents(documents)
    
    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """
        相似度搜索
        
        将查询文本向量化，并在向量存储中搜索最相似的文档。
        
        Args:
            query: 查询文本
            k: 返回结果数量，默认 4
            
        Returns:
            相关文档列表，按相似度降序排列
            
        Raises:
            ValueError: 如果向量存储未初始化
            ValueError: 如果 query 为空
            ValueError: 如果 k <= 0
            
        Validates:
            - Requirement 3.1: 将查询向量化并计算与存储向量的相似度
            - Requirement 3.2: 返回相似度最高的 K 个文档块
            - Requirement 3.3: 支持配置返回结果数量 K
            - Requirement 3.4: 包含文档块内容和相似度分数
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_from_documents first.")
        
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if k <= 0:
            raise ValueError("k must be greater than 0")
        
        # 使用 similarity_search 方法进行相似度搜索
        # 返回最相似的 k 个文档
        results = self.vector_store.similarity_search(query, k=k)
        
        return results
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> list[tuple[Document, float]]:
        """
        带分数的相似度搜索
        
        将查询文本向量化，并在向量存储中搜索最相似的文档，同时返回相似度分数。
        
        Args:
            query: 查询文本
            k: 返回结果数量，默认 4
            
        Returns:
            元组列表，每个元组包含 (Document, score)，按相似度降序排列
            注意：FAISS 返回的是距离分数，分数越低表示越相似
            
        Raises:
            ValueError: 如果向量存储未初始化
            ValueError: 如果 query 为空
            ValueError: 如果 k <= 0
            
        Validates:
            - Requirement 3.4: 包含文档块内容和相似度分数
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_from_documents first.")
        
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if k <= 0:
            raise ValueError("k must be greater than 0")
        
        # 使用 similarity_search_with_score 方法进行带分数的相似度搜索
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        return results
    
    def save(self, path: str) -> None:
        """
        保存向量存储到本地
        
        将 FAISS 向量索引和相关数据保存到指定路径。
        
        Args:
            path: 保存路径（目录路径）
            
        Raises:
            ValueError: 如果向量存储未初始化
            ValueError: 如果 path 为空
            
        Validates:
            - Requirement 2.5: 支持保存和加载向量索引
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_from_documents first.")
        
        if not path or not path.strip():
            raise ValueError("Path cannot be empty")
        
        # 确保目录存在
        os.makedirs(path, exist_ok=True)
        
        # 使用 save_local 方法保存向量存储
        self.vector_store.save_local(path)
    
    def load(self, path: str) -> None:
        """
        从本地加载向量存储
        
        从指定路径加载 FAISS 向量索引和相关数据。
        
        Args:
            path: 加载路径（目录路径）
            
        Raises:
            ValueError: 如果 path 为空
            FileNotFoundError: 如果路径不存在
            
        Validates:
            - Requirement 2.5: 支持保存和加载向量索引
        """
        if not path or not path.strip():
            raise ValueError("Path cannot be empty")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Vector store path not found: {path}")
        
        # 使用 load_local 方法加载向量存储
        # 需要传入 embeddings 以便后续查询时使用
        # allow_dangerous_deserialization=True 是因为 FAISS 使用 pickle 序列化
        self.vector_store = FAISS.load_local(
            path,
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True
        )
    
    def as_retriever(self, k: int = 4) -> VectorStoreRetriever:
        """
        获取 LangChain Retriever 接口
        
        返回一个 VectorStoreRetriever 实例，可以直接用于 LangChain 的 RetrievalQA 链。
        
        Args:
            k: 检索返回的文档数量，默认 4
            
        Returns:
            VectorStoreRetriever 实例
            
        Raises:
            ValueError: 如果向量存储未初始化
            ValueError: 如果 k <= 0
            
        Validates:
            - Requirement 3.3: 支持配置返回结果数量 K
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_from_documents first.")
        
        if k <= 0:
            raise ValueError("k must be greater than 0")
        
        # 使用 as_retriever 方法获取 Retriever 接口
        # search_kwargs 用于配置检索参数
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
    
    @property
    def is_initialized(self) -> bool:
        """
        检查向量存储是否已初始化
        
        Returns:
            如果向量存储已初始化返回 True，否则返回 False
        """
        return self.vector_store is not None
    
    def get_document_count(self) -> int:
        """
        获取向量存储中的文档数量
        
        Returns:
            文档数量
            
        Raises:
            ValueError: 如果向量存储未初始化
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_from_documents first.")
        
        # FAISS 的 index.ntotal 返回向量总数
        return self.vector_store.index.ntotal
