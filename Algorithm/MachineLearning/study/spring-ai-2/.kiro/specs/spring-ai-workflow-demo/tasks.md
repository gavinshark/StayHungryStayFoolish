# Implementation Plan: Spring AI Workflow Demo

## Overview

基于 Spring AI 2.0 框架实现一个包含 3 个节点的顺序工作流 Demo 程序。每个节点通过 ChatService Bean 访问大模型，使用 qwen3.5-plus 模型，配置从环境变量读取。

## Tasks

- [x] 1. 创建项目基础结构
  - [x] 1.1 创建 Maven 项目配置文件 pom.xml
    - 配置 JDK 21、Spring Boot 3.x、Spring AI 2.0 依赖
    - 添加 JUnit 5、Mockito 测试依赖
    - _Requirements: 1.1, 1.2_
  
  - [x] 1.2 创建 Spring Boot 应用配置
    - 创建 application.yml 配置文件
    - 配置 OpenAI API 参数从环境变量读取
    - 配置 qwen3.5-plus 模型
    - _Requirements: 1.3, 2.3_
  
  - [x] 1.3 创建 Spring Boot 主应用类
    - 创建 Application.java 启动类
    - _Requirements: 1.1_

- [ ] 2. 实现核心数据模型
  - [x] 2.1 创建 WorkflowContext 类
    - 实现工作流上下文，包含 input、nodeOneOutput、nodeTwoOutput、finalOutput 字段
    - 添加 metadata 和 createdAt 字段
    - _Requirements: 3.4, 4.2_
  
  - [x] 2.2 创建 WorkflowException 异常类
    - 实现自定义工作流异常
    - _Requirements: 4.3_

- [ ] 3. 实现 Chat Bean 服务
  - [x] 3.1 创建 ChatService 类
    - 注入 ChatClient.Builder 并构建 ChatClient
    - 实现 chat(String prompt) 方法
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 4. 实现工作流节点
  - [x] 4.1 创建 WorkflowNode 接口
    - 定义 process(WorkflowContext) 方法
    - 定义 getName() 方法
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 4.2 实现 NodeOne 节点
    - 实现 WorkflowNode 接口
    - 注入 ChatService，调用大模型进行初始处理
    - 将结果存入 context.nodeOneOutput
    - _Requirements: 3.1, 3.4_
  
  - [x] 4.3 实现 NodeTwo 节点
    - 实现 WorkflowNode 接口
    - 从 context 获取 nodeOneOutput 作为输入
    - 调用大模型进行中间处理，结果存入 nodeTwoOutput
    - _Requirements: 3.2, 3.4_
  
  - [x] 4.4 实现 NodeThree 节点
    - 实现 WorkflowNode 接口
    - 从 context 获取 nodeTwoOutput 作为输入
    - 调用大模型进行最终处理，结果存入 finalOutput
    - _Requirements: 3.3, 3.4_

- [x] 5. Checkpoint - 确保所有节点编译通过
  - 确保所有代码编译通过，如有问题请询问用户。

- [ ] 6. 实现工作流引擎
  - [x] 6.1 创建 WorkflowEngine 类
    - 注入三个节点 Bean
    - 实现 execute(String input) 方法
    - 按顺序执行 NodeOne → NodeTwo → NodeThree
    - 在节点间传递 WorkflowContext
    - 处理异常并记录日志
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 7. 实现单元测试
  - [x] 7.1 创建 NodeOne 单元测试
    - 使用 JUnit 5 和 Mockito
    - Mock ChatService 的响应
    - 验证节点的输入输出转换逻辑
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 8. Final Checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

## Notes

- 所有配置参数从环境变量读取：OPENAI_API_KEY、OPENAI_BASE_URL
- 使用 qwen3.5-plus 模型
- 每个任务引用了对应的需求条款以便追溯
- Checkpoint 任务用于增量验证
