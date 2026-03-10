# RAGAS 评测框架

## 什么是 RAGAS？

RAGAS（Retrieval-Augmented Generation Assessment）是一个专门用于评估 RAG 系统性能的开源框架。它提供了一套标准化的评测指标，帮助开发者量化和改进 RAG 系统的质量。

## RAGAS 的核心评测指标

### 1. Faithfulness（忠实度）

忠实度衡量生成的答案与检索到的上下文之间的一致性。

- **定义**：答案中的每个声明是否都可以从给定的上下文中推断出来
- **分数范围**：0.0 到 1.0，越高越好
- **重要性**：高忠实度意味着答案不会编造上下文中没有的信息

### 2. Answer Relevancy（答案相关性）

答案相关性衡量生成的答案与原始问题的相关程度。

- **定义**：答案是否直接回答了用户的问题
- **分数范围**：0.0 到 1.0，越高越好
- **重要性**：确保答案不偏离主题，直接解决用户需求

### 3. Context Precision（上下文精确度）

上下文精确度衡量检索到的上下文中有多少是真正相关的。

- **定义**：检索结果中相关文档的比例
- **分数范围**：0.0 到 1.0，越高越好
- **重要性**：高精确度意味着检索系统能够准确找到相关信息

### 4. Context Recall（上下文召回率）

上下文召回率衡量检索系统是否找到了所有相关的信息。

- **定义**：参考答案中的信息有多少被检索到的上下文覆盖
- **分数范围**：0.0 到 1.0，越高越好
- **重要性**：高召回率意味着不会遗漏重要信息

## 如何使用 RAGAS

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

# 准备评测数据
dataset = Dataset.from_dict({
    "question": ["问题1", "问题2"],
    "answer": ["答案1", "答案2"],
    "contexts": [["上下文1"], ["上下文2"]],
    "ground_truth": ["参考答案1", "参考答案2"]
})

# 执行评测
result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
```

## 评测结果解读

- **0.8 以上**：优秀，系统表现出色
- **0.6 - 0.8**：良好，有一定提升空间
- **0.4 - 0.6**：一般，需要优化
- **0.4 以下**：较差，需要重点改进
