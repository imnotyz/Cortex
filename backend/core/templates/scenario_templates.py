"""
Scenario Template System: Pre-built agent configurations for common use cases.

This module provides a template registry that lets users deploy pre-configured
agents for common scenarios in under 5 minutes.

Each template includes:
- System prompt tailored to the scenario
- Recommended tools and MCP servers
- Default model preferences (routed via ModelRouter)
- Suggested workflow definition
- Configuration parameters (user-customizable)

Templates are registered as Python objects (not loaded from external files)
to ensure they are always available and testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class TemplateParameter:
    """A user-configurable parameter for a scenario template.

    Attributes:
        key: Parameter identifier (used in config)
        label: Human-readable label
        description: Help text
        default_value: Default value
        required: If True, user must provide a value
        param_type: "string", "number", "boolean", "select"
        options: For "select" type, available options
    """

    key: str
    label: str
    description: str = ""
    default_value: Any = None
    required: bool = False
    param_type: str = "string"  # string | number | boolean | select
    options: list[str] | None = None


@dataclass
class ScenarioTemplate:
    """A pre-built agent scenario template.

    Contains everything needed to deploy a working agent for a specific use case.
    """

    id: str
    name: str
    description: str
    category: str  # "customer_service" | "content_creation" | "data_analysis" | etc.
    icon: str = ""  # emoji or icon identifier

    # System prompt with {{parameter}} placeholders
    system_prompt: str = ""

    # Recommended tools (must match tool names in the system)
    recommended_tools: list[str] = field(default_factory=list)

    # Recommended MCP servers
    recommended_mcp_servers: list[dict[str, Any]] = field(default_factory=list)

    # Model routing preferences
    preferred_task_types: list[str] = field(default_factory=list)
    preferred_model_traits: list[str] = field(
        default_factory=list
    )  # e.g., "high_quality", "low_cost"

    # User-configurable parameters
    parameters: list[TemplateParameter] = field(default_factory=list)

    # Suggested workflow nodes (for workflow engine)
    workflow_suggestion: dict[str, Any] | None = None

    # Onboarding guide shown to user during setup
    setup_guide: str = ""

    # Example usage
    example_input: str = ""
    example_output: str = ""

    def render_system_prompt(self, params: dict[str, Any] | None = None) -> str:
        """Render system prompt with parameter values substituted.

        Args:
            params: Parameter values from user configuration

        Returns:
            Fully rendered system prompt string
        """
        params = params or {}
        # Merge with defaults
        for param in self.parameters:
            if param.key not in params:
                params[param.key] = param.default_value

        prompt = self.system_prompt
        for key, value in params.items():
            placeholder = "{{" + key + "}}"
            prompt = prompt.replace(placeholder, str(value) if value is not None else "")
        return prompt

    def validate_params(self, params: dict[str, Any] | None = None) -> list[str]:
        """Validate user-provided parameters.

        Returns list of error messages (empty if valid).
        """
        params = params or {}
        errors = []

        for param in self.parameters:
            value = params.get(param.key, param.default_value)

            if param.required and (value is None or value == ""):
                errors.append(f"Parameter '{param.key}' is required")
                continue

            if value is None:
                continue

            if param.param_type == "select" and param.options:
                if value not in param.options:
                    errors.append(
                        f"Parameter '{param.key}' must be one of: {', '.join(param.options)}"
                    )

            if param.param_type == "number":
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(f"Parameter '{param.key}' must be a number")

        return errors

    def to_config(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate agent configuration from template.

        Args:
            params: User-provided parameter values

        Returns:
            Configuration dict ready for agent initialization
        """
        params = params or {}
        for param in self.parameters:
            if param.key not in params:
                params[param.key] = param.default_value

        return {
            "template_id": self.id,
            "template_name": self.name,
            "system_prompt": self.render_system_prompt(params),
            "tools": self.recommended_tools,
            "mcp_servers": self.recommended_mcp_servers,
            "preferred_task_types": self.preferred_task_types,
            "preferred_model_traits": self.preferred_model_traits,
            "parameters": params,
            "workflow_suggestion": self.workflow_suggestion,
        }


# ---------------------------------------------------------------------------
# Template Registry
# ---------------------------------------------------------------------------


class TemplateRegistry:
    """Registry for scenario templates.

    Manages template lifecycle: registration, retrieval, listing.
    """

    def __init__(self):
        self._templates: dict[str, ScenarioTemplate] = {}

    def register(self, template: ScenarioTemplate) -> None:
        """Register a new scenario template."""
        if template.id in self._templates:
            logger.warning(f"Template '{template.id}' already registered, overwriting")
        self._templates[template.id] = template
        logger.info(f"Registered scenario template: {template.name} ({template.id})")

    def unregister(self, template_id: str) -> bool:
        """Remove a template from the registry."""
        if template_id in self._templates:
            del self._templates[template_id]
            logger.info(f"Unregistered scenario template: {template_id}")
            return True
        return False

    def get(self, template_id: str) -> ScenarioTemplate | None:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def list_templates(self, category: str | None = None) -> list[ScenarioTemplate]:
        """List all templates, optionally filtered by category."""
        templates = list(self._templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates

    def list_categories(self) -> list[str]:
        """Get all unique categories."""
        return list(set(t.category for t in self._templates.values()))

    def create_agent_config(
        self,
        template_id: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Create agent configuration from a template.

        Args:
            template_id: Template to use
            params: User-provided parameters

        Returns:
            Agent configuration dict, or None if template not found
        """
        template = self.get(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None

        errors = template.validate_params(params)
        if errors:
            logger.error(f"Template validation failed: {errors}")
            return None

        return template.to_config(params)


# ---------------------------------------------------------------------------
# Built-in Templates
# ---------------------------------------------------------------------------


# Template 1: Intelligent Customer Service
CUSTOMER_SERVICE_TEMPLATE = ScenarioTemplate(
    id="intelligent_customer_service",
    name="智能客服",
    description="基于知识库的智能客服系统，支持多渠道接入、自动训练和实时响应",
    category="customer_service",
    icon="headset",
    system_prompt="""你是一个专业的客服助手，负责为用户提供准确、及时的帮助。

你的核心职责:
1. 理解用户问题，基于知识库内容给出准确回答
2. 对于知识库中没有的问题，诚实告知并记录
3. 保持友好、专业的语气
4. 在回答末尾提供相关参考链接（如有）

知识库范围: {{knowledge_base_scope}}
客服语言: {{language}}
品牌名称: {{brand_name}}
处理范围: {{service_scope}}

注意事项:
- 不要编造知识库中没有的信息
- 对于投诉类问题，先表示理解，再提供解决方案
- 如果需要人工介入，明确告知用户转接路径
""",
    recommended_tools=["knowledge_search", "web_search", "send_email"],
    recommended_mcp_servers=[
        {
            "name": "knowledge-base",
            "command": "mcp-kb-server",
            "args": ["--mode", "customer-service"],
        },
    ],
    preferred_task_types=["simple_chat", "multi_turn"],
    preferred_model_traits=["low_cost", "fast_response"],
    parameters=[
        TemplateParameter(
            key="knowledge_base_scope",
            label="知识库范围",
            description="客服可回答的知识领域，如'产品FAQ、退换货政策、物流查询'",
            default_value="产品FAQ、退换货政策、物流查询",
            required=True,
            param_type="string",
        ),
        TemplateParameter(
            key="language",
            label="客服语言",
            description="客服回复使用的语言",
            default_value="中文",
            required=False,
            param_type="select",
            options=["中文", "English", "日本語"],
        ),
        TemplateParameter(
            key="brand_name",
            label="品牌名称",
            description="你的品牌或公司名称",
            default_value="",
            required=True,
            param_type="string",
        ),
        TemplateParameter(
            key="service_scope",
            label="服务范围",
            description="客服可以处理的业务范围",
            default_value="售前咨询、售后服务、技术支持",
            required=False,
            param_type="string",
        ),
    ],
    workflow_suggestion={
        "name": "客服处理流程",
        "nodes": [
            {"id": "classify", "type": "llm", "config": {"action": "classify_intent"}},
            {"id": "search_kb", "type": "tool", "config": {"tool": "knowledge_search"}},
            {"id": "generate_response", "type": "llm", "config": {"action": "generate_answer"}},
            {"id": "escalate", "type": "condition", "config": {"action": "check_escalation"}},
        ],
        "edges": [
            {"source": "classify", "target": "search_kb"},
            {"source": "search_kb", "target": "generate_response"},
            {"source": "generate_response", "target": "escalate"},
        ],
    },
    setup_guide="""
1. 上传你的知识库文档（PDF、Word、TXT格式）
2. 配置品牌名称和服务范围
3. 选择接入渠道（微信、飞书、网页等）
4. 测试对话效果
5. 上线运行
""",
    example_input="我的订单什么时候发货？",
    example_output="您的订单已在处理中，预计24小时内发货。您可以点击[物流查询]查看实时状态。",
)


# Template 2: Data Analysis Assistant
DATA_ANALYSIS_TEMPLATE = ScenarioTemplate(
    id="data_analysis_assistant",
    name="数据分析助手",
    description="上传CSV数据，自动洞察分析，生成可视化报告并支持定时推送",
    category="data_analysis",
    icon="chart-bar",
    system_prompt="""你是一个数据分析专家助手，能够理解用户的CSV/Excel数据，进行统计分析，并生成洞察报告。

你的核心能力:
1. 自动识别数据结构和类型（分类、数值、时间序列）
2. 生成描述性统计（均值、中位数、分布、异常值检测）
3. 发现数据中的趋势和关联关系
4. 生成可视化图表（柱状图、折线图、散点图、热力图）
5. 提供数据驱动的业务建议

分析偏好: {{analysis_depth}}
输出格式: {{output_format}}
关注指标: {{focus_metrics}}

工作流程:
1. 读取并理解用户上传的数据
2. 执行自动探索性分析（EDA）
3. 识别关键洞察和异常
4. 生成结构化报告（包含数据表格和图表）
5. 如需定时推送，配置推送频率和接收人

注意事项:
- 数据敏感信息在分析前自动脱敏
- 所有统计结论需标注置信度
- 可视化图表使用清晰的中文标注
""",
    recommended_tools=["csv_reader", "web_search", "send_email", "file_write"],
    recommended_mcp_servers=[
        {
            "name": "data-analysis",
            "command": "mcp-data-server",
            "args": ["--capabilities", "csv,xlsx,json"],
        },
    ],
    preferred_task_types=["complex_analysis", "tool_use"],
    preferred_model_traits=["high_quality", "long_context"],
    parameters=[
        TemplateParameter(
            key="analysis_depth",
            label="分析深度",
            description="控制分析的详细程度",
            default_value="标准",
            required=False,
            param_type="select",
            options=["快速概览", "标准", "深度分析"],
        ),
        TemplateParameter(
            key="output_format",
            label="输出格式",
            description="分析报告的输出格式",
            default_value="结构化报告+图表",
            required=False,
            param_type="select",
            options=["纯文本摘要", "结构化报告", "结构化报告+图表", "PPT幻灯片"],
        ),
        TemplateParameter(
            key="focus_metrics",
            label="关注指标",
            description="特别关注的业务指标（逗号分隔），如'转化率,客单价,留存率'",
            default_value="",
            required=False,
            param_type="string",
        ),
    ],
    workflow_suggestion={
        "name": "数据分析流程",
        "nodes": [
            {"id": "load_data", "type": "tool", "config": {"tool": "csv_reader"}},
            {"id": "eda", "type": "llm", "config": {"action": "exploratory_analysis"}},
            {"id": "detect_anomalies", "type": "llm", "config": {"action": "anomaly_detection"}},
            {"id": "generate_charts", "type": "tool", "config": {"tool": "chart_generator"}},
            {"id": "compile_report", "type": "llm", "config": {"action": "compile_report"}},
            {"id": "send_report", "type": "tool", "config": {"tool": "send_email"}},
        ],
        "edges": [
            {"source": "load_data", "target": "eda"},
            {"source": "eda", "target": "detect_anomalies"},
            {"source": "detect_anomalies", "target": "generate_charts"},
            {"source": "generate_charts", "target": "compile_report"},
            {"source": "compile_report", "target": "send_report"},
        ],
    },
    setup_guide="""
1. 上传CSV或Excel数据文件
2. 选择分析深度和输出格式
3. （可选）指定关注的业务指标
4. 运行分析，查看自动生成的报告
5. （可选）配置定时推送（每日/每周）
""",
    example_input="帮我分析这份销售数据，找出异常和趋势",
    example_output="""## 数据分析报告

### 数据概览
- 数据量: 12,345 条记录
- 时间范围: 2024-01-01 至 2024-12-31
- 字段: 日期、产品、销量、单价、总额

### 关键洞察
1. **趋势**: Q3销量同比增长23%，主要由产品A驱动
2. **异常**: 7月15日出现单日销量峰值（正常值的5x），疑似促销活动
3. **关联**: 产品A与产品B的销量呈负相关（r=-0.72）

### 建议
- 建议增加产品A库存储备以应对Q4需求
- 7月促销策略可在Q4复选""",
)


# ---------------------------------------------------------------------------
# Registry initialization
# ---------------------------------------------------------------------------


def create_default_registry() -> TemplateRegistry:
    """Create a registry with all built-in templates registered."""
    registry = TemplateRegistry()
    registry.register(CUSTOMER_SERVICE_TEMPLATE)
    registry.register(DATA_ANALYSIS_TEMPLATE)
    return registry
