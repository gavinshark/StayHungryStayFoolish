"""
RAGAS Evaluator Module

Implements the RAGAS evaluation framework integration for evaluating RAG systems.
Implements Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7.
"""

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from datasets import Dataset
from ragas import evaluate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Import metrics from the new recommended location (ragas v1.0+)
try:
    from ragas.metrics._faithfulness import Faithfulness
    from ragas.metrics._answer_relevance import ResponseRelevancy
    from ragas.metrics._context_precision import ContextPrecision
    from ragas.metrics._context_recall import ContextRecall
    
    # Create metric instances
    faithfulness = Faithfulness()
    answer_relevancy = ResponseRelevancy()
    context_precision = ContextPrecision()
    context_recall = ContextRecall()
except ImportError:
    # Fallback to legacy imports for older ragas versions
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )

from .models import EvaluationSample, EvaluationResult

if TYPE_CHECKING:
    from .rag_chain import RAGChain


class RagasEvaluator:
    """
    RAGAS 评测器
    
    使用 RAGAS 框架对 RAG 系统进行多维度评测，包括：
    - Faithfulness（忠实度）：答案与检索上下文的一致性
    - Answer Relevancy（答案相关性）：答案与问题的相关程度
    - Context Precision（上下文精确度）：检索上下文的精确性
    - Context Recall（上下文召回率）：检索上下文的完整性
    
    Attributes:
        rag_chain: RAG 链实例，用于获取答案和上下文
        metrics: RAGAS 评测指标列表
    """
    
    def __init__(
        self, 
        rag_chain: "RAGChain",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        embedding_model: str = "text-embedding-v4"
    ):
        """
        初始化评测器
        
        Args:
            rag_chain: RAG 链实例
            api_key: OpenAI API 密钥（可选，默认从环境变量读取）
            base_url: API Base URL（可选）
            model: 评测使用的 LLM 模型
            embedding_model: 评测使用的 Embedding 模型
        """
        self.rag_chain = rag_chain
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]
        
        # 配置 RAGAS 使用的 LLM 和 Embeddings
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        self.model = model
        self.embedding_model = embedding_model
        
        # 创建 LLM 和 Embeddings 实例
        self._llm = None
        self._embeddings = None
    
    def _get_llm(self):
        """获取配置好的 LLM 实例"""
        if self._llm is None:
            kwargs = {"api_key": self.api_key, "model": self.model}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._llm = ChatOpenAI(**kwargs)
        return self._llm
    
    def _get_embeddings(self):
        """获取配置好的 Embeddings 实例"""
        if self._embeddings is None:
            kwargs = {"api_key": self.api_key, "model": self.embedding_model}
            if self.base_url:
                kwargs["base_url"] = self.base_url
                kwargs["check_embedding_ctx_length"] = False
            self._embeddings = OpenAIEmbeddings(**kwargs)
        return self._embeddings
    
    def load_dataset(self, path: str) -> list[EvaluationSample]:
        """
        加载评测数据集
        
        从 JSON 文件加载评测数据集，文件格式应为：
        {
            "samples": [
                {
                    "question": "问题文本",
                    "ground_truth": "参考答案",
                    "contexts": ["可选的参考上下文"]  // 可选字段
                }
            ]
        }
        
        Args:
            path: 数据集文件路径 (JSON 格式)
            
        Returns:
            评测样本列表
            
        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果数据集格式不正确
            
        Validates:
            - Requirement 5.1: 加载评测数据集
            - Requirement 5.7: 数据集格式验证
        """
        file_path = Path(path)
        
        # 检查文件是否存在
        if not file_path.exists():
            raise FileNotFoundError(f"Evaluation dataset file not found: {path}")
        
        # 读取 JSON 文件
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in evaluation dataset: {e}")
        
        # 验证数据集格式
        # Validates Requirement 5.7: 数据集格式验证
        if not isinstance(data, dict):
            raise ValueError(
                "Invalid evaluation dataset format: expected a JSON object with 'samples' key"
            )
        
        if "samples" not in data:
            raise ValueError(
                "Invalid evaluation dataset format: missing 'samples' key"
            )
        
        samples_data = data["samples"]
        
        if not isinstance(samples_data, list):
            raise ValueError(
                "Invalid evaluation dataset format: 'samples' must be a list"
            )
        
        if len(samples_data) == 0:
            raise ValueError("Evaluation dataset is empty: 'samples' list has no items")
        
        # 解析样本
        samples = []
        for i, sample_data in enumerate(samples_data):
            if not isinstance(sample_data, dict):
                raise ValueError(
                    f"Invalid sample format at index {i}: expected a JSON object"
                )
            
            # 验证必需字段
            if "question" not in sample_data:
                raise ValueError(
                    f"Invalid sample format at index {i}: missing 'question' field"
                )
            
            if "ground_truth" not in sample_data:
                raise ValueError(
                    f"Invalid sample format at index {i}: missing 'ground_truth' field"
                )
            
            question = sample_data["question"]
            ground_truth = sample_data["ground_truth"]
            
            # 验证字段类型
            if not isinstance(question, str) or not question.strip():
                raise ValueError(
                    f"Invalid sample format at index {i}: 'question' must be a non-empty string"
                )
            
            if not isinstance(ground_truth, str) or not ground_truth.strip():
                raise ValueError(
                    f"Invalid sample format at index {i}: 'ground_truth' must be a non-empty string"
                )
            
            # 解析可选的 contexts 字段
            contexts = sample_data.get("contexts")
            if contexts is not None:
                if not isinstance(contexts, list):
                    raise ValueError(
                        f"Invalid sample format at index {i}: 'contexts' must be a list"
                    )
                for j, ctx in enumerate(contexts):
                    if not isinstance(ctx, str):
                        raise ValueError(
                            f"Invalid sample format at index {i}: 'contexts[{j}]' must be a string"
                        )
            
            # 创建 EvaluationSample
            sample = EvaluationSample(
                question=question,
                ground_truth=ground_truth,
                contexts=contexts,
            )
            samples.append(sample)
        
        return samples
    
    def prepare_evaluation_data(self, samples: list[EvaluationSample]) -> Dataset:
        """
        准备 RAGAS 评测数据
        
        对每个样本调用 RAG 链获取答案和上下文，
        构建 RAGAS 所需的 Dataset 格式。
        
        RAGAS 需要的数据格式：
        - question: 问题
        - answer: RAG 系统生成的答案
        - contexts: 检索到的上下文列表
        - ground_truth: 参考答案
        
        Args:
            samples: 评测样本列表
            
        Returns:
            HuggingFace Dataset 对象
            
        Raises:
            ValueError: 如果样本列表为空
        """
        if not samples:
            raise ValueError("Cannot prepare evaluation data: samples list is empty")
        
        # 准备 RAGAS 所需的数据结构
        questions = []
        answers = []
        contexts = []
        ground_truths = []
        
        for sample in samples:
            # 调用 RAG 链获取答案和上下文
            response = self.rag_chain.query(sample.question)
            
            questions.append(sample.question)
            answers.append(response.answer)
            contexts.append(response.contexts)
            ground_truths.append(sample.ground_truth)
        
        # 构建 HuggingFace Dataset
        # RAGAS 需要的列名：question, answer, contexts, ground_truth
        dataset = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        })
        
        return dataset
    
    def evaluate(self, dataset: Dataset) -> EvaluationResult:
        """
        执行 RAGAS 评测
        
        使用 RAGAS 框架计算以下指标：
        - Faithfulness（忠实度）
        - Answer Relevancy（答案相关性）
        - Context Precision（上下文精确度）
        - Context Recall（上下文召回率）
        
        Args:
            dataset: 准备好的评测数据集
            
        Returns:
            EvaluationResult 包含各项指标分数
            
        Validates:
            - Requirement 5.2: 计算 Faithfulness 指标评估答案忠实度
            - Requirement 5.3: 计算 Answer_Relevancy 指标评估答案相关性
            - Requirement 5.4: 计算 Context_Precision 指标评估上下文精确度
            - Requirement 5.5: 计算 Context_Recall 指标评估上下文召回率
        """
        # 调用 RAGAS evaluate 函数，使用自定义的 LLM 和 Embeddings
        # Validates Requirements 5.2, 5.3, 5.4, 5.5
        result = evaluate(
            dataset=dataset,
            metrics=self.metrics,
            llm=self._get_llm(),
            embeddings=self._get_embeddings(),
        )
        
        # 提取各项指标分数
        # RAGAS 返回的结果可能是字典或对象，需要兼容处理
        faithfulness_score = 0.0
        answer_relevancy_score = 0.0
        context_precision_score = 0.0
        context_recall_score = 0.0
        
        # 尝试从不同的属性/方法获取分数
        if hasattr(result, '__getitem__'):
            # 字典形式访问
            try:
                val = result["faithfulness"]
                faithfulness_score = float(val) if val is not None else 0.0
                val = result["answer_relevancy"]
                answer_relevancy_score = float(val) if val is not None else 0.0
                val = result["context_precision"]
                context_precision_score = float(val) if val is not None else 0.0
                val = result["context_recall"]
                context_recall_score = float(val) if val is not None else 0.0
            except (KeyError, TypeError, ValueError):
                pass
        
        # 如果上面没有获取到，尝试其他方式
        if faithfulness_score == 0.0 and answer_relevancy_score == 0.0:
            # 尝试从 to_pandas 获取平均值
            try:
                df = result.to_pandas()
                if "faithfulness" in df.columns:
                    val = df["faithfulness"].mean()
                    faithfulness_score = float(val) if val is not None and not (isinstance(val, float) and val != val) else 0.0
                if "answer_relevancy" in df.columns:
                    val = df["answer_relevancy"].mean()
                    answer_relevancy_score = float(val) if val is not None and not (isinstance(val, float) and val != val) else 0.0
                if "context_precision" in df.columns:
                    val = df["context_precision"].mean()
                    context_precision_score = float(val) if val is not None and not (isinstance(val, float) and val != val) else 0.0
                if "context_recall" in df.columns:
                    val = df["context_recall"].mean()
                    context_recall_score = float(val) if val is not None and not (isinstance(val, float) and val != val) else 0.0
            except Exception:
                pass
        
        # 提取详细分数（每个样本的分数）
        details = {}
        try:
            df = result.to_pandas()
            details = df.to_dict(orient="records")
        except Exception:
            # 如果无法获取详细分数，使用空字典
            details = {}
        
        # 构建并返回 EvaluationResult
        return EvaluationResult(
            faithfulness=faithfulness_score,
            answer_relevancy=answer_relevancy_score,
            context_precision=context_precision_score,
            context_recall=context_recall_score,
            details=details,
        )
    
    def generate_report(self, result: EvaluationResult) -> str:
        """
        生成评测报告
        
        生成格式化的评测报告，包含所有指标的分数和解释。
        
        Args:
            result: 评测结果
            
        Returns:
            格式化的评测报告字符串
            
        Validates:
            - Requirement 5.6: 输出包含所有指标的评测报告
        """
        # 构建报告标题
        report_lines = [
            "=" * 60,
            "RAGAS 评测报告",
            "=" * 60,
            "",
            "📊 评测指标总览",
            "-" * 40,
            "",
        ]
        
        # 添加各项指标分数
        # Validates Requirement 5.6: 输出包含所有指标的评测报告
        report_lines.extend([
            f"🎯 Faithfulness（忠实度）: {result.faithfulness:.4f}",
            f"   - 衡量生成答案与检索上下文的一致性",
            "",
            f"📝 Answer Relevancy（答案相关性）: {result.answer_relevancy:.4f}",
            f"   - 衡量答案与问题的相关程度",
            "",
            f"🔍 Context Precision（上下文精确度）: {result.context_precision:.4f}",
            f"   - 衡量检索上下文的精确性",
            "",
            f"📚 Context Recall（上下文召回率）: {result.context_recall:.4f}",
            f"   - 衡量检索上下文的完整性",
            "",
        ])
        
        # 添加综合评分
        avg_score = (
            result.faithfulness +
            result.answer_relevancy +
            result.context_precision +
            result.context_recall
        ) / 4
        
        report_lines.extend([
            "-" * 40,
            f"📈 综合评分: {avg_score:.4f}",
            "",
        ])
        
        # 添加评分解读
        report_lines.extend([
            "📋 评分解读",
            "-" * 40,
        ])
        
        if avg_score >= 0.8:
            report_lines.append("✅ 优秀：RAG 系统表现出色，各项指标均处于较高水平。")
        elif avg_score >= 0.6:
            report_lines.append("🔶 良好：RAG 系统表现良好，但仍有提升空间。")
        elif avg_score >= 0.4:
            report_lines.append("⚠️ 一般：RAG 系统表现一般，建议优化检索和生成策略。")
        else:
            report_lines.append("❌ 需改进：RAG 系统表现较差，需要重点优化。")
        
        report_lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(report_lines)
    
    def run_evaluation(self, dataset_path: str) -> tuple[EvaluationResult, str]:
        """
        运行完整的评测流程
        
        便捷方法，依次执行：加载数据集 -> 准备评测数据 -> 执行评测 -> 生成报告
        
        Args:
            dataset_path: 评测数据集文件路径
            
        Returns:
            元组 (EvaluationResult, 报告字符串)
        """
        # 1. 加载数据集
        samples = self.load_dataset(dataset_path)
        
        # 2. 准备评测数据
        dataset = self.prepare_evaluation_data(samples)
        
        # 3. 执行评测
        result = self.evaluate(dataset)
        
        # 4. 生成报告
        report = self.generate_report(result)
        
        return result, report
