"""
RAG Chain Module

Implements the RAG chain using LangChain RetrievalQA.
Implements Requirements 4.1, 4.2, 4.3, 4.5.
"""

from langchain_classic.chains import RetrievalQA
from langchain_openai import ChatOpenAI

from .models import RAGResponse
from .vector_store import VectorStoreManager


class RAGChain:
    """
    RAG 链，封装 LangChain RetrievalQA
    
    使用 LangChain 的 RetrievalQA 链构建检索增强生成系统。
    支持配置 LLM 模型、API 密钥和检索文档数量。
    
    Attributes:
        llm: ChatOpenAI LLM 实例
        retriever: VectorStoreRetriever 实例
        chain: RetrievalQA 链实例
        k: 检索文档数量
    """
    
    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        k: int = 4,
        base_url: str = None
    ):
        """
        初始化 RAG 链
        
        Args:
            vector_store_manager: 向量存储管理器实例
            api_key: OpenAI API 密钥
            model: 模型名称，默认 "gpt-3.5-turbo"
            k: 检索文档数量，默认 4
            base_url: API Base URL，可选
            
        Raises:
            ValueError: 如果 api_key 为空
            ValueError: 如果 k <= 0
            ValueError: 如果向量存储未初始化
            
        Validates:
            - Requirement 4.3: 支持配置大模型 API 密钥和模型名称
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        if k <= 0:
            raise ValueError("k must be greater than 0")
        
        if not vector_store_manager.is_initialized:
            raise ValueError("Vector store not initialized. Create or load a vector store first.")
        
        self.k = k
        
        # 初始化 ChatOpenAI LLM
        # Validates Requirement 4.3: 支持配置大模型 API 密钥和模型名称
        llm_kwargs = {"api_key": api_key, "model": model}
        if base_url:
            llm_kwargs["base_url"] = base_url
        self.llm = ChatOpenAI(**llm_kwargs)
        
        # 获取 Retriever 接口
        self.retriever = vector_store_manager.as_retriever(k=k)
        
        # 构建 RetrievalQA 链
        # Validates Requirement 4.1: 构建包含上下文的提示词
        # Validates Requirement 4.2: 调用外部大模型 API 生成回答
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True
        )
    
    def query(self, question: str) -> RAGResponse:
        """
        查询并生成回答
        
        使用 RAG 链处理用户问题，检索相关文档并生成回答。
        
        Args:
            question: 用户问题
            
        Returns:
            RAGResponse 包含答案和上下文
            
        Raises:
            ValueError: 如果 question 为空
            
        Validates:
            - Requirement 4.1: 构建包含上下文的提示词
            - Requirement 4.2: 调用外部大模型 API 生成回答
            - Requirement 4.5: 返回生成的文本回答
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        # 调用 RetrievalQA 链
        # 这会自动执行：检索相关文档 -> 构建提示词 -> 调用 LLM 生成回答
        result = self.chain.invoke({"query": question})
        
        # 提取源文档
        source_documents = result.get("source_documents", [])
        
        # 提取上下文文本列表
        contexts = [doc.page_content for doc in source_documents]
        
        # 提取答案
        answer = result.get("result", "")
        
        # 构建并返回 RAGResponse
        # Validates Requirement 4.5: 返回生成的文本回答
        return RAGResponse(
            question=question,
            answer=answer,
            contexts=contexts,
            source_documents=source_documents
        )
