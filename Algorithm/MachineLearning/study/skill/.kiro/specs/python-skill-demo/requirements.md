# 需求文档

## 简介

本功能实现一个基于 Python 的 Skill Demo 程序。该程序定义一个可调用的 demo skill，并根据用户的提问智能匹配和调用相应的 skill，展示基本的 skill 调度机制。

## 术语表

- **Skill**: 一个可执行的功能单元，包含名称、描述和执行逻辑
- **Skill_Registry**: 管理和存储所有已注册 skill 的组件
- **Skill_Dispatcher**: 根据用户输入匹配并调用相应 skill 的组件
- **User_Query**: 用户输入的问题或指令

## 需求

### 需求 1: Skill 定义

**用户故事:** 作为开发者，我希望能够定义一个 demo skill，以便展示 skill 的基本结构和功能。

#### 验收标准

1. THE Skill SHALL 包含名称（name）属性用于唯一标识
2. THE Skill SHALL 包含描述（description）属性用于说明功能
3. THE Skill SHALL 包含关键词（keywords）列表用于匹配用户查询
4. THE Skill SHALL 包含可执行的处理函数（handler）
5. WHEN Skill 被调用时，THE Skill SHALL 返回执行结果字符串

### 需求 2: Skill 注册

**用户故事:** 作为开发者，我希望能够注册 skill 到系统中，以便后续可以被调用。

#### 验收标准

1. THE Skill_Registry SHALL 提供注册 skill 的方法
2. THE Skill_Registry SHALL 存储所有已注册的 skill
3. WHEN 注册重复名称的 skill 时，THE Skill_Registry SHALL 覆盖已有的 skill
4. THE Skill_Registry SHALL 提供获取所有已注册 skill 列表的方法

### 需求 3: 用户查询处理

**用户故事:** 作为用户，我希望输入问题后系统能调用相应的 skill，以便获得回答。

#### 验收标准

1. WHEN 用户输入查询时，THE Skill_Dispatcher SHALL 解析查询内容
2. WHEN 查询匹配到 skill 关键词时，THE Skill_Dispatcher SHALL 调用对应的 skill
3. WHEN 查询未匹配到任何 skill 时，THE Skill_Dispatcher SHALL 返回提示信息 "未找到匹配的 skill"
4. THE Skill_Dispatcher SHALL 返回 skill 的执行结果给用户

### 需求 4: Demo Skill 实现

**用户故事:** 作为用户，我希望有一个可用的 demo skill，以便测试系统功能。

#### 验收标准

1. THE Demo_Skill SHALL 命名为 "greeting"
2. THE Demo_Skill SHALL 响应包含 "你好"、"hello"、"hi" 等关键词的查询
3. WHEN Demo_Skill 被调用时，THE Demo_Skill SHALL 返回友好的问候语

### 需求 5: 主程序交互

**用户故事:** 作为用户，我希望通过命令行与程序交互，以便测试 skill 调用功能。

#### 验收标准

1. THE Main_Program SHALL 提供命令行交互界面
2. WHEN 程序启动时，THE Main_Program SHALL 显示欢迎信息和使用说明
3. THE Main_Program SHALL 循环接收用户输入直到用户输入退出命令
4. WHEN 用户输入 "exit" 或 "quit" 时，THE Main_Program SHALL 退出程序
