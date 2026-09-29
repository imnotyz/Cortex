<div align="center">
  <img src="https://raw.githubusercontent.com/imnotyz/Cortex/main/frontend/src/assets/cortex-mascot.png" alt="Cortex mascot" width="260" />

  # Cortex

  **A local-first desktop workspace for building, running, and observing AI agents.**

  [简体中文](./README-CN.md) · English

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

## What is Cortex?

Cortex is an open-source AI Agent desktop application that brings conversations, tools, memory, knowledge, workflows, subagents, scheduled tasks, cost tracking, and execution traces into one place.

Unlike a chat-only client, Cortex is designed around **tasks that actually run**. Agents can use local tools, access project-scoped knowledge, delegate work, execute visual workflows, recover from failures, and preserve context across sessions. User data and runtime state are stored locally by default.

> Cortex is under active development. Interfaces and data schemas may change before a stable release.

## Highlights

| Capability | What it provides |
| --- | --- |
| **Agent workspace** | Project-isolated identity, configuration, memory, tools, files, and chat history |
| **Tool execution** | Filesystem, shell, browser, web, image, messaging, scheduling, and MCP tools |
| **Visual workflows** | Drag-and-drop orchestration with branches, loops, parallel execution, forms, agents, and sub-workflows |
| **Knowledge workspace** | Documents, Markdown notes, scoped chat, PDF chat, knowledge graph, and AI distillation |
| **Subagents** | Specialized agents with independent prompts, tools, workspaces, and memory |
| **Reliability controls** | Model routing, retries and fallback, context compression, verification loops, and action hooks |
| **Observability** | Streaming execution, tool-call visibility, run traces, token usage, cost analysis, and budget alerts |
| **Extensibility** | Markdown Skills, plugins, workers, MCP servers, and built-in extensions |
| **Multi-channel access** | Desktop, WeChat, Feishu/Lark, DingTalk, Slack, Discord, Telegram, email, and webhooks |

## Core workflows

### Run an agent

Configure a provider, model, tools, and iteration limits in the UI. Cortex streams responses and tool calls, isolates project data in workspaces, and records token usage, cost, observations, and long-term memory.

### Build a visual workflow

The ReactFlow-based editor includes 16 registered node types for:

- Flow control
- LLM calls and content extraction
- HTTP, code, file, JSON, and text tools
- Conditions, variables, loops, and parallel execution
- User selection and form input
- Agent nodes and sub-workflows

Workflows support node testing, version management, auto-save, execution traces, and variable inspection.

### Work with knowledge

- Upload and preview PDF, DOCX, XLSX, PPTX, images, and Markdown.
- Distill documents into reusable knowledge.
- Organize Markdown notes in vaults and import Obsidian vaults.
- Chat with a selected note path, vault, or PDF.
- Explore relationships through the knowledge graph and PDF mind maps.

### Extend Cortex

- Add a Markdown-based `SKILL.md` to teach an agent a reusable method.
- Connect external tools through MCP over stdio or HTTP SSE.
- Install Skill, Plugin, or Worker extensions.
- Bind tools and extensions to individual subagents.

## Reliability and safety

Cortex includes runtime controls for long-running and tool-using agents:

- Task-aware model routing with cost budgets and circuit breaking
- Recovery chain: retry → fallback model → context compression → user notification
- Verification loops with feedback injection
- Action hooks for dangerous commands, file safety, and token budgets
- Persistent scheduled tasks and long-running task state
- Execution logs for agents, subagents, workflows, and knowledge distillation

These controls reduce avoidable failures, but do not make arbitrary tool execution risk-free. Review permissions before using Cortex with sensitive data or systems.

## Quick start

### Requirements

- Node.js 18+
- Python 3.10+
- npm
- At least one supported model provider API key

### Install and run

```bash
git clone https://github.com/imnotyz/Cortex.git
cd Cortex

npm install
pip install -r backend/requirements.txt

npm run dev
```

`npm run dev` starts the Vite frontend and Electron application. Electron manages the local Python backend lifecycle.

After launch, configure a provider from **Settings → Model Providers**.

## Development commands

| Command | Description |
| --- | --- |
| `npm run dev` | Run the frontend and Electron in development mode |
| `npm run dev:frontend` | Run the Vite frontend only |
| `npm run dev:electron` | Run Electron against the frontend development server |
| `npm run build:frontend` | Build the React frontend |
| `npm run build:python` | Package the Python backend |
| `npm run build` | Build the frontend and Electron application |
| `npm run dist` | Package the current platform |
| `npm run dist:mac` | Build macOS DMG and ZIP packages |
| `npm run dist:win` | Build Windows installer and portable packages |

See [README_BUILD.md](./README_BUILD.md) for packaging details.

## Architecture

```text
┌──────────────────────────────────────────────────────────┐
│                    Electron Desktop                      │
│  React UI ── WebSocket / IPC ── FastAPI Agent Runtime   │
└───────────────────────────────┬──────────────────────────┘
                                │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
  Agent runtime           Workflow engine        Knowledge services
  tools / memory          nodes / traces          docs / notes / graph
        │                       │                        │
        └──────────── SQLite + local workspace ──────────┘
                                │
          Providers · MCP servers · external channels
```

### Technology stack

| Layer | Technologies |
| --- | --- |
| Desktop | Electron 28, electron-builder |
| Frontend | React 18, Vite 5, Ant Design, ReactFlow, Monaco Editor, ECharts, PixiJS |
| Backend | Python 3.10+, FastAPI, WebSocket, SQLAlchemy, SQLite |
| Agent runtime | Tool loop, subagents, memory, compression, routing, recovery, verification |
| Automation | Playwright, APScheduler, MCP |
| Quality | CI, pre-commit hooks, benchmarks, and 310 unit tests |

## Repository structure

```text
Cortex/
├── backend/
│   ├── agent/          # Agent loop, processors, subagents, memory
│   ├── channels/       # Desktop and external messaging channels
│   ├── core/           # Events, providers, configuration, long tasks
│   ├── data/           # SQLite schemas and migrations
│   ├── extensions/     # Extension loading and built-ins
│   ├── mcp/            # MCP connections and tool registry
│   ├── services/       # Knowledge, workflow, cron, TTS, image, LLM
│   └── tools/          # Files, shell, browser, memory, knowledge, actions
├── frontend/           # React desktop interface
├── electron/           # Electron main and preload processes
├── tests/              # Unit tests
├── benchmarks/         # Performance benchmarks
├── build/              # Packaging resources
├── docker-compose.yml
├── Dockerfile
└── README_BUILD.md
```

Runtime user data is written to `workspace/` and excluded from version control.

## Documentation

- [Build and release guide](./README_BUILD.md)
- [Optimization report](./OPTIMIZATION_REPORT.md)
- [Agent workspace guide](./agents/system/AGENTS.md)
- [MCP integration](./backend/mcp/README.md)
- [Browser tools](./backend/tools/browser/README.md)

## Current status

Version **1.1.0** currently includes:

- Visual agent and subagent management
- Visual workflow orchestration
- Local knowledge workspace and scoped knowledge chat
- Observation and long-term memory management
- MCP and Markdown Skill extensions
- Multi-channel messaging adapters
- Scheduled and long-running tasks
- Model routing, recovery, verification, and safety hooks
- Token analytics, cost budgets, CI, benchmarks, and 310 unit tests

## Contributing

Issues and pull requests are welcome. Please keep changes focused, describe user-visible behavior, update tests for logic changes, and never commit API keys or local workspace data.

## License

Cortex is released under the [MIT License](./LICENSE.txt).

<div align="center">
  <sub>Built with ❤️ and 🧠</sub>
</div>
