<div align="center">
  <img src="https://raw.githubusercontent.com/imnotyz/Cortex/main/frontend/src/assets/cortex-mascot.png" alt="Cortex Mascot" width="280" />

  <h1>
    <img src="https://img.shields.io/badge/🧠Cortex-4FACFE?style=for-the-badge&labelColor=0a0f1a" alt="Cortex" />
  </h1>

  <p>
    <strong style="font-size: 1.2em; color: #4FACFE;">AI Agent 桌面应用 · 多模型协作 · 工作流编排</strong>
  </p>

  <p>
    <img src="https://img.shields.io/badge/version-1.1.0-4FACFE?style=flat-square&logo=github" alt="Version" />
    <img src="https://img.shields.io/badge/license-MIT-00d4ff?style=flat-square" alt="License" />
    <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-4FACFE?style=flat-square" alt="Platform" />
  </p>

  <p>
    <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white" alt="React" />
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Electron-28-47848F?style=flat-square&logo=electron&logoColor=white" alt="Electron" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  </p>
</div>

***

<div align="center">
  <h3>🌟 像大脑皮层一样，同时处理多件事 🌟</h3>
</div>

***

## ✨ 核心特性

<table align="center">
<tr>
<td align="center" width="200px">

**🚀 一键部署**
*无需服务器，无需 YAML*

⚡ 双击安装
🐍 内嵌 Python 环境
💾 便携 U 盘模式
🔒 数据本地存储

</td>
<td align="center" width="200px">

**💰 成本透明**
*消费心中有数*

📊 实时 Token 计数
📈 可视化成本图表
⚠️ 预算预警
🔄 模型成本对比

</td>
<td align="center" width="200px">

**🧩 Markdown 技能**
*不写代码就能扩展*

📝 编写 `SKILL.md`
🔗 MCP 协议支持
📦 Git 安装扩展
♻️ 热重载

</td>
<td align="center" width="200px">

**🔄 可视化工作流**
*构建 AI 流水线*

🎨 拖拽编辑器
🧩 16 种节点类型
📋 版本管理
🔍 运行追踪与调试

</td>
</tr>
<tr>
<td align="center" width="200px">

**🤖 可视化子代理**
*创建 AI 助手*

🎨 图形化代理创建器
📁 隔离工作区
🎯 自动任务分发
🧠 独立配置与记忆

</td>
<td align="center" width="200px">

**📚 知识库**
*你的第二大脑*

📄 多格式文档
📝 Markdown 笔记
🤖 笔记对话（范围 AI）
🧠 AI 智能提炼

</td>
<td align="center" width="200px">

**📡 多渠道**
*无处不在的聊天*

💬 桌面端 / 微信
🐦 Slack / Discord
✈️ Telegram / 钉钉
📧 邮件 / Webhook

</td>
<td align="center" width="200px">

**🖥️ 桌面优先**
*原生体验*

🚀 基于 Electron
⚡ 本地计算
🔄 实时流式传输
📊 全局快捷键

</td>
</tr>
</table>

***

## 🚀 快速开始

### 环境要求

- **Node.js** >= 18
- **Python** >= 3.10

### 安装与运行

```bash
# 1. 克隆仓库
git clone <仓库地址>
cd cortex

# 2. 安装前端依赖
npm install

# 3. 安装 Python 后端依赖（Python 3.10+）
pip install -r backend/requirements.txt

# 4. 启动开发模式
npm run dev
```

> 💡 `npm run dev` 同时启动：
>
> - 前端开发服务器（<http://localhost:3000>）
> - Electron 桌面窗口
> - Python 后端（由 Electron 自动启动）

***

## 🏗️ 项目架构

```
cortex/
├── agents/                 🧠 AI 代理工作区
│   ├── code-reviewer/      代码审查代理
│   ├── common/             通用代理模板
│   └── system/             系统代理配置
│       └── avatars/        代理头像资源
├── backend/                ⚡ Python 后端
│   ├── agent/              代理核心逻辑
│   │   ├── processors/     流式 / 非流式 / 长任务处理器
│   │   ├── compressor.py   上下文压缩
│   │   ├── subagent.py     子代理分发（带 ReAct 同步日志）
│   │   ├── notes_chat_agent.py  笔记对话范围代理
│   │   └── observation_*.py 观察提取与管理
│   ├── api/                FastAPI 服务接口
│   ├── channels/           多渠道支持
│   │   ├── desktop/        桌面端通道（WebSocket）
│   │   ├── wechat/         微信通道
│   │   ├── feishu/         飞书通道
│   │   ├── dingtalk/       钉钉通道
│   │   ├── slack/          Slack 通道
│   │   ├── discord/        Discord 通道
│   │   ├── telegram/       Telegram 通道
│   │   ├── email/          邮件通道
│   │   └── webhook/        Webhook 通道
│   ├── core/               核心模块
│   │   ├── config/         配置与校验
│   │   ├── events/         事件总线系统
│   │   ├── longtask/       长任务管理
│   │   ├── models/         数据模型
│   │   └── providers/      LLM 提供商适配器（OpenAI/Anthropic）
│   ├── data/               数据存储（SQLite）
│   │   ├── migrations/     数据库迁移（21 次迁移）
│   │   └── schema/         数据表结构（代理/会话/令牌/工作流/...）
│   ├── extensions/         插件系统
│   │   ├── builtin/        内置插件（定时任务等）
│   │   └── loader.py       动态插件加载器
│   ├── mcp/                MCP 协议集成
│   │   ├── server/         MCP 服务器连接与工具注册
│   │   └── llm_bridge.py   LLM-MCP 桥接
│   ├── services/           服务层
│   │   ├── cron/           定时任务服务
│   │   ├── tts/            文本转语音（OpenAI/MiMo 引擎）
│   │   ├── workflow/       工作流引擎与执行器
│   │   ├── knowledge_*.py  知识库服务
│   │   ├── knowledge_task_worker.py 提炼任务工作者（ReAct 日志）
│   │   ├── notes_chat_service.py   笔记对话会话/消息服务
│   │   ├── image_service.py 图片生成服务
│   │   └── llm_service.py  LLM 调用服务
│   ├── tools/              内置工具
│   │   ├── filesystem.py   文件系统工具
│   │   ├── shell.py        Shell 工具
│   │   ├── web_fetch.py    网页抓取工具
│   │   ├── browser/        Playwright 浏览器自动化
│   │   ├── image.py        图片处理工具
│   │   ├── cron.py         定时任务工具
│   │   ├── message.py      消息工具
│   │   ├── memory.py       记忆读取工具
│   │   ├── memory_write.py 记忆写入工具
│   │   ├── knowledge.py    知识库工具
│   │   ├── action.py       扩展动作工具
│   │   └── spawn.py        进程派生工具
│   └── utils/              工具函数
├── electron/               🖥️ Electron 主进程
│   ├── main.js             主入口（Python 生命周期、窗口管理）
│   └── preload.js          预加载脚本（IPC 桥接）
├── frontend/               🎨 React 前端
│   ├── src/
│   │   ├── pages/          页面组件
│   │   │   ├── Chat/       聊天界面（流式传输与工具展示）
│   │   │   ├── Config/     设置（提供商/代理/通道/多模态）
│   │   │   ├── Workflow/   可视化工作流编辑器（ReactFlow）
│   │   │   ├── Knowledge/  知识库（文档/笔记/图谱）
│   │   │   │   ├── library/LibraryChatDrawer  库内对话抽屉
│   │   │   │   └── hooks/  知识库钩子（useNotesChat, useChat, useChatDrawer）
│   │   │   ├── PdfViewerWindow  独立 PDF 阅读器 + 思维导图
│   │   │   ├── Agents/     子代理管理
│   │   │   ├── MCP/        MCP 服务器与工具管理
│   │   │   ├── Extensions/ 扩展市场
│   │   │   ├── Cron/       定时任务
│   │   │   ├── Tokens/     Token 用量仪表板
│   │   │   ├── History/    聊天历史浏览器
│   │   │   ├── Memory/     观察与记忆查看器
│   │   │   └── Workspace/  文件浏览器与编辑器
│   │   ├── components/     共享组件
│   │   │   ├── MessageList/ 消息渲染（迭代折叠）
│   │   │   ├── TTSPlayer/  音频播放
│   │   │   ├── TaskIndicator/ 任务状态指示器
│   │   │   ├── MermaidDiagram/ Mermaid 图表渲染
│   │   │   └── MindmapDiagram/   PDF 思维导图（react-d3-tree）
│   │   ├── workflow/       工作流引擎
│   │   │   ├── components/ 节点组件（16 种注册类型）
│   │   │   ├── hooks/      Zustand 工作流存储
│   │   │   ├── types/      类型定义
│   │   │   └── templates/  工作流模板
│   │   ├── contexts/       React 上下文（WebSocket, DistillTask）
│   │   ├── hooks/          自定义钩子（useChatState, useMermaid）
│   │   └── utils/          工具函数
│   └── package.json
├── build/                  🔧 构建资源（图标等）
├── workspace/              📂 工作区数据（运行时生成，git 忽略）
├── build_python.py         🐍 Python 打包脚本（PyInstaller）
├── tests/                  🧪 单元测试（310 个测试）
├── package.json            📋 项目配置与脚本
└── README-CN.md            📖 项目文档
```

### 技术栈

| 层级         | 技术                       | 说明                          |
| :----------- | :------------------------ | :----------------------------- |
| **前端**     | React 18 + Vite 5         | 现代 UI 框架                   |
|              | Ant Design 6              | 组件库                        |
|              | ReactFlow                 | 可视化工作流编辑器              |
|              | Monaco Editor             | 代码编辑器                     |
|              | ECharts 6                 | 数据可视化                     |
|              | PixiJS                    | 知识图谱 WebGL 渲染            |
|              | react-d3-tree             | PDF 思维导图渲染               |
|              | Zustand                   | 工作流状态管理                 |
| **后端**     | Python 3.10+ + FastAPI    | 高性能异步 Web 服务             |
|              | SQLite + SQLAlchemy       | 本地轻量数据库                 |
|              | Playwright                | 浏览器自动化                   |
|              | APScheduler               | 任务调度                      |
| **桌面端**   | Electron 28               | 跨平台桌面框架                 |
|              | electron-builder          | 应用打包工具                   |

### 运行时架构

```
┌─────────────────────────────────────────────┐
│                Electron 主进程                │
│  ┌──────────────────┐  ┌─────────────────┐   │
│  │  BrowserWindow   │  │ Python Process  │   │
│  │  (React SPA)     │  │ (cortex-server) │   │
│  │                  │  │                  │   │
│  │  electronAPI ────┼──┼──▶ FastAPI       │   │
│  │  (preload bridge)│  │    (WebSocket)   │   │
│  └──────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────┘
```

- **通信方式**：前端与后端之间全双工 WebSocket
- **请求-响应**：基于 `request_id` 的关联与超时机制
- **事件订阅**：实时事件的发布/订阅模式
- **Python 生命周期**：由 Electron 管理（自动启动/停止）

***

## 💬 聊天界面

美观的聊天界面，支持实时流式传输和工具调用可视化：

- **实时流式传输**：打字机效果，支持 Markdown 与代码高亮
- **工具调用展示**：可折叠的工具执行详情，显示参数与结果
- **迭代折叠**：自动折叠 Agent 的多轮思考过程
- **Thinking 标签页**：将推理内容与最终答案分离显示
- **成本展示**：每条消息显示 Token 消耗
- **重新生成**：支持重新生成或切换模型
- **TTS 播放**：文本转语音，支持 OpenAI 和 MiMo 引擎

***

## 🧠 智能代理

### ReAct 推理引擎

基于 ReAct（推理 + 行动）模式，Agent 循环执行：

```
用户输入 → Agent 思考 → 工具调用 → 观察结果 → ... → 最终答案
```

### 上下文压缩

长对话自动压缩，保持代理聚焦：

| 压缩策略     | 触发条件                      | 效果                     |
| :----------- | :---------------------------- | :----------------------- |
| **Token 阈值** | 超过 max_tokens × 2          | 移除旧消息               |
| **总结**       | 消息过多                      | 保留最后 5 条，总结其余   |
| **迭代折叠**   | 多轮工具调用                  | 折叠历史迭代              |

### 模型路由器 🧭

自动根据任务复杂度选择最优模型：

- **任务分类**：简单 / 中等 / 复杂 / 创意 / 代码 / 分析
- **成本预算**：每类任务设置月度预算上限
- **熔断器**：连续失败自动降级到备用模型
- **动态切换**：用户可随时覆盖自动选择

### 错误恢复 🛡️

4 级恢复策略，确保代理稳定运行：

| 级别 | 策略         | 说明                                      |
| :--- | :----------- | :---------------------------------------- |
| L1   | 重试         | 自动重试，指数退避（最多 3 次）             |
| L2   | 备用模型     | 切换到低成本备用模型                       |
| L3   | 上下文压缩 | 压缩历史，减少 Token 消耗                   |
| L4   | 降级通知     | 通知用户并优雅降级                         |

***

## 🔄 可视化工作流

基于 ReactFlow 的拖拽式工作流编辑器，支持 16 种节点类型：

### 节点类型

| 类型          | 节点                                                                                      |
| :------------ | :---------------------------------------------------------------------------------------- |
| **流程**      | 工作流开始、回答、工作流结束                                                               |
| **AI**        | LLM、问题分类器、内容提取器                                                                 |
| **工具**      | HTTP 请求、代码执行、读取文件、JSON 序列化/反序列化、文本编辑器                              |
| **逻辑**      | 条件分支、变量更新、循环、并行执行                                                         |
| **交互**      | 用户选择、表单输入、输入、插件输出                                                         |
| **代理**      | 代理节点、子工作流                                                                         |

### 关键能力

- **可视化编辑器**：拖拽画布，自动布局
- **节点测试**：在运行完整工作流前单独测试节点
- **版本管理**：保存、对比、恢复工作流版本
- **运行追踪**：逐步执行追踪，带变量检查
- **循环支持**：嵌套循环节点，专用内部画布
- **模板**：常见模式的预置模板（简单对话、条件分支）
- **自动保存**：5 秒防抖，脏状态指示器

***

## 📚 知识库

完整的知识管理系统，具备 AI 能力：

### 文档

- **多格式上传**：PDF、DOCX、XLSX、PPTX、图片等
- **分块上传**：大于 2MB 的文件自动分块（最大 500MB）
- **AI 提炼**：使用 AI 从文档中提取关键见解
- **批量操作**：批量提炼、移动、管理文档
- **预览**：应用内预览所有支持的格式
- **导入/导出**：基于 ZIP 的导入/导出，Obsidian 库导入

### 笔记

- **Markdown 编辑器**：功能完备的编辑器，支持维基链接导航
- **知识库系统**：创建、管理多个知识库
- **Obsidian 兼容**：导入现有 Obsidian 库

### 笔记对话

使用专用、可配置的 AI 代理与知识库对话：

- **范围访问**：限制代理到特定路径或知识库，进行聚焦对话
- **持久会话**：按范围保存聊天历史，可随时恢复
- **可配置代理**：复用任何已注册的子代理配置（模型、工具、系统提示词）
- **知识库感知工具**：内置全文搜索、笔记读取、链接列表、时间线遍历
- **记忆集成**：可选写入长期记忆和时间线观察
- **WebSocket 流式传输**：实时令牌流式传输，工具调用可见

### 库内对话抽屉

可调整大小的库内对话面板，用于在知识库视图中进行临时问答：

- **拖拽调整大小**：调整抽屉宽度以适应阅读流程
- **会话列表**：快速切换最近聊天会话
- **Markdown + KaTeX**：回复中丰富的数学和代码渲染
- **流式传输 UX**：实时令牌流式传输，支持复制到剪贴板

### 知识图谱

- **可视化探索**：WebGL 驱动的图谱可视化（PixiJS）
- **力导向布局**：交互式节点定位
- **关系映射**：发现知识节点之间的连接

### PDF 思维导图

将任何 PDF 转换为可导航的思维导图：

- **大纲提取**：解析 PDF 书签 / 标题为树形结构
- **交互式渲染**：平移、缩放、展开/折叠节点
- **独立窗口**：在独立的 Electron 窗口中打开 PDF 阅读器
- **内联批注**：阅读时高亮和下划线
- **PDF 对话**：基于当前文档进行问答

***

## 📡 多渠道支持

将 Cortex 连接到您喜爱的平台：

| 通道        | 特性                                            |
| :---------- | :---------------------------------------------- |
| 🖥️ 桌面端  | 全功能原生应用，WebSocket 实时                  |
| 💬 微信     | 二维码登录，发送/接收，自动回复                 |
| 🐦 Slack    | Bolt SDK 集成，频道与私信支持                   |
| 🎮 Discord  | 机器人集成，服务器与频道消息                    |
| ✈️ Telegram | 机器人 API，聊天与群组支持                      |
| 📱 钉钉     | Stream 协议，对话消息                           |
| 📧 邮件     | SMTP/IMAP 集成                                  |
| 🔗 Webhook  | 通用 HTTP Webhook，用于自定义集成               |
| 🐦 飞书     | Lark SDK，事件订阅                              |

***

## 🔌 扩展生态

### 技能扩展（只需 Markdown）

编写 `SKILL.md` 文件来教授 AI 新能力：

```markdown
---
name: "代码审查"
emoji: "🔍"
---

审查代码时，检查：
1. 安全问题（SQL 注入、XSS）
2. 性能瓶颈
3. 命名规范
```

放入 `workspace/extensions/my-skill/SKILL.md` 并重启即可激活。

### 扩展市场

- 浏览、安装社区扩展
- 三种扩展类型：**技能**、**插件**、**工作者**
- 搜索、按类型筛选、按热度排序
- 一键安装，支持环境变量配置

### MCP 协议支持

- 连接任何 MCP 服务器（stdio / HTTP SSE）
- 自动发现工具，无需手动配置
- 可视化权限管理，支持每个工具启用/禁用
- 实时连接状态监控

***

## 🛠️ 内置工具

| 类别         | 工具                                            | 说明                      |
| :----------- | :---------------------------------------------- | :------------------------ |
| 📁 文件系统  | `read`, `write`, `edit`, `list`                  | 文件读写操作              |
| 🖥️ 系统     | `shell`, `spawn`                                 | 命令执行                  |
| 🌐 网络      | `web_fetch`                                      | 网页内容抓取              |
| 🖥️ 浏览器    | `browser_navigate`, `browser_click`, `browser_screenshot`, ... | Playwright 浏览器自动化 |
| 🖼️ 图片      | `image_understand`, `image_generate`             | AI 图片处理              |
| ⏰ 定时任务  | `cron_add`, `cron_list`, `cron_remove`           | 任务调度                  |
| 💬 消息      | `send_message`                                   | 多渠道消息发送            |
| 🧠 记忆      | `memory_read`, `memory_write`                    | 代理记忆操作              |
| 📚 知识库    | `knowledge_search`, `knowledge_query`            | 知识库检索                |
| ⚡ 动作      | `action`                                         | 执行扩展动作              |

***

## 🧠 观察与记忆

Cortex 自动从对话中提取见解：

### 观察类型

| 类型              | 说明                                     |
| :---------------- | :--------------------------------------- |
| 🎯 顿悟            | 关键发现和顿悟时刻                        |
| 🔧 问题-解决方案   | 问题-解决方案对                          |
| ⚙️ 工作原理        | 工作原理说明                              |
| 📝 变更记录        | 变更记录                                 |
| 🔍 发现            | 新发现                                   |
| ❓ 存在原因         | 原理和原因                               |
| 📋 决策            | 设计决策                                 |
| ⚖️ 权衡            | 权衡分析                                 |
| 💡 通用            | 通用观察                                 |

### 记忆特性

- **自动提取**：AI 识别并从对话中提取观察
- **提升为记忆**：将重要观察提升为长期记忆
- **用户画像**：追踪用户偏好和模式
- **上下文深度**：查看带有周围对话上下文的观察

***

## ⚙️ 可视化配置

所有配置都有图形界面，无需 YAML：

| 配置项           | 说明                                                           |
| :---------------- | :-------------------------------------------------------------- |
| **模型提供商**    | 添加 OpenAI/Anthropic/DeepSeek，支持多提供商切换               |
| **代理设置**      | 模型、最大 Token、温度、最大迭代次数、压缩                       |
| **通道配置**      | 微信二维码登录、Telegram 机器人、Slack 应用、钉钉等             |
| **工具开关**      | 一键启用/禁用工具，设置超时                                     |
| **工作区**        | 隔离工作区，独立配置和记忆                                       |
| **预算限制**      | 设置月度 Token 上限，超预算提醒                                 |
| **多模态**        | 图片理解、TTS 等多模态设置                                      |

***

## 💰 Token 用量可视化

实时监控每次对话的成本：

- 📊 **实时统计**：输入/输出 Token、缓存命中、补全 Token、子代理用量
- 📈 **历史趋势**：按天查看消耗（7/14/30 天）
- 📋 **明细表**：按提供商和按模型的成本分析
- ⚠️ **预算预警**：设置上限，自动警告

***

## ⏰ 智能定时任务

不只是通知，而是实际工作：

- **子代理执行**：任务在隔离代理中运行，执行真实操作
- **灵活调度**：支持 ISO 时间、间隔秒数、Cron 表达式
- **上下文继承**：任务可以访问创建时的会话记忆
- **持久存储**：任务保存在 SQLite 中，重启后仍然保留
- **通道投递**：将任务结果发送到特定通道

***

## 🗂️ 工作区管理

每个项目都有自己的隔离工作区：

```
workspace/
├── project-a/          # 项目 A
│   ├── extensions/     # 专属扩展
│   ├── memory/         # 长期记忆
│   └── history/        # 聊天历史
├── project-b/          # 项目 B
│   └── ...
```

- 切换工作区 = 切换完整配置和记忆
- 支持导出/导入工作区
- 团队共享：导出工作区，同事导入即可使用
- 内置文件浏览器，带 Monaco 编辑器
- 多格式预览：PDF、DOCX、XLSX、PPTX、图片、Markdown

***

## 💬 聊天历史

- 所有对话保存在本地 SQLite
- 3 级组织：通道 → 会话 → 实例
- 按消息类型筛选，跨历史搜索
- 随时返回到任何历史会话
- 支持并行多会话

***

## 🤖 可视化子代理

通过 UI 创建、管理专用代理：

- **可视化编辑**：修改 `SOUL.md` 来配置角色、工具、模型
- **一键创建**：填写名称自动生成模板配置
- **隔离工作区**：每个子代理都有自己的配置和记忆
- **主从分发**：主代理自动调用合适的子代理
- **工具与扩展绑定**：为每个代理分配特定工具和扩展

***

## 📦 构建与发布

### 开发命令

| 命令               | 说明                      |
| :----------------- | :------------------------ |
| `npm run dev`      | 开发模式（前端 + Electron） |
| `npm run dev:frontend` | 仅前端开发服务器        |
| `npm run dev:electron` | 仅 Electron            |

### 构建命令

| 命令                  | 说明                      |
| :-------------------- | :------------------------ |
| `npm run build:frontend` | 构建 React 前端          |
| `npm run build:python`   | 打包 Python 后端          |
| `npm run build`          | 完整构建（前端 + Electron）|

### 打包与发布

| 命令              | 说明              | 输出                                  |
| :---------------- | :---------------- | :------------------------------------ |
| `npm run dist`    | 打包当前平台      | 自动按平台选择                        |
| `npm run dist:mac` | macOS 打包       | DMG + ZIP（通用：x64/arm64）         |
| `npm run dist:win` | Windows 打包     | NSIS 安装包 + 便携版                  |
| `npm run dist:linux` | Linux 打包      | AppImage + DEB                       |

> 📂 输出：`dist-electron/`
> 📖 详细指南：[README_BUILD.md](./README_BUILD.md)

***

## 🔧 模型配置

在应用设置面板中添加 API 密钥：

### 支持的提供商

| 提供商    | 代表模型                                      |
| :-------- | :-------------------------------------------- |
| OpenAI    | GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo, o1        |
| Anthropic | Claude 3 Opus, Claude 3 Sonnet, Claude 3 Haiku |
| Google    | Gemini Pro, Gemini Ultra                       |
| DeepSeek  | DeepSeek Chat, DeepSeek Coder                  |
| 阿里巴巴   | 通义千问系列                                   |
| 百度      | 文心一言系列                                   |
| 自定义     | 任何 OpenAI 兼容 API 端点                     |

### 配置步骤

1. 打开应用 → 设置 → 模型提供商
2. 添加提供商（选择或自定义）
3. 输入 API Key 和 Base URL
4. 选择要使用的模型
5. 保存并启动

***

## 🔌 MCP 协议

Cortex 完全支持**模型上下文协议（MCP）**：

- 🔗 连接任何 MCP 服务器
- 🛠️ 使用 MCP 提供的工具
- 🔐 安全权限管理
- 🔄 实时连接监控
- 📋 可视化服务器管理（添加/编辑/删除/重连）
- 🔍 自动发现工具，支持每个工具启用/禁用

### 支持的传输方式

- **stdio**：本地进程通信
- **HTTP SSE**：基于 HTTP 的服务器发送事件

***

## 🤖 代理工作区

代理系统支持连续记忆和个性化：

### 配置文件

| 文件              | 用途                                         |
| :---------------- | :------------------------------------------- |
| `SOUL.md`         | 代理灵魂 - 核心原则与性格                    |
| `IDENTITY.md`     | 代理身份 - 自我介绍                           |
| `AGENTS.md`       | 工作区指南 - 使用说明                         |
| `MEMORY.md`       | 长期记忆 - 重要信息持久化                     |
| `memory/YYYY-MM-DD.md` | 每日笔记 - 每日事件记录                |

### 创建自定义代理

在 `agents/` 目录中创建新文件夹，添加配置文件即可创建自定义代理。

***

## 📂 项目结构

```
cortex/
├── backend/              # Python 后端（FastAPI）
├── frontend/             # React 前端（Vite）
├── electron/             # Electron 主进程
├── build/                # 构建资源（图标等）
├── build_python.py       # Python 打包脚本
├── workspace/            # ⚠️ 运行时生成目录（git 忽略）
│   ├── agents/           #   - 用户创建的代理配置
│   ├── extensions/       #   - 已安装的扩展
│   ├── files/            #   - 工作区文件
│   ├── images/           #   - 生成的图片
│   └── ...               #   - 其他运行时数据
└── scripts/              # 辅助脚本
```

> **注意**：`workspace/` 目录在运行时创建，包含用户数据、代理配置和生成的文件。它被 `.gitignore` 排除在版本控制之外。

***

## 📖 文档

- 📘 [构建指南](./README_BUILD.md) - 打包与发布详情
- 📗 [代理指南](./agents/system/AGENTS.md) - 代理工作区使用
- 📕 [身份说明](./agents/system/IDENTITY.md) - 了解 Cortex 是谁
- 🧠 [灵魂核心](./agents/system/SOUL.md) - 代理核心原则
- 🔌 [MCP 文档](./backend/mcp/README.md) - MCP 协议集成
- 🌐 [浏览器工具](./backend/tools/browser/README.md) - 浏览器自动化指南

***

## 🤝 贡献

欢迎提交 Issue 和 Pull Request：

- 🐛 Bug 报告
- ✨ 新功能
- 📝 文档改进
- 🎨 UI/UX 优化

***

## 📋 更新日志

### 2026-06

| 日期       | 版本   | 变更                                                       |
| :--------- | :----- | :--------------------------------------------------------- |
| 2026-06-06 | v1.1.0 | 💬 新增：笔记对话 — 知识笔记的范围 AI 代理                |
| 2026-06-06 | v1.1.0 | 📚 新增：库内对话抽屉 — 可调整大小的库内对话               |
| 2026-06-06 | v1.1.0 | 🧠 新增：PDF 思维导图渲染（react-d3-tree）                  |
| 2026-06-06 | v1.1.0 | 📄 新增：独立 PDF 阅读器窗口（批注 + 对话）                |
| 2026-06-06 | v1.1.0 | 🐧 新增：Linux 打包（AppImage + DEB）                      |
| 2026-06-06 | v1.1.0 | 🔧 改进：子代理 / 提炼 ReAct 执行日志                      |
| 2026-06-06 | v1.1.0 | 🧹 清理：移除旧版 pixel-theme 备份文件                     |
| 2026-06-07 | v1.1.0 | 🌙 新增：深色/浅色主题切换，支持系统偏好检测               |
| 2026-06-07 | v1.1.0 | 💰 新增：预算预警 — 月度消费上限与进度条                   |
| 2026-06-07 | v1.1.0 | 🔧 修复：修正节点类型数量（24→16）和版本徽章               |

### 2026-08

| 日期       | 版本   | 变更                                                       |
| :--------- | :----- | :--------------------------------------------------------- |
| 2026-08-18 | v1.1.0 | 🧭 新增：模型路由器（任务分类 + 成本预算 + 熔断器）        |
| 2026-08-18 | v1.1.0 | 🛡️ 新增：错误恢复（4 级：重试 → 备用模型 → 压缩 → 通知）   |
| 2026-08-18 | v1.1.0 | 📋 新增：场景模板（客服 + 数据分析）                       |
| 2026-08-18 | v1.1.0 | 📊 新增：代理分析服务（成本聚合 + 优化）                    |
| 2026-08-18 | v1.1.0 | 🐳 新增：Docker 多阶段构建 + docker-compose 部署           |
| 2026-08-18 | v1.1.0 | 🔧 新增：CI/CD（代码检查 + 测试 + 构建）                   |
| 2026-08-18 | v1.1.0 | 📈 新增：性能基准脚本（4 类算法）                          |
| 2026-08-18 | v1.1.0 | ✅ 新增：验证循环（4 级验证 + 反馈注入）                    |
| 2026-08-18 | v1.1.0 | 🛡️ 新增：动作钩子（危险命令拦截 + 文件安全 + Token 预算） |
| 2026-08-18 | v1.1.0 | 📝 新增：3 个 SKILL.md 方法论模板（清单/工作流/专家）      |
| 2026-08-18 | v1.1.0 | 🧪 新增：310 单元测试（路由器 45 + 恢复 17 + 模板 34 + 验证 42 + 钩子 43 + 引擎 25 + 分析 29 + 压缩器 20 + 浏览器 45 + 子代理 10）|
| 2026-08-18 | v1.1.0 | 📖 改进：README 重写（快速开始 + 对比 + 路线图）           |
| 2026-08-17 | v1.1.0 | 🔧 修复：全局重命名 Octopus → Cortex（代码、文档、资源）   |

### 2026-05

| 日期       | 版本   | 变更                                                       |
| :--------- | :----- | :--------------------------------------------------------- |
| 2026-05-17 | v1.0.0 | 🔄 新增：可视化工作流编辑器，16 种节点类型                 |
| 2026-05-17 | v1.0.0 | 📚 新增：知识库（文档、笔记、图谱）                        |
| 2026-05-17 | v1.0.0 | 📡 新增：多渠道支持（Slack/Discord/Telegram/...）           |
| 2026-05-17 | v1.0.0 | 🌐 新增：Playwright 浏览器自动化工具                         |
| 2026-05-17 | v1.0.0 | 🧠 新增：观察与记忆系统                                     |

### 2026-03

| 日期       | 版本   | 变更                                                       |
| :--------- | :----- | :--------------------------------------------------------- |
| 2026-03-29 | v1.0.0 | 🔊 新增：文本转语音（TTS）功能支持                          |
| 2026-03-29 | v1.0.0 | 🤖 新增：子代理管理和 UI 改进                               |
| 2026-03-28 | v1.0.0 | 🗜️ 新增：上下文压缩和 LLM 重试优化                         |
| 2026-03-25 | v1.0.0 | 📄 新增：PDF、DOCX 和 Excel 文件支持                       |
| 2026-03-24 | v1.0.0 | 💬 新增：微信通道（二维码登录和消息）                       |
| 2026-03-22 | v1.0.0 | 🖼️ 新增：无边框窗口支持                                    |
| 2026-03-20 | v1.0.0 | 🎉 发布：项目重命名为 Cortex                               |

***

<div align="center">

### 🧠 Cortex 让你的工作更高效 🧠

<img src="https://raw.githubusercontent.com/imnotyz/Cortex/main/frontend/src/assets/cortex-logo.png" width="80" style="border-radius: 10px;" />

<sub>用 ❤️ 和 🧠 构建</sub>

</div>
