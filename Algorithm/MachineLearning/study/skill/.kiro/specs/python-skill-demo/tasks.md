# 实现计划: Python Skill Demo

## 概述

本实现计划将 Python Skill Demo 的设计转换为可执行的编码任务。采用增量开发方式，从核心数据结构开始，逐步构建注册、调度和交互功能。

## 任务列表

- [x] 1. 创建项目结构和核心 Skill 类
  - [x] 1.1 创建 skill.py 文件，实现 Skill 数据类
    - 使用 @dataclass 装饰器定义 Skill 类
    - 包含 name、description、keywords、handler 四个字段
    - 添加类型注解：name: str, description: str, keywords: List[str], handler: Callable[[], str]
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ]* 1.2 编写 Property 1 属性测试：Skill 结构完整性
    - **Property 1: Skill 结构完整性**
    - 使用 hypothesis 生成随机 Skill 实例
    - 验证所有必需字段存在且类型正确
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

  - [ ]* 1.3 编写 Property 2 属性测试：Skill handler 返回字符串
    - **Property 2: Skill handler 返回字符串**
    - 使用 hypothesis 生成随机 Skill 实例
    - 验证调用 handler 返回字符串类型
    - **Validates: Requirements 1.5**

- [x] 2. 实现 SkillRegistry 注册管理
  - [x] 2.1 创建 registry.py 文件，实现 SkillRegistry 类
    - 实现 __init__ 方法，初始化内部 Dict[str, Skill] 存储
    - 实现 register(skill: Skill) 方法，支持覆盖同名 skill
    - 实现 get_all_skills() 方法，返回所有已注册 skill 列表
    - 实现 find_by_name(name: str) 方法，根据名称查找 skill
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ]* 2.2 编写 Property 3 属性测试：Skill 注册 round-trip
    - **Property 3: Skill 注册 round-trip**
    - 使用 hypothesis 生成随机 Skill 列表
    - 验证注册后 get_all_skills() 返回正确数量的 skill
    - **Validates: Requirements 2.2**

  - [ ]* 2.3 编写 Property 4 属性测试：重复注册覆盖
    - **Property 4: 重复注册覆盖**
    - 使用 hypothesis 生成两个同名 Skill
    - 验证后注册的 skill 覆盖先注册的
    - **Validates: Requirements 2.3**

- [x] 3. 检查点 - 确保核心组件测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 4. 实现 SkillDispatcher 调度器
  - [x] 4.1 创建 dispatcher.py 文件，实现 SkillDispatcher 类
    - 实现 __init__(registry: SkillRegistry) 方法
    - 实现 dispatch(query: str) 方法
    - 实现关键词匹配逻辑：转小写、子字符串匹配
    - 处理空查询和无匹配情况，返回 "未找到匹配的 skill"
    - 捕获 handler 执行异常，返回错误提示
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [ ]* 4.2 编写 Property 5 属性测试：关键词匹配调用 skill
    - **Property 5: 关键词匹配调用 skill**
    - 使用 hypothesis 生成 Skill 和包含关键词的查询
    - 验证 dispatch 返回 handler 执行结果
    - **Validates: Requirements 3.2, 3.4**

  - [ ]* 4.3 编写 Property 6 属性测试：无匹配返回提示
    - **Property 6: 无匹配返回提示**
    - 使用 hypothesis 生成不包含任何关键词的查询
    - 验证 dispatch 返回 "未找到匹配的 skill"
    - **Validates: Requirements 3.3**

- [x] 5. 实现 Demo Skill
  - [x] 5.1 创建 demo_skill.py 文件，实现 greeting skill
    - 实现 create_greeting_skill() 工厂函数
    - 设置 name 为 "greeting"
    - 设置 keywords 包含 "你好"、"hello"、"hi"
    - 实现 handler 返回友好问候语
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 5.2 编写 Demo Skill 单元测试
    - 验证 skill name 为 "greeting"
    - 验证 keywords 包含指定关键词
    - 验证 handler 返回问候语字符串
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 6. 检查点 - 确保调度和 Demo Skill 测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [x] 7. 实现主程序交互界面
  - [x] 7.1 创建 main.py 文件，实现命令行交互
    - 实现欢迎信息和使用说明显示
    - 实现用户输入循环
    - 集成 SkillRegistry 和 SkillDispatcher
    - 注册 greeting skill
    - 处理 "exit" 和 "quit" 退出命令
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 7.2 编写主程序单元测试
    - 测试退出命令识别
    - 测试欢迎信息输出
    - _Requirements: 5.2, 5.4_

- [x] 8. 创建测试配置文件
  - [x] 8.1 创建 tests/conftest.py 文件
    - 配置 pytest fixtures
    - 配置 hypothesis 设置（最少 100 次迭代）
    - 创建通用测试辅助函数
    - _Requirements: 所有属性测试依赖_

- [x] 9. 最终检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

## 备注

- 标记 `*` 的任务为可选任务，可跳过以加快 MVP 开发
- 每个任务都引用了具体的需求条款以确保可追溯性
- 检查点确保增量验证
- 属性测试验证通用正确性属性
- 单元测试验证具体示例和边界情况
