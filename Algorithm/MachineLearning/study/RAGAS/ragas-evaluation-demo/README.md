# RAGAS Evaluation Demo

一个完整的 RAGAS（Retrieval-Augmented Generation Assessment）评测演示项目，展示如何使用 RAGAS 框架评估 RAG 系统的性能。

## 功能特性

- 🔄 **完整的 RAG 流程**：文档加载 → 文本分块 → 向量化 → 检索 → 生成
- 📊 **RAGAS 评测**：支持 Faithfulness、Answer Relevancy、Context Precision、Context Recall 四项指标
- 🛠️ **基于 LangChain**：使用 LangChain 框架构建，易于扩展
- 💾 **本地向量存储**：使用 FAISS，无需外部数据库服务

## 项目结构

```
ragas-evaluation-demo/
├── src/
│   ├── document_processor.py  # 文档加载和分块
│   ├── vector_store.py        # FAISS 向量存储
│   ├── rag_chain.py           # RAG 链实现
│   ├── evaluator.py           # RAGAS 评测器
│   └── models.py              # 数据模型
├── data/
│   ├── documents/             # 示例文档
│   └── evaluation/            # 评测数据集
├── config/
│   └── config.example.yaml    # 配置示例
├── tests/                     # 单元测试
├── main.py                    # 演示入口
├── requirements.txt           # 依赖列表
└── README.md
```

## 安装

1. 克隆项目并进入目录：
```bash
cd ragas-evaluation-demo
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

### 方式一：环境变量（推荐）

创建 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置 API Key：
```
OPENAI_API_KEY=your-api-key-here

# 可选：自定义 API Base URL（用于代理或自定义端点）
OPENAI_API_BASE=https://your-custom-endpoint.com/v1
```

### 方式二：配置文件

```bash
cp config/config.example.yaml config/config.yaml
```

编辑 `config/config.yaml` 设置参数。

## 使用

运行演示：
```bash
python main.py
```

演示流程：
1. 加载 `data/documents/` 目录下的文档
2. 创建向量存储
3. 构建 RAG 链
4. 执行测试查询
5. 运行 RAGAS 评测并输出报告

## RAGAS 评测指标

| 指标 | 说明 |
|------|------|
| Faithfulness | 答案与检索上下文的一致性 |
| Answer Relevancy | 答案与问题的相关程度 |
| Context Precision | 检索上下文的精确性 |
| Context Recall | 检索上下文的完整性 |

## 运行测试

```bash
python -m pytest tests/ -v
```

## License

MIT License
