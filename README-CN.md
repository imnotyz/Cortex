<div align="center">
  <img src="https://raw.githubusercontent.com/imnotyz/Cortex/main/frontend/src/assets/cortex-mascot.png" alt="Cortex Mascot" width="260" />

  # Cortex

  **面向产品前期创意探索的本地优先可视化 AI Agent 工作台**

  简体中文 · [English](./README.md)

  ![Version](https://img.shields.io/badge/version-1.1.0-4FACFE?style=flat-square)
  ![License](https://img.shields.io/badge/license-MIT-00d4ff?style=flat-square)
  ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-4FACFE?style=flat-square)
  ![Tests](https://img.shields.io/badge/tests-310%20unit%20tests-success?style=flat-square)

  ![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white)
  ![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
  ![Electron](https://img.shields.io/badge/Electron-28-47848F?style=flat-square&logo=electron&logoColor=white)
  ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
</div>

---

## Cortex 是什么？

产品、概念设计和创意团队在前期探索阶段，通常需要经历需求澄清、资料收集、方向发散、方案比较、局部深化和最终收敛。传统的线性 AI 对话只能保留一条连续上下文，当方案出现多个分支时，用户很难回到此前的决策点，也难以比较不同路径或追溯结果来源。

Cortex 将 **AI Agent** 与 **可视化 Workflow** 结合，把创意过程从一段不可见的聊天记录，转化为可分支、可比较、可回放的任务画布。

你可以让 Agent 使用本地文件、Shell、浏览器、知识库和外部工具完成任务，同时在画布中查看节点状态、工具调用、变量变化、执行轨迹和 Token 成本。

> Cortex 目前处于持续开发阶段，部分界面、能力与数据结构仍可能发生变化。

## 为什么是可视化 Agent？

线性对话适合回答单一问题，却不擅长承载非线性的创意过程。Cortex 的核心设计原则包括：

- **允许发散**：同一问题可以产生多个探索分支，而不是覆盖前一个答案。
- **支持比较**：不同方向可以并列查看、独立修改和重新组合。
- **过程可见**：用户能够看到 Agent 调用了什么工具、执行到了哪一步。
- **人机共决策**：用户可以在关键节点选择方向、补充条件或接管任务。
- **结果可追溯**：通过版本、Trace 和上下文记录保留方案演变过程。
- **本地优先**：工作区、对话、运行状态和大部分用户数据默认保存在本地。

## 典型工作流程

```text
输入问题或 Design Brief
          │
          ▼
     Agent 拆解任务
          │
          ▼
资料检索 ── 方向发散 ── 条件筛选
   │           │            │
   └────── 方案比较与重组 ──┘
                    │
                    ▼
             人工确认与深化
                    │
                    ▼
           输出结果与完整 Trace
```

Cortex 不试图替代人的创意判断，而是帮助用户管理探索过程，让 Agent 负责资料处理、重复执行和方案扩展，把方向选择与最终决策留给用户。

## 核心能力

| 能力 | 说明 |
| --- | --- |
| **可视化工作流** | 通过拖拽画布组织 Agent、工具、条件分支、循环、并行任务和人工交互 |
| **16 类工作流节点** | 覆盖流程控制、LLM、内容提取、代码、文件、HTTP、变量、表单、Agent 和子工作流 |
| **Agent 执行** | 支持工具调用、流式输出、多轮执行、子代理和长任务 |
| **版本与 Trace** | 保存工作流版本、节点运行状态、变量变化和完整执行轨迹 |
| **本地工具** | 支持文件读写、Shell、网页获取、浏览器自动化、图片和消息工具 |
| **知识工作区** | 支持文档、Markdown 笔记、PDF 对话、知识图谱和 AI 提炼 |
| **可靠性控制** | 提供模型路由、失败重试、上下文压缩、验证循环和安全 Hook |
| **成本治理** | 展示 Token 用量、模型成本、历史趋势和预算预警 |
| **扩展能力** | 支持 Markdown Skill、插件、Worker 和 MCP Server |
| **多渠道访问** | 支持桌面端、微信、飞书、钉钉、Slack、Discord、Telegram、邮件和 Webhook |

## 可视化工作流

工作流编辑器基于 ReactFlow 构建，支持以下节点类型：

| 分类 | 节点能力 |
| --- | --- |
| **流程** | 开始、回答、结束 |
| **AI** | LLM、问题分类、内容提取 |
| **工具** | HTTP、代码执行、文件读取、JSON 和文本处理 |
| **逻辑** | 条件分支、变量更新、循环、并行执行 |
| **交互** | 用户选择、表单输入 |
| **Agent** | Agent 节点、子工作流 |

工作流支持：

- 拖拽编辑与自动保存
- 节点级独立测试
- 条件分支、循环和并行执行
- 工作流版本管理
- 节点状态与变量检查
- 完整运行 Trace
- 模板复用与子工作流组合

## Agent Runtime

Cortex 使用基于 ReAct 的工具调用循环：

```text
用户目标
   ↓
Agent 推理
   ↓
选择并调用工具
   ↓
观察执行结果
   ↓
验证结果或继续迭代
   ↓
输出结果与执行记录
```

每个项目可以拥有独立的 Agent 配置、工具、文件、记忆和对话历史，避免不同任务之间的上下文相互污染。

### 子代理

复杂任务可以委派给具有独立提示词、工具、工作区和记忆的子代理：

- 可视化创建和配置子代理
- 同步或异步执行任务
- 隔离子代理的试错过程
- 聚合多个子任务结果
- 为不同子代理绑定专属工具和 Skill

## 可靠性与安全

工具型 Agent 的价值不仅取决于模型能力，还取决于任务执行、错误恢复和结果验证。

Cortex 提供以下运行时控制：

- **模型路由**：结合任务类型、成本预算和可用状态选择模型。
- **错误恢复**：重试 → 备用模型 → 上下文压缩 → 通知用户。
- **上下文压缩**：裁剪冗余工具输出，并将长任务压缩为结构化摘要。
- **验证循环**：检查空输出、占位内容和未通过验证的执行结果。
- **迭代限制**：限制最大执行轮数，降低死循环造成的资源消耗。
- **危险操作拦截**：针对高风险命令、文件访问和 Token 预算设置 Hook。
- **执行可观测性**：记录工具调用、节点状态、失败原因和成本信息。

这些机制可以降低可避免的执行失败，但不能保证任意工具调用绝对安全。处理敏感文件或连接外部系统前，请检查模型权限和工具配置。

## 评测与优化

Cortex 将 Agent 评测拆分为三个层级：

1. **单能力评测**：检查需求理解、节点选择、参数生成和工具调用。
2. **执行过程评测**：检查任务是否按预期推进，能否处理异常并避免无效循环。
3. **端到端评测**：检查最终结果是否满足任务约束，以及用户是否需要人工接管。

推荐结合以下方式开展评测：

- 程序规则与结构化校验
- LLM Judge 交叉评分
- 人工抽样复核
- 与聊天式 Agent 基线对照
- Bad Case 分类、修复和回归
- Token 成本与任务质量联合分析

仓库中的 `benchmarks/` 用于存放性能和评测脚本。项目不会在缺少可复现记录的情况下宣称评测提升。

## 知识与记忆

Cortex 提供本地知识工作区：

- 上传并预览 PDF、DOCX、XLSX、PPTX、图片和 Markdown
- 将文档提炼为可复用知识
- 创建和管理 Markdown 知识库
- 导入 Obsidian Vault
- 针对指定文件、目录、Vault 或 PDF 进行范围对话
- 通过知识图谱和 PDF 思维导图查看信息关系
- 将重要观察沉淀为长期记忆

## Skill、插件与 MCP

### Markdown Skill

通过 `SKILL.md` 为 Agent 提供可复用的方法和约束：

```markdown
---
name: concept-review
description: Review an early-stage product concept
---

When reviewing a concept:

1. Clarify the target user and context.
2. Identify the unresolved user problem.
3. Generate at least three alternative directions.
4. Compare value, feasibility, and risk.
5. Preserve assumptions and open questions.
```

### MCP

Cortex 支持通过 stdio 或 HTTP SSE 连接 MCP Server：

- 自动发现外部工具
- 查看连接状态
- 控制单个工具的启用权限
- 将工具绑定到特定 Agent 或子代理

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- npm
- 至少一个受支持模型的 API Key

### 安装与运行

```bash
git clone https://github.com/imnotyz/Cortex.git
cd Cortex

npm install
pip install -r backend/requirements.txt

npm run dev
```

`npm run dev` 会启动 Vite 前端和 Electron 桌面应用，Electron 负责管理本地 Python 后端。

启动后，前往 **设置 → 模型提供商** 配置模型。

## 常用命令

| 命令 | 说明 |
| --- | --- |
| `npm run dev` | 启动前端和 Electron 开发环境 |
| `npm run dev:frontend` | 只启动 Vite 前端 |
| `npm run dev:electron` | 启动 Electron 并连接前端开发服务器 |
| `npm run build:frontend` | 构建 React 前端 |
| `npm run build:python` | 打包 Python 后端 |
| `npm run build` | 构建前端和 Electron 应用 |
| `npm run dist` | 打包当前平台 |
| `npm run dist:mac` | 构建 macOS DMG 和 ZIP |
| `npm run dist:win` | 构建 Windows 安装包和便携版本 |

详细说明请参阅 [README_BUILD.md](./README_BUILD.md)。

## 系统架构

```text
┌──────────────────────────────────────────────────────────┐
│                    Electron Desktop                      │
│  React UI ── WebSocket / IPC ── FastAPI Agent Runtime   │
└───────────────────────────────┬──────────────────────────┘
                                │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
  Agent Runtime          Workflow Engine        Knowledge Services
  Tools / Memory         Nodes / Traces          Docs / Notes / Graph
        │                       │                        │
        └──────────── SQLite + Local Workspace ──────────┘
                                │
          Model Providers · MCP Servers · Channels
```

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 桌面端 | Electron 28、electron-builder |
| 前端 | React 18、Vite 5、Ant Design、ReactFlow、Monaco Editor、ECharts、PixiJS |
| 后端 | Python 3.10+、FastAPI、WebSocket、SQLAlchemy、SQLite |
| Agent Runtime | Tool Loop、Sub-agent、Memory、Compression、Routing、Recovery、Verification |
| 自动化 | Playwright、APScheduler、MCP |
| 质量保障 | CI、pre-commit、Benchmark、310 个单元测试 |

## 项目结构

```text
Cortex/
├── backend/
│   ├── agent/          # Agent 循环、处理器、子代理和记忆
│   ├── channels/       # 桌面端与外部消息渠道
│   ├── core/           # 事件、模型提供商、配置和长任务
│   ├── data/           # SQLite Schema 与迁移
│   ├── extensions/     # 扩展加载与内置扩展
│   ├── mcp/            # MCP 连接与工具注册
│   ├── services/       # 知识、工作流、定时任务、图像和 LLM 服务
│   └── tools/          # 文件、Shell、浏览器、记忆和知识工具
├── frontend/           # React 桌面界面
├── electron/           # Electron 主进程与 Preload
├── tests/              # 单元测试
├── benchmarks/         # 性能与评测脚本
├── build/              # 打包资源
├── docker-compose.yml
├── Dockerfile
└── README_BUILD.md
```

运行时用户数据会写入 `workspace/`，该目录默认不进入版本控制。

## 当前状态与后续方向

当前版本已经包含：

- Agent 与子代理管理
- 16 类节点的可视化工作流
- 版本管理与执行 Trace
- 本地知识工作区
- 观察与长期记忆
- MCP 与 Markdown Skill
- 多渠道消息适配
- 模型路由、错误恢复、验证循环与安全 Hook
- Token 分析、成本预算、CI、Benchmark 和单元测试

后续将重点完善：

- 面向产品与概念设计的工作流模板
- 方案分支的并列比较和局部重组体验
- 工作流版本之间的结果差异展示
- 可复现的 Agent 评测集与回放机制
- 任务质量、人工接管率与成本的联合分析

## 贡献

欢迎提交 Issue 和 Pull Request。请尽量保持改动聚焦，说明用户可感知的行为变化，并为逻辑改动补充测试。

请勿提交 API Key、用户工作区或本地运行数据。

## License

Cortex 使用 [MIT License](./LICENSE.txt)。

<div align="center">
  <sub>Built with ❤️ and 🧠</sub>
</div>
