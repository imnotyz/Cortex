"""Scenario template system for pre-built agent configurations."""

from backend.core.templates.scenario_templates import (
    CUSTOMER_SERVICE_TEMPLATE,
    DATA_ANALYSIS_TEMPLATE,
    ScenarioTemplate,
    TemplateParameter,
    TemplateRegistry,
    create_default_registry,
)

__all__ = [
    "CUSTOMER_SERVICE_TEMPLATE",
    "DATA_ANALYSIS_TEMPLATE",
    "ScenarioTemplate",
    "TemplateParameter",
    "TemplateRegistry",
    "create_default_registry",
]
