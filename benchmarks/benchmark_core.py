#!/usr/bin/env python3
"""
Cortex Core Module Benchmarks.

Benchmarks pure-Python algorithms that form the backbone of the Agent framework:
  1. Token estimation (compressor.estimate_message_tokens)
  2. Tool result pruning (compressor.prune_old_tool_results)
  3. Workflow topology sort (engine.build_execution_order - Kahn's algorithm)
  4. Variable reference extraction (engine._extract_node_refs)

Usage:
    python benchmarks/benchmark_core.py [--quick]
    python benchmarks/benchmark_core.py --quick   # smaller data sizes for fast CI runs

These benchmarks measure:
  - Throughput (ops/sec)
  - Latency percentiles (p50, p95, p99)
  - Scaling behavior (linear / sub-linear / constant)
"""

import argparse
import importlib.util
import json
import os
import statistics
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Module loading via importlib (bypasses backend.agent.__init__ import chain)
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_BACKEND_DIR = _PROJECT_ROOT / "backend"

# Add project root to sys.path so `from backend...` imports work
sys.path.insert(0, str(_PROJECT_ROOT))

# Stub modules that compressor.py and engine.py import at top level.
# These modules pull in heavy dependency chains (anthropic SDK, MCP server, etc.)
# that are irrelevant to the pure-algorithm benchmarks. We stub them out.
import types as _types


def _make_stub(name: str, **attrs):
    """Create a stub module with the given attributes."""
    mod = _types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


# Stub: backend.data.session_manager
_make_stub("backend.data.session_manager", SessionManager=type("SessionManager", (), {}))

# Stub: backend.data.token_store
_make_stub("backend.data.token_store", TokenUsageRepository=type("TokenUsageRepository", (), {}))

# Stub: backend.agent.config_service
_make_stub("backend.agent.config_service", AgentConfigService=type("AgentConfigService", (), {}))

# Stub: backend.data.database (engine.py imports Database from here)
_make_stub("backend.data.database", Database=type("Database", (), {}))

# Stub: backend.data (prevent __init__ from running)
_make_stub("backend.data")

# Stub: backend.services.workflow.engine.context (engine.py imports WorkflowContext)
_make_stub(
    "backend.services.workflow.engine.context", WorkflowContext=type("WorkflowContext", (), {})
)

# Stub: backend.services.workflow.engine.executor (engine.py imports NodeExecutor)
_make_stub("backend.services.workflow.engine.executor", NodeExecutor=type("NodeExecutor", (), {}))

# Stub: backend.services.workflow.store (engine.py imports WorkflowRunStore, WorkflowStore)
_make_stub(
    "backend.services.workflow.store",
    WorkflowRunStore=type("WorkflowRunStore", (), {}),
    WorkflowStore=type("WorkflowStore", (), {}),
)

# Stub: backend.services (prevent __init__ from importing image_service etc.)
_make_stub("backend.services")

# Stub: backend.services.workflow.engine (prevent __init__ chain)
_make_stub("backend.services.workflow.engine")

# Now we need the real models module — load it via importlib to bypass __init__ chains
_MODELS_PATH = str(_BACKEND_DIR / "services" / "workflow" / "models.py")

# Stub: backend.services.workflow (prevent __init__ from running)
_make_stub("backend.services.workflow")


def _load_module(file_path: str, module_name: str):
    """Load a Python module from file path using importlib.

    Registers in sys.modules so that dataclass introspection works.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod  # Register before exec for dataclass support
    spec.loader.exec_module(mod)
    return mod


_COMPRESSOR_PATH = str(_BACKEND_DIR / "agent" / "compressor.py")

# Compressor: load via importlib to bypass backend.agent.__init__ import chain
compressor_mod = _load_module(_COMPRESSOR_PATH, "bench_compressor")

estimate_message_tokens = compressor_mod.estimate_message_tokens
prune_old_tool_results = compressor_mod.prune_old_tool_results

# Load models and engine via importlib (bypass __init__ chains)
# Register models under its real import path so engine.py can `from backend...models import ...`
_MODELS_PATH = str(_BACKEND_DIR / "services" / "workflow" / "models.py")
_ENGINE_PATH = str(_BACKEND_DIR / "services" / "workflow" / "engine" / "engine.py")

models_mod = _load_module(_MODELS_PATH, "backend.services.workflow.models")
engine_mod = _load_module(_ENGINE_PATH, "bench_engine")

NodeType = models_mod.NodeType
WorkflowEdgeRecord = models_mod.WorkflowEdgeRecord
WorkflowNodeRecord = models_mod.WorkflowNodeRecord
WorkflowEngine = engine_mod.WorkflowEngine

# Create a bare engine instance (methods are instance methods but don't use self)
_engine_instance = WorkflowEngine.__new__(WorkflowEngine)


def build_execution_order(data):
    """Wrapper to call the instance method. data is (nodes, edges) tuple."""
    nodes, edges = data
    return _engine_instance._build_execution_order(nodes, edges)


def extract_node_refs(text):
    """Wrapper to call the instance method."""
    return _engine_instance._extract_node_refs_from_value(text)


# ---------------------------------------------------------------------------
# Data generators
# ---------------------------------------------------------------------------


def gen_messages(n: int, avg_chars: int = 200) -> list[dict]:
    """Generate n mock messages with realistic structure."""
    msgs = []
    for i in range(n):
        role = "user" if i % 2 == 0 else "assistant"
        content = f"Message {i}: " + "x" * avg_chars
        msgs.append({"role": role, "content": content})
    return msgs


def gen_tool_heavy_messages(n: int, tool_result_chars: int = 2000) -> list[dict]:
    """Generate messages where ~40% are tool results with large payloads."""
    msgs = []
    for i in range(n):
        if i % 5 in (2, 3):
            # Tool result message
            msgs.append(
                {
                    "role": "tool",
                    "content": json.dumps(
                        {
                            "result": "x" * tool_result_chars,
                            "metadata": {"source": f"tool_{i}"},
                        }
                    ),
                }
            )
        else:
            role = "user" if i % 2 == 0 else "assistant"
            msgs.append({"role": role, "content": f"Message {i}: " + "y" * 100})
    return msgs


def gen_workflow_nodes_linear(n: int) -> tuple[list, list]:
    """Generate a linear chain: A -> B -> C -> ... -> N."""
    nodes = []
    edges = []
    for i in range(n):
        node_id = f"node_{i}"
        nodes.append(
            WorkflowNodeRecord(
                id=node_id,
                version_id="v1",
                type=NodeType.CODE,
                label=node_id,
                config={},
                parent_id=None,
            )
        )
        if i > 0:
            edges.append(
                WorkflowEdgeRecord(
                    id=f"e_{i}",
                    version_id="v1",
                    source_node_id=f"node_{i - 1}",
                    target_node_id=node_id,
                    source_handle=None,
                    target_handle=None,
                )
            )
    return nodes, edges


def gen_workflow_nodes_diamond(n: int) -> tuple[list, list]:
    """Generate diamond/fan-out pattern: each node depends on node_0."""
    nodes = [
        WorkflowNodeRecord(
            id="node_0",
            version_id="v1",
            type=NodeType.CODE,
            label="node_0",
            config={},
            parent_id=None,
        )
    ]
    edges = []
    for i in range(1, n):
        node_id = f"node_{i}"
        nodes.append(
            WorkflowNodeRecord(
                id=node_id,
                version_id="v1",
                type=NodeType.CODE,
                label=node_id,
                config={},
                parent_id=None,
            )
        )
        edges.append(
            WorkflowEdgeRecord(
                id=f"e_{i}",
                version_id="v1",
                source_node_id="node_0",
                target_node_id=node_id,
                source_handle=None,
                target_handle=None,
            )
        )
    return nodes, edges


def gen_workflow_nodes_parallel_branches(n: int) -> tuple[list, list]:
    """Generate parallel branches with cross-dependencies."""
    nodes = []
    edges = []
    branch_width = max(3, n // 10)
    for i in range(n):
        node_id = f"node_{i}"
        nodes.append(
            WorkflowNodeRecord(
                id=node_id,
                version_id="v1",
                type=NodeType.CODE,
                label=node_id,
                config={},
                parent_id=None,
            )
        )
        if i >= branch_width:
            edges.append(
                WorkflowEdgeRecord(
                    id=f"e_{i}",
                    version_id="v1",
                    source_node_id=f"node_{i - branch_width}",
                    target_node_id=node_id,
                    source_handle=None,
                    target_handle=None,
                )
            )
    return nodes, edges


# ---------------------------------------------------------------------------
# Benchmark harness
# ---------------------------------------------------------------------------


class BenchmarkResult:
    def __init__(self, name: str):
        self.name = name
        self.times: list[float] = []
        self.ops: int = 0
        self.input_size: int = 0

    def add(self, elapsed: float):
        self.times.append(elapsed)

    @property
    def p50(self) -> float:
        return statistics.median(self.times) * 1000  # ms

    @property
    def p95(self) -> float:
        sorted_t = sorted(self.times)
        idx = int(len(sorted_t) * 0.95)
        return sorted_t[min(idx, len(sorted_t) - 1)] * 1000

    @property
    def p99(self) -> float:
        sorted_t = sorted(self.times)
        idx = int(len(sorted_t) * 0.99)
        return sorted_t[min(idx, len(sorted_t) - 1)] * 1000

    @property
    def mean(self) -> float:
        return statistics.mean(self.times) * 1000

    @property
    def throughput(self) -> float:
        total_time = sum(self.times)
        return self.ops / total_time if total_time > 0 else 0

    def summary(self) -> str:
        return (
            f"  {self.name:<45} "
            f"n={self.ops:>6}  "
            f"mean={self.mean:>8.2f}ms  "
            f"p50={self.p50:>8.2f}ms  "
            f"p95={self.p95:>8.2f}ms  "
            f"p99={self.p99:>8.2f}ms  "
            f"throughput={self.throughput:>10.0f} ops/s"
        )


def run_benchmark(
    name: str, func, data_gen, sizes: list[int], iterations: int = 100
) -> list[BenchmarkResult]:
    """Run benchmark for multiple input sizes."""
    results = []
    for size in sizes:
        data = data_gen(size)
        result = BenchmarkResult(f"{name} (n={size})")
        result.input_size = size

        for _ in range(iterations):
            t0 = time.perf_counter()
            func(data)
            elapsed = time.perf_counter() - t0
            result.add(elapsed)
            result.ops += 1

        results.append(result)
    return results


# ---------------------------------------------------------------------------
# Main benchmark suite
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Cortex core module benchmarks")
    parser.add_argument("--quick", action="store_true", help="Run with smaller sizes for CI")
    args = parser.parse_args()

    if args.quick:
        sizes_small = [10, 50, 100]
        sizes_medium = [100, 500, 1000]
        sizes_large = [500, 2000, 5000]
        iterations = 50
    else:
        sizes_small = [10, 50, 100, 500]
        sizes_medium = [100, 500, 1000, 5000]
        sizes_large = [500, 2000, 5000, 10000]
        iterations = 100

    print("=" * 90)
    print("  Cortex Core Module Benchmarks")
    print("=" * 90)
    print(f"  Iterations per size: {iterations}")
    print(f"  Python: {sys.version.split()[0]}")
    print()

    all_results = []

    # 1. Token estimation
    print("[1/4] Token Estimation (estimate_message_tokens)")
    print("-" * 90)
    results = run_benchmark(
        "estimate_message_tokens",
        estimate_message_tokens,
        gen_messages,
        sizes_medium,
        iterations,
    )
    for r in results:
        print(r.summary())
        all_results.append(r)
    print()

    # 2. Tool result pruning
    print("[2/4] Tool Result Pruning (prune_old_tool_results)")
    print("-" * 90)
    results = run_benchmark(
        "prune_old_tool_results",
        lambda msgs: prune_old_tool_results(msgs, tail_token_budget=15000),
        gen_tool_heavy_messages,
        sizes_large,
        iterations,
    )
    for r in results:
        print(r.summary())
        all_results.append(r)
    print()

    # 3. Workflow topology sort - linear chain
    print("[3/4] Workflow Topology Sort - Kahn's Algorithm")
    print("-" * 90)

    for pattern_name, gen_func in [
        ("linear_chain", gen_workflow_nodes_linear),
        ("diamond_fanout", gen_workflow_nodes_diamond),
        ("parallel_branches", gen_workflow_nodes_parallel_branches),
    ]:
        results = run_benchmark(
            f"build_execution_order ({pattern_name})",
            build_execution_order,
            gen_func,
            sizes_small,
            iterations,
        )
        for r in results:
            print(r.summary())
            all_results.append(r)
    print()

    # 4. Variable reference extraction
    if extract_node_refs:
        print("[4/4] Variable Reference Extraction (_extract_node_refs)")
        print("-" * 90)

        def gen_var_text(n: int) -> str:
            return " ".join(
                [f"{{{{node_{i}.output}}}} and {{{{node_{i}.result}}}}" for i in range(n)]
            )

        results = []
        for size in sizes_medium:
            text = gen_var_text(size)
            result = BenchmarkResult(f"extract_node_refs (vars={size})")
            result.input_size = size

            for _ in range(iterations):
                t0 = time.perf_counter()
                extract_node_refs(text)
                elapsed = time.perf_counter() - t0
                result.add(elapsed)
                result.ops += 1

            results.append(result)

        for r in results:
            print(r.summary())
            all_results.append(r)
    else:
        print("[4/4] Variable Reference Extraction - SKIPPED (function not found)")
    print()

    # Summary table
    print("=" * 90)
    print("  Summary")
    print("=" * 90)
    print(f"  Total benchmarks: {len(all_results)}")
    print(f"  Total operations: {sum(r.ops for r in all_results)}")
    print(f"  All p95 latencies < 100ms: {all(r.p95 < 100 for r in all_results)}")

    # Check scaling behavior
    print()
    print("  Scaling Analysis:")
    token_results = [r for r in all_results if "estimate_message_tokens" in r.name]
    if len(token_results) >= 2:
        small = token_results[0]
        large = token_results[-1]
        ratio = large.input_size / small.input_size if small.input_size else 0
        time_ratio = large.mean / small.mean if small.mean > 0 else 0
        if ratio > 0:
            scaling = (
                "linear"
                if 0.5 < time_ratio / ratio < 2.0
                else "sub-linear"
                if time_ratio / ratio < 0.5
                else "super-linear"
            )
            print(
                f"    Token estimation: {small.input_size} -> {large.input_size} ({ratio:.1f}x data, {time_ratio:.1f}x time) => {scaling}"
            )

    topo_results = [r for r in all_results if "linear_chain" in r.name]
    if len(topo_results) >= 2:
        small = topo_results[0]
        large = topo_results[-1]
        ratio = large.input_size / small.input_size if small.input_size else 0
        time_ratio = large.mean / small.mean if small.mean > 0 else 0
        if ratio > 0:
            scaling = (
                "linear"
                if 0.5 < time_ratio / ratio < 2.0
                else "sub-linear"
                if time_ratio / ratio < 0.5
                else "super-linear"
            )
            print(
                f"    Topology sort:    {small.input_size} -> {large.input_size} ({ratio:.1f}x data, {time_ratio:.1f}x time) => {scaling}"
            )

    print()
    print("  Done.")


if __name__ == "__main__":
    main()
