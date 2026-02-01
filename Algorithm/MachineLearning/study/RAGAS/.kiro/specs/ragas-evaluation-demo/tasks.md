# Implementation Plan: RAGAS Evaluation Demo

## Overview

基于 LangChain 框架实现一个完整的 RAGAS 评测演示系统。采用增量开发方式，先实现核心组件，再集成为完整流水线，最后添加评测功能。

## Tasks

- [x] 1. 项目初始化和依赖配置
  - 创建项目目录结构
  - 创建 `requirements.txt` 包含所有依赖：langchain, langchain-openai, langchain-community, faiss-cpu, ragas, datasets, python-dotenv, pyyaml
  - 创建 `config/config.example.yaml` 配置示例文件
  - 创建 `.env.example` 环境变量示例
  - _Requirements: 7.2, 7.3, 7.4_

- [x] 2. 实现文档处理器
  - [x] 2.1 实现 DocumentProcessor 类
    - 使用 LangChain TextLoader 和 DirectoryLoader 加载文档
    - 使用 RecursiveCharacterTextSplitter 进行文本分块
    - 支持配置 chunk_size 和 chunk_overlap
    - 实现 load_file 和 load_directory 方法
    - _Requirements: 1.1, 1.2, 1.4, 1.5_
  
  - [x]* 2.2 编写 DocumentProcessor 属性测试
    - **Property 1: Document Load Round-Trip**
    - **Property 2: Text Chunk Size Constraint**
    - **Property 3: Text Chunk Overlap Preservation**
    - **Validates: Requirements 1.1, 1.2, 1.4, 1.5**
  
  - [x]* 2.3 编写 DocumentProcessor 错误处理测试
    - **Property 12: Invalid Path Error Handling**
    - **Validates: Requirements 1.3**

- [x] 3. 实现向量存储管理器
  - [x] 3.1 实现 VectorStoreManager 类
    - 使用 LangChain OpenAIEmbeddings 进行向量化
    - 使用 LangChain FAISS 进行向量存储
    - 实现 create_from_documents、add_documents、similarity_search 方法
    - 实现 save 和 load 方法支持持久化
    - 实现 as_retriever 方法返回 LangChain Retriever
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 3.4_
  
  - [x]* 3.2 编写 VectorStoreManager 属性测试
    - **Property 4: Vector Store Round-Trip**
    - **Property 5: Incremental Document Addition**
    - **Property 6: Top-K Retrieval Constraint**
    - **Property 7: Search Result Content Validity**
    - **Validates: Requirements 2.2, 2.3, 2.5, 3.2, 3.3, 3.4**

- [x] 4. Checkpoint - 确保文档处理和向量存储测试通过
  - 确保所有测试通过，如有问题请询问用户

- [x] 5. 实现 RAG 链
  - [x] 5.1 实现 RAGChain 类
    - 使用 LangChain ChatOpenAI 作为 LLM
    - 使用 LangChain RetrievalQA.from_chain_type 构建链
    - 配置 return_source_documents=True 返回检索文档
    - 实现 query 方法返回 RAGResponse
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [x]* 5.2 编写 RAGChain 属性测试
    - **Property 8: RAG Response Context Inclusion**
    - **Validates: Requirements 4.1**

- [x] 6. 实现 RAGAS 评测器
  - [x] 6.1 实现 RagasEvaluator 类
    - 实现 load_dataset 方法加载 JSON 格式评测数据集
    - 实现 prepare_evaluation_data 方法调用 RAG 链获取答案和上下文
    - 实现 evaluate 方法调用 ragas.evaluate 计算指标
    - 实现 generate_report 方法生成格式化报告
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [x]* 6.2 编写 RagasEvaluator 属性测试
    - **Property 9: Evaluation Dataset Load Consistency**
    - **Property 10: RAGAS Metrics Range Constraint**
    - **Property 11: Evaluation Report Completeness**
    - **Property 13: Invalid Dataset Format Error Handling**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7**

- [x] 7. Checkpoint - 确保所有组件测试通过
  - 确保所有测试通过，如有问题请询问用户

- [x] 8. 创建示例数据和演示脚本
  - [x] 8.1 创建示例文档
    - 在 `data/documents/` 目录创建示例 Markdown 文档
    - 内容涵盖 RAG 和 RAGAS 相关知识
    - _Requirements: 6.1_
  
  - [x] 8.2 创建评测数据集
    - 在 `data/evaluation/test_dataset.json` 创建评测数据集
    - 包含 3-5 个问答样本和参考答案
    - _Requirements: 6.2_
  
  - [x] 8.3 实现 main.py 演示脚本
    - 加载配置文件和环境变量
    - 依次执行：文档加载 → 向量化 → 创建 RAG 链 → 运行评测
    - 打印清晰的评测结果报告
    - 处理配置缺失情况并提示用户
    - _Requirements: 6.3, 6.4, 6.5, 6.6_

- [x] 9. 创建项目文档
  - [x] 9.1 创建 README.md
    - 项目介绍和功能说明
    - 安装步骤和依赖说明
    - 配置说明（API 密钥设置）
    - 使用方法和运行示例
    - 项目结构说明
    - _Requirements: 7.1_

- [x] 10. Final Checkpoint - 确保所有测试通过并验证演示流程
  - 确保所有测试通过
  - 验证 main.py 可以正常运行（需要有效的 API 密钥）
  - 如有问题请询问用户

## Notes

- 标记 `*` 的任务为可选测试任务，可跳过以加快 MVP 开发
- 每个任务都引用了具体的需求条款以保证可追溯性
- Checkpoint 任务用于阶段性验证，确保增量开发的正确性
- 属性测试验证通用正确性属性，单元测试验证具体示例和边界情况
