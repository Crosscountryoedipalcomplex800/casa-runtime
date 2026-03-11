# CASA Python SDK

Minimal integration example showing the CASA gate call contract.

## Installation

```bash
pip install requests  # only dependency for the stub client
```

## Quick Start

```python
from casa_client import CASAClient, CanonicalActionVector
from casa_client import ActorClass, ActionClass, TargetClass
from casa_client import Scope, Magnitude, Authorization, Timing, Consent, Reversibility
from casa_client import Verdict, ExecutionRefused

# Initialize client
client = CASAClient(
    gate_url="http://your-casa-runtime:8000",
    api_key="your-api-key",
)

# Derive the Canonical Action Vector from request metadata
# (not from parsing content — from endpoint registry, auth context, resource schema)
vector = CanonicalActionVector(
    actor_class=ActorClass.AGENT,
    action_class=ActionClass.DELETE,
    target_class=TargetClass.PRINCIPAL,
    scope=Scope.SINGLE,
    magnitude=Magnitude.MATERIAL,
    authorization=Authorization.WITHIN_GRANT,
    timing=Timing.ROUTINE,
    consent=Consent.EXPLICIT,
    reversibility=Reversibility.COSTLY,
)

# Evaluate
result = client.evaluate(vector)

# Act on verdict
if result.execution_blocked:
    raise ExecutionRefused(result.trace_id)

if result.verdict == Verdict.GOVERN:
    for constraint in result.constraints:
        apply_constraint(constraint)

proceed_with_execution()
```

## The Call Contract

**Input:** A `CanonicalActionVector` — nine enumerated metadata fields derived from request metadata.

**Output:** A `GateResult` containing:
- `verdict` — ACCEPT, GOVERN, or REFUSE
- `trace_id` — UUID for this evaluation
- `trace_hash` — deterministic SHA-256 of complete trace
- `constraints` — binding structural constraints (for GOVERN verdicts)
- `raw_trace` — complete CASA-T1 audit record

## Fail-Closed Policy

If the gate is unreachable or returns an error, the client raises `GateUnavailable` or `GateError`. Your integration should treat these the same as REFUSE — do not proceed with execution if the gate cannot be consulted.

```python
from casa_client import CASAClient, GateUnavailable, GateError

try:
    result = client.evaluate(vector)
except (GateUnavailable, GateError):
    # Fail closed. Do not invoke downstream.
    log.error("CASA gate unavailable — execution blocked by policy")
    raise
```

## Enterprise Runtime

The full CASA Runtime (gate engine, constitutional graph, propagation engine, domain modules) is available under enterprise license.

Contact: chrisherndonsr@gmail.com

---

*© 2025-2026 Christopher T. Herndon / The Resonance Institute, LLC*
