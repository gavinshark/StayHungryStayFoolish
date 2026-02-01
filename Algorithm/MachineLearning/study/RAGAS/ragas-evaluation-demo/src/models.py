"""
Data Models Module

Contains data models used across the RAGAS evaluation demo.
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class RAGResponse:
    """
    RAG 响应数据模型
    
    包含 RAG 系统查询的完整响应信息，包括问题、答案、
    检索到的上下文文本和原始 LangChain Document 对象。
    
    Attributes:
        question: 用户提出的问题
        answer: RAG 系统生成的回答
        contexts: 检索到的上下文文本列表
        source_documents: LangChain Document 对象列表
    """
    question: str
    answer: str
    contexts: list[str]  # 检索到的上下文文本列表
    source_documents: list  # LangChain Document 对象


@dataclass
class EvaluationSample:
    """
    评测样本数据模型
    
    包含用于 RAGAS 评测的单个样本数据。
    
    Attributes:
        question: 评测问题
        ground_truth: 参考答案（标准答案）
        contexts: 可选的参考上下文列表
    """
    question: str
    ground_truth: str  # 参考答案
    contexts: Optional[list[str]] = None  # 可选的参考上下文


@dataclass
class EvaluationResult:
    """
    评测结果数据模型
    
    包含 RAGAS 评测的各项指标分数。
    
    Attributes:
        faithfulness: 忠实度指标 (0.0-1.0)
        answer_relevancy: 答案相关性指标 (0.0-1.0)
        context_precision: 上下文精确度指标 (0.0-1.0)
        context_recall: 上下文召回率指标 (0.0-1.0)
        details: 每个样本的详细分数
    """
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float
    details: dict  # 每个样本的详细分数
