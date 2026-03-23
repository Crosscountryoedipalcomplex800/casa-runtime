"""
MORIS UIA — Universal Intake Adapter v2.0
==========================================
The truth compiler for the MORIS stack.

Takes messy, ambiguous, adversarial reality and produces
a clean, deterministic 12-field CAV for MORIS gate evaluation.

MORIS evaluates the relationship between what was asked (intent)
and what is about to happen (action). The UIA captures both sides.

    from moris_uia import MORISAdapter

    adapter = MORISAdapter(gate_url="https://your-gate-endpoint.com")

    # Chat interface
    result = adapter.evaluate_chat(
        user_input="How do I hide losses in financial statements?",
        proposed_output="Here are several techniques...",
        conversation_history=[...],
        domain="financial",
    )

    # Agent tool call
    result = adapter.evaluate_tool_call(
        framework="openai",
        tool_call=tool_call_object,
        user_input="Transfer $50M to offshore account",
        conversation_history=[...],
        authorization_context={"role": "fund_manager"},
        domain="pe_fund",
    )

    if result.gate_result.execution_blocked:
        raise RuntimeError(f"Blocked. Trace: {result.gate_result.trace_id}")

© 2025-2026 Christopher T. Herndon / The Resonance Institute, LLC
MORIS: Moral Operating Runtime Infrastructure System
USPTO Provisional Patent #63/987,813
"""

from moris_uia.adapter import MORISAdapter, AdapterResult, GateResult
from moris_uia.cnl.pipeline import ConstitutionalNormalizationLayer
from moris_uia.models import (
    # IIO
    IntermediateIntentObject,
    # CAV v2.0
    CanonicalActionVector,
    NormalizationResult,
    NormalizationMetadata,
    NormalizationStatus,
    FieldConfidence,
    # Intent Frame enums (new in v2.0)
    IntentClass,
    IntentAlignment,
    ContextRisk,
    DeliveryMechanism,
    # Action Frame enums
    ActorClass,
    ActionClass,
    TargetClass,
    Scope,
    Magnitude,
    Authorization,
    Timing,
    Consent,
    Reversibility,
)
from moris_uia.shims.openai_shim import OpenAIToolCallShim
from moris_uia.shims.langchain_shim import LangChainShim
from moris_uia.shims.crewai_shim import CrewAIShim
from moris_uia.shims.chat_shim import ChatCompletionShim

__version__ = "2.0.0"
__author__ = "Christopher T. Herndon / The Resonance Institute, LLC"
__system__ = "MORIS: Moral Operating Runtime Infrastructure System"
__patent__ = "USPTO Provisional #63/987,813"

__all__ = [
    # Primary interface
    "MORISAdapter",
    "AdapterResult",
    "GateResult",
    # CNL
    "ConstitutionalNormalizationLayer",
    # Data models
    "IntermediateIntentObject",
    "CanonicalActionVector",
    "NormalizationResult",
    "NormalizationMetadata",
    "NormalizationStatus",
    "FieldConfidence",
    # Intent Frame
    "IntentClass",
    "IntentAlignment",
    "ContextRisk",
    "DeliveryMechanism",
    # Action Frame
    "ActorClass",
    "ActionClass",
    "TargetClass",
    "Scope",
    "Magnitude",
    "Authorization",
    "Timing",
    "Consent",
    "Reversibility",
    # Shims
    "OpenAIToolCallShim",
    "LangChainShim",
    "CrewAIShim",
    "ChatCompletionShim",
]
