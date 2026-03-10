# Requirements Document

## Introduction

本项目是一个 RAGAS（Retrieval-Augmented Generation Assessment）评测演示工程，旨在展示如何使用 RAGAS 框架评估 RAG 系统的性能。项目包含一个完整的本地 RAG 系统实现和 RAGAS 评测流程，无需依赖外部数据库服务，可直接运行体验。

## Glossary

- **RAG_System**: 检索增强生成系统，包含文档加载、文本分块、向量化、检索和生成回答的完整流程
- **Document_Loader**: 文档加载器，负责从本地文件读取文档内容
- **Text_Chunker**: 文本分块器，将长文档切分为适合向量化的小块
- **Vector_Store**: 向量存储，使用本地内存或文件存储文档向量
- **Retriever**: 检索器，根据查询从向量存储中检索相关文档块
- **Generator**: 生成器，调用大模型 API 基于检索结果生成回答
- **RAGAS_Evaluator**: RAGAS 评测器，使用 RAGAS 框架评估 RAG 系统性能
- **Faithfulness**: 忠实度指标，衡量生成答案与检索上下文的一致性
- **Answer_Relevancy**: 答案相关性指标，衡量答案与问题的相关程度
- **Context_Precision**: 上下文精确度指标，衡量检索上下文的精确性
- **Context_Recall**: 上下文召回率指标，衡量检索上下文的完整性
- **Evaluation_Dataset**: 评测数据集，包含问题、参考答案和相关上下文

## Requirements

### Requirement 1: 文档加载与处理

**User Story:** 作为用户，我希望系统能够加载本地文档并进行预处理，以便后续的向量化和检索。

#### Acceptance Criteria

1. WHEN 用户指定文档路径 THEN THE Document_Loader SHALL 读取文档内容并返回文本数据
2. WHEN 文档格式为 TXT 或 Markdown THEN THE Document_Loader SHALL 正确解析文档内容
3. IF 文档路径不存在或无法读取 THEN THE Document_Loader SHALL 返回明确的错误信息
4. WHEN 文档加载成功 THEN THE Text_Chunker SHALL 将文档切分为指定大小的文本块
5. WHEN 进行文本分块 THEN THE Text_Chunker SHALL 保留块之间的重叠以保持上下文连贯性

### Requirement 2: 向量化与存储

**User Story:** 作为用户，我希望系统能够将文本块向量化并存储在本地，以便进行相似度检索。

#### Acceptance Criteria

1. WHEN 文本块准备就绪 THEN THE Vector_Store SHALL 使用嵌入模型将文本转换为向量
2. THE Vector_Store SHALL 将向量数据存储在本地内存或文件中
3. WHEN 向量存储初始化 THEN THE Vector_Store SHALL 支持增量添加新向量
4. IF 向量化过程失败 THEN THE Vector_Store SHALL 返回明确的错误信息
5. WHEN 向量存储持久化 THEN THE Vector_Store SHALL 支持保存和加载向量索引

### Requirement 3: 检索功能

**User Story:** 作为用户，我希望系统能够根据查询检索最相关的文档块，以便生成准确的回答。

#### Acceptance Criteria

1. WHEN 用户提交查询 THEN THE Retriever SHALL 将查询向量化并计算与存储向量的相似度
2. WHEN 检索完成 THEN THE Retriever SHALL 返回相似度最高的 K 个文档块
3. THE Retriever SHALL 支持配置返回结果数量 K
4. WHEN 检索结果返回 THEN THE Retriever SHALL 包含文档块内容和相似度分数
5. IF 向量存储为空 THEN THE Retriever SHALL 返回空结果列表

### Requirement 4: 回答生成

**User Story:** 作为用户，我希望系统能够基于检索结果调用大模型生成回答，以便获得问题的答案。

#### Acceptance Criteria

1. WHEN 检索结果准备就绪 THEN THE Generator SHALL 构建包含上下文的提示词
2. WHEN 提示词构建完成 THEN THE Generator SHALL 调用外部大模型 API 生成回答
3. THE Generator SHALL 支持配置大模型 API 密钥和模型名称
4. IF 大模型 API 调用失败 THEN THE Generator SHALL 返回明确的错误信息并支持重试
5. WHEN 回答生成成功 THEN THE Generator SHALL 返回生成的文本回答

### Requirement 5: RAGAS 评测

**User Story:** 作为用户，我希望能够使用 RAGAS 框架评估 RAG 系统的性能，以便了解系统的优缺点。

#### Acceptance Criteria

1. WHEN 评测开始 THEN THE RAGAS_Evaluator SHALL 加载评测数据集
2. THE RAGAS_Evaluator SHALL 计算 Faithfulness 指标评估答案忠实度
3. THE RAGAS_Evaluator SHALL 计算 Answer_Relevancy 指标评估答案相关性
4. THE RAGAS_Evaluator SHALL 计算 Context_Precision 指标评估上下文精确度
5. THE RAGAS_Evaluator SHALL 计算 Context_Recall 指标评估上下文召回率
6. WHEN 评测完成 THEN THE RAGAS_Evaluator SHALL 输出包含所有指标的评测报告
7. IF 评测数据集格式不正确 THEN THE RAGAS_Evaluator SHALL 返回明确的错误信息

### Requirement 6: 演示流程

**User Story:** 作为用户，我希望有一个完整的演示脚本，能够一键运行整个 RAG 系统和 RAGAS 评测流程。

#### Acceptance Criteria

1. THE Demo_Script SHALL 提供示例文档数据用于演示
2. THE Demo_Script SHALL 提供示例评测数据集包含问题和参考答案
3. WHEN 运行演示脚本 THEN THE Demo_Script SHALL 依次执行文档加载、向量化、检索、生成和评测
4. WHEN 演示完成 THEN THE Demo_Script SHALL 打印清晰的评测结果报告
5. THE Demo_Script SHALL 提供配置文件用于设置 API 密钥和模型参数
6. IF 配置缺失 THEN THE Demo_Script SHALL 提示用户完成必要配置

### Requirement 7: 项目结构与文档

**User Story:** 作为用户，我希望项目结构清晰、文档完善，以便快速理解和使用。

#### Acceptance Criteria

1. THE Project SHALL 提供 README 文档说明安装和使用方法
2. THE Project SHALL 提供 requirements.txt 列出所有依赖包
3. THE Project SHALL 采用模块化结构组织代码
4. THE Project SHALL 提供配置示例文件说明必要的环境变量
