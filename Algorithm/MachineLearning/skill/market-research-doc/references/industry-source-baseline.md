# 行业实践来源基线

> 用户确认日期：2026-10-27  
> 数据核对日期：2026-10-27  
> 用途：市场调研文档第二章“行业现状”的候选来源池，不代表永久事实。每次使用都要重新核对链接、star、活跃度、版本与内容。

## 使用规则

- 行业现状至少覆盖：阿里巴巴（含天猫、蚂蚁）、腾讯、字节跳动、Codex、Anthropic、其他实践。
- 每个实践簇至少使用 2 个可追溯来源；优先“一手来源 + 独立验证”。
- GitHub star 只作发现信号；同时检查近 6 个月提交、release、issue/PR、license 和生产案例。
- QCon 2026 上海举办时间为 2026-10-22 至 10-24；QCon 只作为生产经验来源，关键结论仍需交叉验证。
- 没有专属议题时明确写“未发现”，不得把提到某产品的其他公司议题包装成该产品实践。
- 用户提供材料与公开来源统一编号，并标明“用户提供”。

## 1. 阿里巴巴（含天猫、蚂蚁）

| 来源 | 类型 | 拟用于 |
|---|---|---|
| [Open Code Review：百万真实任务验证的确定性工程与 Agent 协同](https://qcon.infoq.cn/2026/shanghai/presentation/7216)（阿里巴巴，李峥峰） | QCon | 确定性工程与 Agent 混合架构、代码评审规模化 |
| [alibaba/open-code-review](https://github.com/alibaba/open-code-review)（约 48.4k star，Apache-2.0） | GitHub | 与 QCon 议题交叉验证，了解开源实现与架构 |
| [AI 写完代码，谁来验证？——手淘 TEKO “写—验—修”自主闭环](https://qcon.infoq.cn/2026/shanghai/presentation/7278)（阿里淘天，泠乐） | QCon | 天猫场景下的 Agent 闭环、验证信号和工程质量 |
| [从 Harness 到 Loop：阿福 Agent 小队如何处理持续涌入的线上 Badcase](https://qcon.infoq.cn/2026/shanghai/presentation/7232)（蚂蚁集团，肖汉松） | QCon | 专家团、多 Agent 分工、线上问题闭环 |
| [从沙箱到执行边界：蚂蚁 AI Agent 的大规模企业级实践](https://qcon.infoq.cn/2026/shanghai/presentation/7213)（蚂蚁集团，林鑫） | QCon | 企业级执行沙箱、权限边界和规模化运行 |

## 2. 腾讯实践

| 来源 | 类型 | 拟用于 |
|---|---|---|
| [AI Agent 执行环境的规模化难题：CubeSandbox 的解法与实践](https://qcon.infoq.cn/2026/shanghai/presentation/7393)（腾讯云，龙进） | QCon | 长周期、有状态、大规模并行的 Agent 执行环境 |
| [TencentCloud/CubeSandbox](https://github.com/TencentCloud/CubeSandbox)（约 13.0k star） | GitHub | CubeSandbox 开源实现与生产架构交叉验证；使用前核对具体 license |
| [把 Loop 接进团队：游戏研发实践中的 Loop Engineering](https://qcon.infoq.cn/2026/shanghai/presentation/7309)（腾讯，任磊达） | QCon | 团队级 Agent Loop、组织落地与成本评估 |
| [失败一次，受益多次：测试 Agent 从记忆到持续学习](https://qcon.infoq.cn/2026/shanghai/presentation/7341)（腾讯，赵旭峰） | QCon | Agent 记忆、持续学习、测试场景闭环 |
| [Tencent/WeKnora](https://github.com/Tencent/WeKnora)（约 35.6k star） | GitHub | 企业知识库、RAG 与自主推理 Agent；使用前核对具体 license |

## 3. 字节跳动实践

| 来源 | 类型 | 拟用于 |
|---|---|---|
| [从 App 到 Agent：字节跳动 Supabase 的 Agent-Native 规模化实践](https://qcon.infoq.cn/2026/shanghai/presentation/7269)（字节跳动，张国强） | QCon | Agent-Native 应用形态、弹性资源与规模化基础设施 |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow)（约 84.5k star，MIT） | GitHub | 多 Agent 研究、编码、工具调用、沙箱与子 Agent 编排 |
| [coze-dev/coze-studio](https://github.com/coze-dev/coze-studio)（约 21.8k star，Apache-2.0） | GitHub | 可视化 Agent 工作流、插件和团队协作 |
| [bytedance/trae-agent](https://github.com/bytedance/trae-agent)（约 12.2k star，MIT） | GitHub | 软件工程 Agent、工具调用与执行流程 |

## 4. Codex 实践

| 来源 | 类型 | 拟用于 |
|---|---|---|
| [openai/codex](https://github.com/openai/codex)（约 131.1k star，Apache-2.0） | GitHub | Codex 产品能力、运行方式、开源实现与持续演进 |
| [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)（约 34.6k star，Apache-2.0） | GitHub | Codex 与 Claude Code 的协作、任务委派和代码评审 |
| [openai/skills](https://github.com/openai/skills)（约 28.3k star） | GitHub | 可复用 Skill 的组织方式与生态扩展；使用前核对 license |
| [DIBP-小红书数据 Agent 的语义层建设实践](https://qcon.infoq.cn/2026/shanghai/presentation/7343) | QCon | Codex 作为企业通用 Agent 的第三方采用旁证，不作为 Codex 官方实践 |

说明：QCon 2026 上海未发现 Codex 专属议题。OpenAI 官方文档站点在本次核对时返回 403，因此没有列入已核验来源；后续正式撰写应通过 openai-docs 流程再次核验官方文档。

## 5. Anthropic 实践

| 来源 | 类型 | 拟用于 |
|---|---|---|
| [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams) | 官方文档 | Agent Teams、共享任务、Agent 间通信与集中管理 |
| [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | 官方工程博客 | Multi-Agent 编排、并行研究、上下文隔离与效果/成本权衡 |
| [Building effective AI agents](https://www.anthropic.com/engineering/building-effective-agents) | 官方工程博客 | 从简单组合模式到自主 Agent 的工程原则 |
| [anthropics/claude-code](https://github.com/anthropics/claude-code)（约 153.5k star） | GitHub | Claude Code 产品生态与 Agent 工具链；使用前核对具体 license |
| [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)（约 8.4k star，MIT） | GitHub | Agent 编排、工具调用和程序化集成 |

## 6. 其他实践

| 来源 | 类型 | 拟用于 |
|---|---|---|
| [美团企业级 Agent 的平台化应用实践](https://qcon.infoq.cn/2026/shanghai/presentation/7335) | QCon | AgentOS、Runtime、Harness、Skill、权限治理与可观测 |
| [从“会用 Agent”到“组织级生产力”：网易帝王蟹多 Agent 设计与实践](https://qcon.infoq.cn/2026/shanghai/presentation/7277) | QCon | 多 Agent 分工、协作追踪、结果验证与经验沉淀 |
| [复杂业务 Agent 的持续进化：快手电商导购的 Harness Loop 实践](https://qcon.infoq.cn/2026/shanghai/presentation/7231) | QCon | 复杂业务 Agent、动态上下文和持续优化 |
| [DIBP-小红书数据 Agent 的语义层建设实践](https://qcon.infoq.cn/2026/shanghai/presentation/7343) | QCon | 企业规模 Agent 的 Context Layer 与多 Agent 演进 |
| [langgenius/dify](https://github.com/langgenius/dify)（约 159.7k star） | GitHub | Agent/工作流平台化实现；使用前核对具体 license |
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)（约 91.9k star，MIT） | GitHub | 软件工程 Agent 的开源实现与工程闭环 |
| [FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT)（约 71.0k star，MIT） | GitHub | 多 Agent 角色分工与协作框架 |

## 本次确认记录

- 2026-10-27：用户确认上述来源清单，同意据此修改 skill。
- 后续使用时，如 star、仓库归属、license、QCon 页面或技术结论发生变化，应更新本文件而不是沿用旧数字。
