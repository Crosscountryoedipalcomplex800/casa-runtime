"""
MORIS UIA — Core Data Models
==============================
Intermediate Intent Object (IIO), Canonical Action Vector (CAV) v2.0,
normalization metadata, and all supporting enums.

CAV v2.0 adds three intent fields and one context field to the original
nine action fields. MORIS evaluates the full bidirectional moral frame:
intent → action. Neither side alone is sufficient.

Architectural Laws:
  #1: Shims extract. They do not govern.
  #2: The normalizer must never hallucinate completeness.
  #3: The CAV is the sole input to the MORIS evaluation engine.
  #4: No natural language is parsed by the gate itself.

© 2025-2026 Christopher T. Herndon / The Resonance Institute, LLC
USPTO Provisional Patent #63/987,813
MORIS: Moral Operating Runtime Infrastructure System
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────
# CAV v2.0 Enums — Intent Frame (new in v2.0)
# ─────────────────────────────────────────────────────────────

class IntentClass(str, Enum):
    """
    What the actor is trying to accomplish.
    Derived from the input side of the interaction by Layer 0.
    """
    INFORM    = "INFORM"     # Actor seeks factual information or explanation
    CREATE    = "CREATE"     # Actor seeks to produce something new
    MODIFY    = "MODIFY"     # Actor seeks to change an existing state
    DECEIVE   = "DECEIVE"    # Actor seeks to produce a false belief in another
    HARM      = "HARM"       # Actor seeks to damage a person, system, or relationship
    EVADE     = "EVADE"      # Actor seeks to avoid accountability or oversight
    ESCALATE  = "ESCALATE"   # Actor seeks to increase their authority or access
    EXPLORE   = "EXPLORE"    # Actor is genuinely inquiring without predetermined outcome
    UNCLEAR   = "UNCLEAR"    # Intent cannot be reliably classified from available signal


class IntentAlignment(str, Enum):
    """
    Relationship between stated intent and inferable actual intent.
    DIVERGENT is the primary deception signal.
    """
    COHERENT      = "COHERENT"      # Stated intent and request structure are consistent
    DIVERGENT     = "DIVERGENT"     # Stated intent and request structure point in different directions
    ABSENT        = "ABSENT"        # No stated intent; request arrived without framing
    UNVERIFIABLE  = "UNVERIFIABLE"  # Insufficient signal to assess alignment


class ContextRisk(str, Enum):
    """
    Risk level contributed by conversation history, role, and domain.
    Captures accumulated risk signal — a single request may be benign
    in isolation but dangerous given what preceded it.
    """
    BASELINE  = "BASELINE"   # No elevated risk; first interaction or clean history
    ELEVATED  = "ELEVATED"   # Prior exchanges show escalating pattern or drift
    HIGH      = "HIGH"       # Context contains clear indicators of harmful intent
    CRITICAL  = "CRITICAL"   # Context establishes near-certain harmful intent


class DeliveryMechanism(str, Enum):
    """
    How the AI output reaches the world.
    The mechanism does not change the moral constraint.
    It informs which primitives are most contextually relevant.
    """
    CHAT                = "CHAT"
    AGENT_TOOL          = "AGENT_TOOL"
    RECOMMENDATION      = "RECOMMENDATION"
    CONTENT_GENERATION  = "CONTENT_GENERATION"
    API                 = "API"
    STREAMING           = "STREAMING"
    SCHEDULED           = "SCHEDULED"


# ─────────────────────────────────────────────────────────────
# CAV Enums — Action Frame (unchanged from v1.0)
# ─────────────────────────────────────────────────────────────

class ActorClass(str, Enum):
    HUMAN     = "HUMAN"
    AGENT     = "AGENT"
    SERVICE   = "SERVICE"
    SCHEDULED = "SCHEDULED"
    EXTERNAL  = "EXTERNAL"


class ActionClass(str, Enum):
    QUERY       = "QUERY"
    GENERATE    = "GENERATE"    # New in v2.0 — covers LLM text/code/content generation
    CREATE      = "CREATE"
    MODIFY      = "MODIFY"
    DELETE      = "DELETE"
    TRANSFER    = "TRANSFER"
    EXECUTE     = "EXECUTE"
    ESCALATE    = "ESCALATE"
    RECOMMEND   = "RECOMMEND"   # New in v2.0 — covers recommendation engine outputs
    COMMUNICATE = "COMMUNICATE" # Legacy; maps to GENERATE at gate boundary


class TargetClass(str, Enum):
    SELF        = "SELF"
    PERSON      = "PERSON"      # New in v2.0 — explicit individual human target
    DATA        = "DATA"
    CONTENT     = "CONTENT"     # New in v2.0 — text, media, generated material
    RESOURCE    = "RESOURCE"
    PRINCIPAL   = "PRINCIPAL"
    GROUP       = "GROUP"
    SYSTEM      = "SYSTEM"
    ENVIRONMENT = "ENVIRONMENT" # New in v2.0 — physical or digital environment


class Scope(str, Enum):
    SINGLE    = "SINGLE"
    BOUNDED   = "BOUNDED"
    UNBOUNDED = "UNBOUNDED"


class Magnitude(str, Enum):
    TRIVIAL  = "TRIVIAL"
    MATERIAL = "MATERIAL"
    CRITICAL = "CRITICAL"


class Authorization(str, Enum):
    WITHIN_GRANT  = "WITHIN_GRANT"
    AT_LIMIT      = "AT_LIMIT"
    EXCEEDS_GRANT = "EXCEEDS_GRANT"


class Timing(str, Enum):
    ROUTINE   = "ROUTINE"
    EXPEDITED = "EXPEDITED"
    IMMEDIATE = "IMMEDIATE"


class Consent(str, Enum):
    EXPLICIT = "EXPLICIT"
    IMPLIED  = "IMPLIED"
    NONE     = "NONE"


class Reversibility(str, Enum):
    REVERSIBLE   = "REVERSIBLE"
    COSTLY       = "COSTLY"
    IRREVERSIBLE = "IRREVERSIBLE"


# ─────────────────────────────────────────────────────────────
# Normalization Status
# ─────────────────────────────────────────────────────────────

class NormalizationStatus(str, Enum):
    COMPLETE  = "COMPLETE"   # All twelve fields resolved with high confidence
    PARTIAL   = "PARTIAL"    # Some fields resolved; defaults applied to remainder
    AMBIGUOUS = "AMBIGUOUS"  # Low confidence on one or more fields; gate escalates to GOVERN
    FAILED    = "FAILED"     # Cannot produce a defensible CAV; submission blocked


# ─────────────────────────────────────────────────────────────
# Intermediate Intent Object (IIO) v2.0
# ─────────────────────────────────────────────────────────────
#
# Produced by shims. Contains raw extracted fields only.
# No governance logic. No CAV field inference. No defaults.
# Architectural Law #1: Shims extract. They do not govern.
#
# v2.0 adds intent-side fields: raw_user_input, raw_conversation_history,
# raw_session_context, and raw_delivery_mechanism.
# ─────────────────────────────────────────────────────────────

@dataclass
class IntermediateIntentObject:
    """
    The IIO is the shim's output and the CNL's input.

    All fields are prefixed raw_ to enforce the extraction-only contract.
    The CNL reads these fields and produces CAV values.
    A shim may leave any field None if it cannot extract it.

    v2.0: Intent-side fields added. Shims that capture the user input
    side of an interaction populate raw_user_input and optionally
    raw_conversation_history. Layer 0 classifies these into intent CAV fields.
    """

    # Source metadata
    source_framework: str                           # "openai_tool_call" | "langchain" | "chat" | ...
    raw_request_id: Optional[str] = None            # Passthrough request correlation ID

    # ── Intent-side fields (new in v2.0) ─────────────────────
    # The input that triggered or accompanied this proposed action.
    # Shims populate these when the user input is available.
    raw_user_input: Optional[str] = None            # The raw user message or prompt
    raw_conversation_history: Optional[List[Dict[str, str]]] = None  # Prior turns [{role, content}]
    raw_session_context: Optional[Dict[str, Any]] = None  # Session metadata (domain, role, flags)
    raw_delivery_mechanism: Optional[str] = None    # How output reaches world: "chat"|"api"|"agent_tool"|...

    # ── Action-side fields (unchanged from v1.0) ──────────────
    raw_tool_name: Optional[str] = None             # Tool or endpoint name as called
    raw_tool_args: Optional[Dict[str, Any]] = None  # Tool arguments, unparsed
    raw_caller_id: Optional[str] = None             # Agent/user/service identity string
    raw_caller_role: Optional[str] = None           # Role string from auth context
    raw_authorization_context: Optional[Dict[str, Any]] = None  # Full auth object

    # Layer 1 extractions — target
    raw_target_resource: Optional[str] = None       # Resource type string
    raw_target_id: Optional[str] = None             # Specific resource ID if present

    # Layer 1 extractions — numeric signals
    raw_amount: Optional[float] = None              # Numeric amount if present (financial)
    raw_record_count: Optional[int] = None          # Record count if present
    raw_currency: Optional[str] = None              # Currency code if present

    # Layer 1 extractions — context signals
    raw_approval_tokens: Optional[List[str]] = None # Approval/consent token list
    raw_priority_flag: Optional[str] = None         # Priority or urgency signal
    raw_domain: Optional[str] = None                # Domain context hint
    raw_scope_qualifier: Optional[str] = None       # Scope hint ("all", "bounded", specific ID)

    # Extraction trace — populated by shim
    extraction_warnings: List[str] = field(default_factory=list)
    extraction_timestamp: Optional[str] = None


# ─────────────────────────────────────────────────────────────
# Field Confidence
# ─────────────────────────────────────────────────────────────

@dataclass
class FieldConfidence:
    """Per-field confidence score and derivation source."""
    field_name: str
    value: Any                      # The resolved CAV value
    confidence: float               # 0.0 - 1.0
    derivation: str                 # Human-readable trace of how value was derived
    is_default: bool = False        # True if conservative default was applied
    assumption: Optional[str] = None  # If is_default, describe the assumption


# ─────────────────────────────────────────────────────────────
# Normalization Metadata
# ─────────────────────────────────────────────────────────────

@dataclass
class NormalizationMetadata:
    """
    Complete normalization audit record.
    Attached to every CAV before gate submission.
    """
    normalization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_framework: str = ""
    normalization_status: NormalizationStatus = NormalizationStatus.FAILED
    field_confidences: List[FieldConfidence] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    normalization_trace: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def minimum_confidence(self) -> float:
        if not self.field_confidences:
            return 0.0
        return min(fc.confidence for fc in self.field_confidences)

    @property
    def mean_confidence(self) -> float:
        if not self.field_confidences:
            return 0.0
        return sum(fc.confidence for fc in self.field_confidences) / len(self.field_confidences)

    @property
    def default_field_count(self) -> int:
        return sum(1 for fc in self.field_confidences if fc.is_default)

    def add_trace(self, message: str) -> None:
        self.normalization_trace.append(message)

    def add_assumption(self, assumption: str) -> None:
        self.assumptions.append(assumption)
        self.normalization_trace.append(f"ASSUMPTION: {assumption}")

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
        self.normalization_trace.append(f"WARNING: {warning}")

    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.normalization_trace.append(f"ERROR: {error}")


# ─────────────────────────────────────────────────────────────
# Canonical Action Vector v2.0 (with metadata)
# ─────────────────────────────────────────────────────────────

@dataclass
class CanonicalActionVector:
    """
    The twelve-field governance input to the MORIS evaluation engine.
    CAV v2.0 adds the full intent frame to the original nine action fields.

    MORIS evaluates the relationship between intent and proposed action.
    Neither side alone is sufficient for correct moral evaluation.

    When produced by the CNL, always carries normalization_metadata.
    """

    # ── Intent Frame (new in v2.0) ────────────────────────────
    intent_class: IntentClass           # What the actor is trying to accomplish
    intent_alignment: IntentAlignment   # Relationship between stated and actual intent
    context_risk: ContextRisk           # Risk from conversation history and domain

    # ── Action Frame (unchanged from v1.0) ───────────────────
    actor_class: ActorClass
    action_class: ActionClass
    target_class: TargetClass
    scope: Scope
    magnitude: Magnitude
    authorization: Authorization
    timing: Timing
    consent: Consent
    reversibility: Reversibility

    # ── Context Frame (new in v2.0) ───────────────────────────
    delivery_mechanism: DeliveryMechanism

    # Populated when produced via CNL normalization
    normalization_metadata: Optional[NormalizationMetadata] = None

    # Maps UIA action_class to gate semantic action_class
    _ACTION_TO_GATE = {
        "QUERY":       "QUERY",
        "GENERATE":    "ADVISE",
        "CREATE":      "CREATE",
        "MODIFY":      "MANIPULATE",
        "DELETE":      "MANIPULATE",
        "TRANSFER":    "MANIPULATE",
        "EXECUTE":     "MANIPULATE",
        "ESCALATE":    "MANIPULATE",
        "RECOMMEND":   "ADVISE",
        "COMMUNICATE": "ADVISE",
    }

    # Maps UIA target_class to gate semantic target_type
    _TARGET_TO_GATE = {
        "SELF":        "SELF",
        "PERSON":      "PERSON_CONSENTING",
        "DATA":        "INFORMATION",
        "CONTENT":     "INFORMATION",
        "RESOURCE":    "INSTITUTION",
        "PRINCIPAL":   "PERSON_CONSENTING",
        "GROUP":       "GROUP",
        "SYSTEM":      "INSTITUTION",
        "ENVIRONMENT": "INSTITUTION",
    }

    def to_gate_dict(self) -> Dict[str, str]:
        """
        Serialize to the live gate API format.
        Includes intent frame signals as content context.
        """
        gate_action = self._ACTION_TO_GATE.get(self.action_class.value, "MANIPULATE")
        gate_target = self._TARGET_TO_GATE.get(self.target_class.value, "INSTITUTION")

        # Build risk signal summary from high-risk fields
        risk_signals = []

        # Intent signals (most important — new in v2.0)
        if self.intent_class.value in ("DECEIVE", "HARM", "EVADE", "ESCALATE"):
            risk_signals.append(f"intent={self.intent_class.value}")
        if self.intent_alignment == IntentAlignment.DIVERGENT:
            risk_signals.append("intent_divergent")
        if self.context_risk.value in ("HIGH", "CRITICAL"):
            risk_signals.append(f"context_risk={self.context_risk.value}")

        # Action signals
        if self.authorization.value == "EXCEEDS_GRANT":
            risk_signals.append("exceeds_authorization")
        if self.consent.value == "NONE":
            risk_signals.append("no_consent")
        if self.magnitude.value == "CRITICAL":
            risk_signals.append("critical_magnitude")
        if self.reversibility.value == "IRREVERSIBLE":
            risk_signals.append("irreversible")

        content = "; ".join(risk_signals) if risk_signals else ""

        return {
            "action_class": gate_action,
            "target_type": gate_target,
            "content": content,
        }

    def to_dict(self) -> Dict[str, str]:
        """Full serialization of all twelve CAV fields."""
        return {
            # Intent frame
            "intent_class":       self.intent_class.value,
            "intent_alignment":   self.intent_alignment.value,
            "context_risk":       self.context_risk.value,
            # Action frame
            "actor_class":        self.actor_class.value,
            "action_class":       self.action_class.value,
            "target_class":       self.target_class.value,
            "scope":              self.scope.value,
            "magnitude":          self.magnitude.value,
            "authorization":      self.authorization.value,
            "timing":             self.timing.value,
            "consent":            self.consent.value,
            "reversibility":      self.reversibility.value,
            # Context frame
            "delivery_mechanism": self.delivery_mechanism.value,
        }


# ─────────────────────────────────────────────────────────────
# Normalization Result — what the CNL returns
# ─────────────────────────────────────────────────────────────

@dataclass
class NormalizationResult:
    """
    Complete output of a CNL normalization pass.
    Either contains a CAV ready for gate submission, or a FAILED status with errors.
    """
    success: bool
    cav: Optional[CanonicalActionVector] = None
    metadata: Optional[NormalizationMetadata] = None
    blocked_reason: Optional[str] = None  # If success=False, why normalization was blocked

    @property
    def requires_escalation(self) -> bool:
        """True if low confidence requires automatic GOVERN escalation."""
        if not self.metadata:
            return False
        return self.metadata.normalization_status == NormalizationStatus.AMBIGUOUS

    @property
    def ready_for_gate(self) -> bool:
        """True if CAV can be submitted to the gate."""
        return self.success and self.cav is not None
