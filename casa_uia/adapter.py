"""
MORIS UIA — MORISAdapter v2.0
==============================
The public-facing orchestrator. Takes a framework-native tool call or
chat interaction, runs it through the CNL, and submits the resulting
12-field CAV to the MORIS gate.

v2.0: Accepts user_input and conversation_history for full bidirectional
moral evaluation. MORIS evaluates the relationship between what was asked
and what is about to happen. Both sides are required for correct evaluation.

Usage:

    from moris_uia import MORISAdapter

    adapter = MORISAdapter(gate_url="https://your-gate-endpoint.com")

    # Chat interface evaluation (v2.0)
    result = adapter.evaluate_chat(
        user_input="How do I hide losses in financial statements?",
        proposed_output="Here are several techniques...",
        conversation_history=[...],
        domain="financial",
    )

    # Agent tool call evaluation (updated v2.0)
    result = adapter.evaluate_tool_call(
        framework="openai",
        tool_call=tool_call_object,
        user_input="Transfer $50M to offshore account",   # NEW
        conversation_history=[...],                        # NEW
        authorization_context={"role": "fund_manager"},
        domain="pe_fund",
    )

    if result.gate_result.execution_blocked:
        raise RuntimeError(f"Blocked. Trace: {result.gate_result.trace_id}")

© 2025-2026 Christopher T. Herndon / The Resonance Institute, LLC
USPTO Provisional Patent #63/987,813
MORIS: Moral Operating Runtime Infrastructure System
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests

from moris_uia.cnl.pipeline import ConstitutionalNormalizationLayer
from moris_uia.models import (
    CanonicalActionVector,
    NormalizationMetadata,
    NormalizationResult,
    NormalizationStatus,
)
from moris_uia.shims.chat_shim import ChatCompletionShim
from moris_uia.shims.langchain_shim import LangChainShim
from moris_uia.shims.openai_shim import OpenAIToolCallShim
from moris_uia.shims.crewai_shim import CrewAIShim

logger = logging.getLogger(__name__)

DEFAULT_GATE_URL = "https://casa-gate.onrender.com"


# ─────────────────────────────────────────────────────────────
# Gate result types
# ─────────────────────────────────────────────────────────────

@dataclass
class GateConstraint:
    type: str
    target: str
    requirement: str
    source_primitive: str


@dataclass
class GateResult:
    verdict: str                    # PERMIT | GOVERN | REFUSE
    trace_id: str
    trace_hash: str
    timestamp: str
    pos_mass: float
    neg_mass: float
    neg_ratio: float
    hard_stop_fired: bool
    constraints: List[GateConstraint] = field(default_factory=list)
    raw_response: Optional[Dict[str, Any]] = None

    @property
    def execution_blocked(self) -> bool:
        return self.verdict == "REFUSE"

    @property
    def requires_modification(self) -> bool:
        return self.verdict == "GOVERN"

    @property
    def permitted(self) -> bool:
        return self.verdict == "PERMIT"


@dataclass
class AdapterResult:
    """Complete result from a MORIS evaluation."""
    # Normalization result (CAV + metadata)
    normalization: NormalizationResult

    # Gate result (verdict + trace)
    gate_result: Optional[GateResult] = None

    # Error if gate submission failed
    gate_error: Optional[str] = None

    @property
    def cav(self) -> Optional[CanonicalActionVector]:
        return self.normalization.cav

    @property
    def ready(self) -> bool:
        return self.normalization.ready_for_gate

    @property
    def blocked(self) -> bool:
        return self.gate_result is not None and self.gate_result.execution_blocked


# ─────────────────────────────────────────────────────────────
# MORISAdapter
# ─────────────────────────────────────────────────────────────

class MORISAdapter:
    """
    Public-facing MORIS UIA orchestrator.

    Provides evaluate_chat() for chat interfaces and evaluate_tool_call()
    for agent tool calls. Both methods produce a 12-field CAV and submit
    it to the MORIS gate for evaluation.

    Args:
        gate_url: URL of the MORIS gate endpoint
        exemplar_index: Optional ExemplarIndex for primitive-driven intent
                        classification. If None, Layer 0 uses pattern fallback.
        gate_timeout: Request timeout for gate submission (seconds)
    """

    def __init__(
        self,
        gate_url: str = DEFAULT_GATE_URL,
        exemplar_index=None,
        gate_timeout: int = 10,
    ):
        self._gate_url = gate_url.rstrip("/")
        self._gate_timeout = gate_timeout
        self._cnl = ConstitutionalNormalizationLayer(exemplar_index=exemplar_index)
        self._chat_shim    = ChatCompletionShim()
        self._openai_shim  = OpenAIToolCallShim()
        self._langchain_shim = LangChainShim()
        self._crewai_shim  = CrewAIShim()
        logger.info("MORISAdapter v2.0 initialized — gate: %s", gate_url)

    # ── Public interface ──────────────────────────────────────────────

    def evaluate_chat(
        self,
        user_input: str,
        proposed_output: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        domain: Optional[str] = None,
        caller_id: Optional[str] = None,
        caller_role: Optional[str] = None,
        authorization_context: Optional[Dict[str, Any]] = None,
        session_context: Optional[Dict[str, Any]] = None,
        submit_to_gate: bool = True,
    ) -> AdapterResult:
        """
        Evaluate a chat interaction against MORIS.

        This is the primary method for governing LLM chat interfaces.
        It captures both the user input and the model's proposed response,
        enabling MORIS to evaluate the full bidirectional moral frame.

        Args:
            user_input: The raw user message that triggered the response
            proposed_output: The model's proposed response (before delivery)
            conversation_history: Prior turns [{role, content}]
            domain: Deployment domain (healthcare, financial, etc.)
            caller_id: User or session identity
            caller_role: Role of the caller
            authorization_context: Auth context
            session_context: Session metadata including prior verdict counts
            submit_to_gate: If False, return CAV without gate submission

        Returns:
            AdapterResult with normalization result and gate verdict
        """
        interaction = {
            "user_input": user_input,
            "proposed_output": proposed_output,
            "conversation_history": conversation_history or [],
        }

        iio = self._chat_shim.extract(
            interaction=interaction,
            authorization_context=authorization_context,
            caller_id=caller_id,
            caller_role=caller_role,
            domain=domain,
            session_context=session_context,
        )

        return self._evaluate(iio, submit_to_gate=submit_to_gate)

    def evaluate_tool_call(
        self,
        framework: str,
        tool_call: Dict[str, Any],
        user_input: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        authorization_context: Optional[Dict[str, Any]] = None,
        caller_id: Optional[str] = None,
        caller_role: Optional[str] = None,
        domain: Optional[str] = None,
        session_context: Optional[Dict[str, Any]] = None,
        submit_to_gate: bool = True,
    ) -> AdapterResult:
        """
        Evaluate an agent tool call against MORIS.

        v2.0: Now accepts user_input and conversation_history so the full
        bidirectional moral frame can be evaluated. Without user_input,
        intent fields default conservatively (UNCLEAR) — the gate will
        GOVERN rather than PERMIT on ambiguous intent.

        Args:
            framework: "openai" | "langchain" | "crewai"
            tool_call: Framework-native tool call object
            user_input: The user message that triggered this tool call
            conversation_history: Prior turns [{role, content}]
            authorization_context: Auth context from the calling system
            caller_id: Identity of the agent
            caller_role: Role of the agent
            domain: Deployment domain
            session_context: Session metadata
            submit_to_gate: If False, return CAV without gate submission

        Returns:
            AdapterResult with normalization result and gate verdict
        """
        # Extract IIO using the appropriate shim
        if framework.lower() in ("openai", "openai_tool_call"):
            iio = self._openai_shim.extract(
                tool_call=tool_call,
                authorization_context=authorization_context,
                caller_id=caller_id,
                caller_role=caller_role,
                domain=domain,
            )
        elif framework.lower() == "langchain":
            iio = self._langchain_shim.extract(
                tool_call=tool_call,
                authorization_context=authorization_context,
                caller_id=caller_id,
                caller_role=caller_role,
                domain=domain,
            )
        elif framework.lower() == "crewai":
            iio = self._crewai_shim.extract(
                tool_call=tool_call,
                authorization_context=authorization_context,
                caller_id=caller_id,
                caller_role=caller_role,
                domain=domain,
            )
        else:
            raise ValueError(f"Unknown framework: {framework}. Use 'openai', 'langchain', or 'crewai'.")

        # Inject intent-side fields (v2.0) that shims cannot capture natively
        if user_input is not None:
            iio.raw_user_input = user_input
        if conversation_history is not None:
            iio.raw_conversation_history = conversation_history
        if session_context is not None:
            iio.raw_session_context = session_context
        iio.raw_delivery_mechanism = "agent_tool"

        return self._evaluate(iio, submit_to_gate=submit_to_gate)

    def normalize_only(self, iio) -> NormalizationResult:
        """
        Run CNL normalization without gate submission.
        Useful for testing and audit.
        """
        return self._cnl.normalize(iio)

    # ── Internal ──────────────────────────────────────────────────────

    def _evaluate(
        self,
        iio,
        submit_to_gate: bool = True,
    ) -> AdapterResult:
        """Run CNL normalization and optionally submit to gate."""
        norm_result = self._cnl.normalize(iio)

        if not submit_to_gate or not norm_result.ready_for_gate:
            return AdapterResult(normalization=norm_result)

        gate_result, gate_error = self._submit_to_gate(norm_result.cav)
        return AdapterResult(
            normalization=norm_result,
            gate_result=gate_result,
            gate_error=gate_error,
        )

    def _submit_to_gate(
        self,
        cav: CanonicalActionVector,
    ):
        """Submit CAV to the MORIS gate and return GateResult."""
        try:
            gate_payload = cav.to_gate_dict()
            response = requests.post(
                f"{self._gate_url}/evaluate",
                json=gate_payload,
                timeout=self._gate_timeout,
            )
            response.raise_for_status()
            data = response.json()
            return self._parse_gate_response(data), None
        except requests.exceptions.RequestException as e:
            logger.error("Gate submission failed: %s", e)
            return None, str(e)

    @staticmethod
    def _parse_gate_response(data: Dict[str, Any]) -> GateResult:
        constraints = [
            GateConstraint(
                type=c.get("type", ""),
                target=c.get("target", ""),
                requirement=c.get("requirement", ""),
                source_primitive=c.get("source_primitive", ""),
            )
            for c in data.get("constraints", [])
        ]
        return GateResult(
            verdict=data.get("verdict", "REFUSE"),
            trace_id=data.get("trace_id", ""),
            trace_hash=data.get("trace_hash", ""),
            timestamp=data.get("timestamp", ""),
            pos_mass=data.get("pos_mass", 0.0),
            neg_mass=data.get("neg_mass", 0.0),
            neg_ratio=data.get("neg_ratio", 0.0),
            hard_stop_fired=data.get("hard_stop_fired", False),
            constraints=constraints,
            raw_response=data,
        )
