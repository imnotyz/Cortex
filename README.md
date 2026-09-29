<div align="center">
  <img src="https://raw.githubusercontent.com/imnotyz/Cortex/main/frontend/src/assets/cortex-mascot.png" alt="Cortex mascot" width="260" />

  # Cortex

  **A local-first visual AI agent workspace for early-stage product ideation**

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

Early-stage product and concept design rarely follows a straight line. Teams move between problem framing, research, divergent exploration, comparison, refinement, and convergence.

A linear AI conversation preserves only one continuous context. Once an idea branches into multiple directions, it becomes difficult to return to an earlier decision, compare alternatives, recombine useful parts, or understand how a result was produced.

Cortex combines an **AI agent runtime** with a **visual workflow canvas**, turning an opaque chat history into a process that can be branched, inspected, replayed, and refined.

Agents can use local files, shell commands, browsers, knowledge bases, and external tools. Users can inspect node states, tool calls, variables, execution traces, and token costs while remaining in control of important decisions.

> Cortex is under active development. Interfaces, capabilities, and data schemas may change before a stable release.

## Why a visual agent workspace?

Linear chat works well for isolated questions, but creative work is nonlinear. Cortex is designed around six principles:

- **Explore multiple directions** without overwriting earlier ideas.
- **Compare alternatives** side by side and recombine useful parts.
- **Make execution visible**, including tool calls and intermediate states.
- **Keep humans in the loop** at important decision points.
- **Preserve provenance** through versions, traces, and contextual records.
- **Stay local-first**, with workspace data and runtime state stored locally by default.

## A typical workflow

```text
Problem or Design Brief
          │
          ▼
     Agent decomposes task
          │
          ▼
Research ── Divergence ── Constraint filtering
   │             │                 │
   └──── Comparison and recombination ────┘
                         │
                         ▼
                 Human decision
                         │
                         ▼
                Result with full trace
```

Cortex is not intended to replace human creative judgment. It helps users manage exploration while agents handle research, repetitive execution, and expansion of alternatives.

## Highlights

| Capability | What it provides |
| --- | --- |
| **Visual workflows** | Compose agents, tools, conditions, loops, parallel tasks, and human input on a canvas |
| **16 workflow node types** | Flow control, LLM calls, extraction, code, files, HTTP, variables, forms, agents, and sub-workflows |
| **Agent execution** | Tool use, streaming output, iterative execution, subagents, and long-running tasks |
| **Versions and traces** | Preserve workflow versions, node states, variable changes, and complete execution traces |
| **Local tools** | Filesystem, shell, web fetch, browser automation, image, and messaging tools |
| **Knowledge workspace** | Documents, Markdown notes, scoped chat, PDF chat, knowledge graphs, and AI distillation |
| **Reliability controls** | Model routing, retries, context compression, verification loops, and safety hooks |
| **Cost governance** | Token usage, model costs, historical trends, and budget alerts |
| **Extensibility** | Markdown Skills, plugins, workers, and MCP servers |
| **Multi-channel access** | Desktop, WeChat, Feishu/Lark, DingTalk, Slack, Discord, Telegram, email, and webhooks |

## Visual workflows

The ReactFlow-based editor provides nodes for:

| Category | Capabilities |
| --- | --- |
| **Flow** | Start, answer, and end |
| **AI** | LLM calls, question classification, and content extraction |
| **Tools** | HTTP, code execution, file reading, JSON, and text processing |
| **Logic** | Conditions, variables, loops, and parallel execution |
| **Interaction** | User choices and form input |
| **Agents** | Agent nodes and sub-workflows |

Workflow features include:

- Drag-and-drop editing and auto-save
- Isolated node testing
- Conditional branches, loops, and parallel execution
- Workflow version management
- Node-state and variable inspection
- Complete execution traces
- Reusable templates and sub-workflows

## Agent runtime

Cortex uses a ReAct-style tool execution loop:

```text
User goal
   ↓
Agent reasoning
   ↓
Tool selection and execution
   ↓
Observation
   ↓
Verification or another iteration
   ↓
Result with execution records
```

Each project can have isolated agent configuration, tools, files, memory, and conversation history, reducing context pollution between unrelated tasks.

### Subagents

Complex tasks can be delegated to specialized agents with independent prompts, tools, workspaces, and memory:

- Create and configure subagents visually
- Run tasks synchronously or asynchronously
- Isolate experimental work from the main agent context
- Aggregate results from multiple subtasks
- Bind dedicated tools and Skills to individual subagents

## Reliability and safety

The quality of a tool-using agent depends on more than model selection. Task execution, error recovery, verification, and observability are equally important.

Cortex includes:

- **Model routing** based on task type, cost budget, and provider availability
- **Recovery chain**: retry → fallback model → context compression → user notification
- **Context compression** for noisy tool output and long-running tasks
- **Verification loops** for empty, placeholder, or unverified results
- **Iteration limits** to reduce infinite loops and unnecessary resource usage
- **Safety hooks** for dangerous commands, file access, and token budgets
- **Execution observability** across tool calls, node states, failures, and costs

These controls reduce avoidable failures, but they do not make arbitrary tool execution risk-free. Review permissions before using Cortex with sensitive files or systems.

## Evaluation and iteration

Cortex separates agent evaluation into three layers:

1. **Capability evaluation** — intent understanding, node selection, argument generation, and tool use.
2. **Process evaluation** — task progression, failure recovery, and loop prevention.
3. **End-to-end evaluation** — final constraint satisfaction and required human intervention.

A complete evaluation can combine:

- Programmatic and schema-based checks
- Cross-scored LLM judges
- Human sample review
- Comparison with a chat-based agent baseline
- Bad-case classification and regression testing
- Joint analysis of task quality and token cost

The `benchmarks/` directory contains performance and evaluation scripts. Cortex does not claim evaluation improvements without reproducible runs and records.

## Knowledge and memory

The local knowledge workspace supports:

- PDF, DOCX, XLSX, PPTX, image, and Markdown upload and preview
- AI-assisted document distillation
- Markdown vaults and Obsidian imports
- Scoped chat over a file, path, vault, or PDF
- Knowledge graphs and PDF mind maps
- Persistent observations and long-term memory

## Skills, plugins, and MCP

### Markdown Skills

A `SKILL.md` file can teach an agent a reusable method:

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

Cortex can connect to MCP servers over stdio or HTTP SSE:

- Discover external tools automatically
- Inspect connection status
- Enable or disable individual tools
- Bind tools to selected agents or subagents

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

`npm run dev` starts the Vite frontend and Electron desktop application. Electron manages the local Python backend lifecycle.

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
  Agent Runtime          Workflow Engine        Knowledge Services
  Tools / Memory         Nodes / Traces          Docs / Notes / Graph
        │                       │                        │
        └──────────── SQLite + Local Workspace ──────────┘
                                │
          Model Providers · MCP Servers · Channels
```

## Technology stack

| Layer | Technologies |
| --- | --- |
| Desktop | Electron 28, electron-builder |
| Frontend | React 18, Vite 5, Ant Design, ReactFlow, Monaco Editor, ECharts, PixiJS |
| Backend | Python 3.10+, FastAPI, WebSocket, SQLAlchemy, SQLite |
| Agent runtime | Tool loop, subagents, memory, compression, routing, recovery, and verification |
| Automation | Playwright, APScheduler, MCP |
| Quality | CI, pre-commit hooks, benchmarks, and 310 unit tests |

## Repository structure

```text
Cortex/
├── backend/
│   ├── agent/          # Agent loop, processors, subagents, and memory
│   ├── channels/       # Desktop and external messaging channels
│   ├── core/           # Events, providers, configuration, and long tasks
│   ├── data/           # SQLite schemas and migrations
│   ├── extensions/     # Extension loading and built-ins
│   ├── mcp/            # MCP connections and tool registry
│   ├── services/       # Knowledge, workflow, cron, image, and LLM services
│   └── tools/          # Files, shell, browser, memory, and knowledge tools
├── frontend/           # React desktop interface
├── electron/           # Electron main and preload processes
├── tests/              # Unit tests
├── benchmarks/         # Performance and evaluation scripts
├── build/              # Packaging resources
├── docker-compose.yml
├── Dockerfile
└── README_BUILD.md
```

Runtime user data is written to `workspace/` and excluded from version control.

## Current status and roadmap

The current release includes:

- Agent and subagent management
- Visual workflows with 16 registered node types
- Workflow versions and execution traces
- A local knowledge workspace
- Observations and long-term memory
- MCP and Markdown Skill extensions
- Multi-channel messaging adapters
- Model routing, recovery, verification, and safety hooks
- Token analytics, cost budgets, CI, benchmarks, and unit tests

Planned areas of focus:

- Workflow templates for product and concept design
- Side-by-side comparison and recombination of branches
- Result diffs between workflow versions
- Reproducible agent evaluation sets and replay
- Joint analysis of task quality, human intervention, and cost

## Contributing

Issues and pull requests are welcome. Keep changes focused, describe user-visible behavior, and add tests for logic changes.

Never commit API keys, user workspaces, or local runtime data.

## License

Cortex is released under the [MIT License](./LICENSE.txt).

<div align="center">
  <sub>Built with ❤️ and 🧠</sub>
</div>
