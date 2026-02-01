"""
RAGAS Evaluation Demo - Main Entry Point

This script demonstrates the complete RAG system and RAGAS evaluation workflow.
"""

import os
import sys
from pathlib import Path

import yaml

from src.document_processor import DocumentProcessor
from src.vector_store import VectorStoreManager
from src.rag_chain import RAGChain
from src.evaluator import RagasEvaluator


def load_config() -> dict:
    """加载配置文件"""
    config_path = Path("config/config.yaml")
    
    if not config_path.exists():
        print("❌ 错误: 未找到 config/config.yaml 配置文件")
        return {}
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_openai_config(config: dict) -> dict:
    """
    获取 OpenAI API 配置
    
    - api_key, base_url: 从系统环境变量读取
    - model, embedding_model: 从 config.yaml 读取
    
    Args:
        config: 配置字典
    
    Returns:
        dict: 包含 api_key, base_url, model, embedding_model
    """
    openai_config = config.get("openai", {})
    
    return {
        # 从系统环境变量读取
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "base_url": os.environ.get("OPENAI_BASE_URL"),
        # 从 config.yaml 读取
        "model": openai_config.get("model", "gpt-3.5-turbo"),
        "embedding_model": openai_config.get("embedding_model", "text-embedding-v4"),
    }


def main():
    """主函数：运行完整的 RAG 系统和 RAGAS 评测流程"""
    print("=" * 60)
    print("🚀 RAGAS Evaluation Demo")
    print("=" * 60)
    print()
    
    # 1. 检查配置
    print("📋 步骤 1: 检查配置...")
    config = load_config()
    openai_config = get_openai_config(config)
    api_key = openai_config["api_key"]
    base_url = openai_config["base_url"]
    model = openai_config["model"]
    embedding_model = openai_config["embedding_model"]
    
    if not api_key:
        print("❌ 错误: 未找到 OpenAI API Key")
        print()
        print("请设置系统环境变量:")
        print("  export OPENAI_API_KEY=your-key")
        print("  export OPENAI_BASE_URL=https://your-api-endpoint (可选)")
        print()
        print("模型配置在 config/config.yaml 文件中:")
        print("  openai.model: gpt-3.5-turbo")
        print("  openai.embedding_model: text-embedding-v4")
        sys.exit(1)
    
    print("✅ API Key 已配置")
    if base_url:
        print(f"✅ API Base URL: {base_url}")
    print(f"✅ LLM Model: {model}")
    print(f"✅ Embedding Model: {embedding_model}")
    print()
    
    # 加载其他配置
    chunk_size = config.get("document_processing", {}).get("chunk_size", 500)
    chunk_overlap = config.get("document_processing", {}).get("chunk_overlap", 50)
    retrieval_k = config.get("retrieval", {}).get("k", 4)
    
    # 2. 加载文档
    print("📄 步骤 2: 加载文档...")
    doc_processor = DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    documents_path = Path("data/documents")
    if not documents_path.exists() or not any(documents_path.glob("*.md")):
        print("❌ 错误: 未找到示例文档")
        print(f"请确保 {documents_path} 目录下有 Markdown 文档")
        sys.exit(1)
    
    documents = doc_processor.load_directory(str(documents_path), glob="**/*.md")
    print(f"✅ 已加载 {len(documents)} 个文档块")
    print()
    
    # 3. 创建向量存储
    print("🔢 步骤 3: 创建向量存储...")
    
    vector_store = VectorStoreManager(api_key=api_key, embedding_model=embedding_model, base_url=base_url)
    vector_store.create_from_documents(documents)
    print(f"✅ 向量存储已创建，包含 {vector_store.get_document_count()} 个向量 (模型: {embedding_model})")
    print()
    
    # 4. 创建 RAG 链
    print("🔗 步骤 4: 创建 RAG 链...")
    rag_chain = RAGChain(
        vector_store_manager=vector_store,
        api_key=api_key,
        model=model,
        k=retrieval_k,
        base_url=base_url
    )
    print(f"✅ RAG 链已创建 (模型: {model}, k={retrieval_k})")
    print()
    
    # 5. 测试查询
    print("💬 步骤 5: 测试查询...")
    test_question = "什么是 RAG？"
    print(f"问题: {test_question}")
    
    response = rag_chain.query(test_question)
    print(f"回答: {response.answer[:200]}..." if len(response.answer) > 200 else f"回答: {response.answer}")
    print(f"检索到 {len(response.contexts)} 个上下文")
    print()
    
    # 6. 运行 RAGAS 评测
    print("📊 步骤 6: 运行 RAGAS 评测...")
    dataset_path = Path("data/evaluation/test_dataset.json")
    
    if not dataset_path.exists():
        print("❌ 错误: 未找到评测数据集")
        print(f"请确保 {dataset_path} 文件存在")
        sys.exit(1)
    
    evaluator = RagasEvaluator(
        rag_chain,
        api_key=api_key,
        base_url=base_url,
        model=model,
        embedding_model=embedding_model
    )
    
    try:
        result, report = evaluator.run_evaluation(str(dataset_path))
        print()
        print(report)
    except Exception as e:
        print(f"⚠️  评测过程中出现错误: {e}")
        print("这可能是由于 API 调用限制或网络问题导致的")
        print("请稍后重试或检查 API 配置")
    
    print()
    print("🎉 演示完成！")


if __name__ == "__main__":
    main()
