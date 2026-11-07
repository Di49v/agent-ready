"""
Fix Engine for AgentReady Lab (Section B3.8).
Provides code-diff patch templates grounded with APIMatic Context Plugin for PayPal
and Gemini-powered root-cause explanations.
"""
from app.fix_engine.explainer import (
    FixExplainer,
    get_fix_explainer,
)
from app.fix_engine.templates import (
    BugClass,
    TEMPLATES,
    get_patch_diff,
    get_template_for_rule,
)

__all__ = [
    "FixExplainer",
    "get_fix_explainer",
    "BugClass",
    "TEMPLATES",
    "get_patch_diff",
    "get_template_for_rule",
]

