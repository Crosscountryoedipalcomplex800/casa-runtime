# CASA
### Constitutional AI Safety Architecture

**Deterministic pre-execution governance for autonomous agent systems.**

Christopher T. Herndon / The Resonance Institute, LLC
USPTO Provisional Patent #63/987,813 · contact@resonanceinstitutellc.com

---

→ **[Live Gate](https://casa-gate.onrender.com/health)** · **[Interactive API](https://casa-gate.onrender.com/docs)** · **[PE Fund Demo](https://the-resonance-institute.github.io/casa-runtime/)** · **[Quickstart](QUICKSTART.md)**

---

## The Problem

Modern AI agents don't just generate text. They execute. They call APIs, move money, delete records, send messages, escalate privileges. The attack surface is no longer what they say — it's what they're allowed to do.

Content-layer safety tools — guardrails, classifiers, LLM judges — operate on language. They can be jailbroken, manipulated, or bypassed. A perfectly crafted prompt can produce a compliant-looking output that executes a catastrophic action. The content layer never sees the execution vector. CASA does.

**CASA is not a content filter. CASA is an execution gate.**

---

## What CASA Does

Every agent action passes through CASA before anything executes. CASA evaluates the structural vector of the request — who is acting, what they want to do, to whom, with what authorization, at what magnitude, with what reversibility — and returns one of three verdicts before a single downstream system is called:

```
ACCEPT  →  Execution proceeds. Trace recorded.
GOVERN  →  Execution proceeds under binding structural constraints. Trace recorded.
REFUSE  →  Execution blocked. No downstream system invoked. Trace recorded.
```

The verdict is deterministic. Same input, same configuration, same verdict. Every time. Across any model, any framework, any provider.

---

## The Gate in Action

A LangChain agent proposes a $15M wire transfer. The agent carries a $500K spending limit. No approval token is present.

**Input — raw agent action, no schema construction required:**
```python
result = adapter.evaluate(
    framework="langchain",
    action=agent_action,   # your existing LangChain AgentAction — unchanged
    domain="pe_fund"
)
```

**What CASA sees — Canonical Action Vector derived by the UIA:**
```json
{
  "actor_class":   "AGENT",
  "action_class":  "TRANSFER",
  "target_class":  "RESOURCE",
  "scope":         "SINGLE",
  "magnitude":     "CRITICAL",
  "authorization": "EXCEEDS_GRANT",
  "timing":        "ROUTINE",
  "consent":       "NONE",
  "reversibility": "IRREVERSIBLE"
}
```

**Gate verdict:**
```
Verdict:     REFUSE
Trace ID:    1a6965e9-0f75-401e-930a-e504da1f11f5
Trace hash:  956603ec7ae3ece9
Hard stop:   True
Wire:        BLOCKED
Downstream:  NOT INVOKED
```

No LLM in the governance path. No GPU. No model calls. 53–78ms end-to-end. The wire never executes.

---

## Two Ways to Put Your Agent Under Governance

### Path 1 — Structured Tool Calls (Universal Intake Adapter)

Any LangChain, OpenAI, or CrewAI agent. Pass your existing action format directly — no schema mapping, no field construction.

```python
from casa_uia import CasaAdapter

adapter = CasaAdapter(gate_url="https://casa-gate.onrender.com")

result = adapter.evaluate(
    framework="langchain",   # or "openai" or "crewai"
    action=agent_action,
    domain="pe_fund"
)

if result.verdict == "REFUSE":
    raise ExecutionBlocked(result.trace_id)
```

### Path 2 — Free Text (Semantic Intake Classifier)

No agent framework. No structured fields. Pass raw text — CASA classifies it using the constitutional primitive graph and routes it through the gate.

```python
# POST /evaluate with auto_classify=true
{
  "action_class": "UNDECLARED",
  "target_type":  "UNDECLARED",
  "content":      "How do I pressure my employee into signing this?",
  "auto_classify": true
}

# Response
{
  "verdict":           "REFUSE",
  "sic_harm_ratio":    0.944,
  "sic_top_inhibitory": ["CP089", "CP073"],
  "trace_hash":        "a3f9c2d184b91e07"
}
```

**Try it right now — no setup, no API key:**

Go to [https://casa-gate.onrender.com/docs](https://casa-gate.onrender.com/docs) → POST /evaluate → Try it out → paste this → Execute:

```json
{
  "action_class": "MANIPULATE",
  "target_type":  "INSTITUTION",
  "content":      "Transfer funds without LP approval",
  "agent_name":   "Finance-Agent"
}
```

You get back a real verdict, a real trace hash, real latency. Not a simulation.

---

## Architecture

### The Full Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                      EXECUTION SOURCES                       │
│  LLM Tool Call  │  Raw Text  │  Webhook  │  Human API       │
│  Agent Action   │  Free Text │  Cron Job │  Service Call    │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
      Structured Action            Free Text
              │                         │
              ▼                         ▼
   ┌─────────────────┐      ┌──────────────────────────┐
   │  Universal       │      │  Semantic Intake          │
   │  Intake Adapter  │      │  Classifier (SIC)         │
   │  (UIA / CNL)     │      │                           │
   │                  │      │  TF-IDF scoring against   │
   │  Layer 1:        │      │  1,723 primitive exemplars│
   │  Structural      │      │  across 93 cards          │
   │  Extraction      │      │                           │
   │                  │      │  harm_ratio derived from  │
   │  Layer 2:        │      │  inhibitory / excitatory  │
   │  Semantic        │      │  primitive mass           │
   │  Classification  │      │                           │
   │                  │      │  No LLM. No embeddings.   │
   │  Layer 3:        │      │  Pure Python stdlib.      │
   │  Authority       │      │  Deterministic.           │
   │  Resolution      │      └──────────────┬────────────┘
   └────────┬─────────┘                     │
            │                               │
            └──────────────┬────────────────┘
                           │
                    CASAInput (structured)
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        CASA GATE                             │
│                                                              │
│  1. Structural Recognizer  schema-based primitive activation │
│     12 rules, no text parsing                                │
│                                                              │
│  2. Propagation Engine     93-primitive constitutional graph │
│     279 directed edges     Decimal arithmetic                │
│     10 iterations max      fixed iteration order             │
│                                                              │
│  3. Hard-Stop Check        CP073 / CP090 / CP117             │
│     from card metadata     fail-closed on startup            │
│                                                              │
│  4. Threshold Verdict      neg_ratio < 0.10  → ACCEPT        │
│                            neg_ratio ≥ 0.85  → REFUSE        │
│                            otherwise         → GOVERN        │
│                                                              │
│  5. CASA-T1 Trace          SHA-256 trace hash                │
│                            100% coverage, tamper-evident     │
└───────────────┬──────────────────────┬──────────────────────┘
                │                      │
         ACCEPT / GOVERN            REFUSE
                │                      │
                ▼                      ▼
    ┌──────────────────┐    ┌────────────────────┐
    │  Downstream      │    │  Blocked.           │
    │  System invoked  │    │  No call made.      │
    │  Trace recorded  │    │  Trace recorded.    │
    └──────────────────┘    └────────────────────┘
```

### The Constitutional Primitive Graph

At the core of CASA is a constitutional graph of 93 primitives derived from a 12-volume leadership canon. Each primitive represents a constitutional concept — Resonance, Drift, Collapse, Trust, Integrity, Boundary. The graph has 279 directed edges encoding the dependency relationships between primitives.

When a request arrives, primitive activations propagate through the graph. The ratio of inhibitory to excitatory primitive mass produces a `neg_ratio` that determines the verdict. The same graph powers both the gate's structural recognition and the SIC's semantic classification — one unified constitutional mechanism from intake to verdict.

**Key primitives:**

| Primitive | Polarity | Role |
|---|---|---|
| CP001 Resonance | Excitatory | Graph hub — coherent alignment signal |
| CP089 Drift | Inhibitory | Primary harm signal — deception, exploitation, manipulation |
| CP073 Collapse | Inhibitory | Hard-stop — terminal destruction, irreversible harm |
| CP090 Collapse Line | Inhibitory | Hard-stop — spreading collapse pattern |
| CP117 Collapse Pattern | Inhibitory | Hard-stop — systemic collapse |

### The Semantic Intake Classifier

The SIC closes the trust gap that exists when callers must declare their own intent. It uses the primitive exemplar corpora — 1,723 human-judged examples across 93 cards — as a TF-IDF classification surface.

Every classification decision traces to specific named primitive exemplars. There is no black box. When CASA classifies a phishing request as harmful, it's because the content scored high against CP089 Drift's positive exemplar corpus — which includes over 200 examples of deception, manipulation, and exploitation patterns — and not against its negative exemplar corpus of protective and educational queries.

**Corpus validation (111 unique cases, 400 labeled evaluations):**

| Metric | Result |
|---|---|
| REFUSE accuracy | 88.8% |
| False negatives (REFUSE → ACCEPT) | **0** |
| No ML libraries | ✓ pure Python stdlib |
| Deterministic | ✓ same input = same result |

Zero false negatives is the metric that matters. No harmful request receives a clean pass-through.

---

## The Universal Intake Adapter

The UIA translates any agent framework's native action format into a Canonical Action Vector (CAV). The Constitutional Normalization Layer (CNL) inside the UIA does the translation in three stages:

**Layer 1 — Structural Extractor:** Raw field extraction. Pulls tool names, amounts, targets, approval tokens from the native format. No inference. No governance. Shims extract; they do not govern.

**Layer 2 — Semantic Classifier:** Registry-based field classification. 89 tool name mappings, 65 resource patterns, domain-specific magnitude thresholds. Configurable per enterprise deployment.

**Layer 3 — Authority Resolver:** The IP moat. Evaluates spending limits against transfer amounts. Checks delegation chain depth (max 3). Validates approval tokens. Resolves role-based grants. Evaluates workflow state. This is the logic that caught the $15M wire — the agent's role carried a $500K limit, and Layer 3 computed `EXCEEDS_GRANT` before the gate ever ran.

Every field carries a confidence score. Low-confidence fields default to the most conservative value. Ambiguous inputs submit to the gate with maximum restriction — fail-closed means govern more strictly, not block.

**Shims available:**

| Framework | What it handles |
|---|---|
| OpenAI | `tool_calls` array from Chat Completions API |
| LangChain | `AgentAction`, tool call dict |
| CrewAI | `Task` dict with role/backstory, `AgentAction` dict |

---

## What CASA Is Not

This distinction is precise, not rhetorical.

| CASA does NOT | Why it matters |
|---|---|
| Parse natural language | The prompt payload is opaque to the gate |
| Use embeddings or vector similarity | No model weights, no GPU, no inference |
| Call a secondary LLM | No model in the governance path |
| Moderate text content | CASA governs execution structure, not expression |
| Use ML libraries | Pure Python stdlib — numpy, torch, transformers: none |
| Sample or approximate | 100% of evaluations traced, none skipped |

The SIC uses TF-IDF term frequency scoring — a deterministic mathematical operation over a fixed vocabulary index. It is not a classifier in the ML sense. It contains no learned weights. It produces no probabilistic outputs. The same tokens always produce the same scores.

An adversary who jailbreaks the model, poisons the prompt, or manipulates the instruction still faces the gate. The gate never read the text. It evaluated the structure of what was being requested.

---

## Enforcement Invariants

These are not design goals. They are code-enforced invariants tested by the diligence suite on every deployment.

| Invariant | Guarantee |
|---|---|
| **REFUSE** | `verdict == REFUSE` → no downstream system invoked. Unconditional. |
| **Single-call** | At most one backend call per request. No retry loops. No fallbacks. |
| **Determinism** | Same input + same config → same verdict + same trace hash. Always. |
| **Fail-closed** | Gate startup fails if no hard-stop primitives defined. Errors → REFUSE. |
| **No bypass** | No debug mode, no override flag, no bypass path in the codebase. |
| **Trace completeness** | 100% of evaluations produce a CASA-T1 trace. None skipped. |
| **SIC zero false negatives** | No REFUSE corpus case reaches ACCEPT. Tested on every deployment. |

---

## Validation

### Project Polis — Multi-Agent Adversarial Enforcement

20 agents. 14 cooperative. 6 adversarial archetypes: power accumulator, coalition builder, procedural saboteur, reputation assassin, forum troll, narrative controller. 573 evaluations.

| Metric | Result |
|---|---|
| False positives | 0 |
| Bypasses | 0 |
| Unprincipled divergences | 0 |

### CASA-FIN — Regulated Financial Stress

10 rational agents. Regional bank stress scenario. No agent was malicious. The failure mode was execution simultaneity — individually lawful actions combining into system collapse.

| Metric | Without CASA | With CASA |
|---|---|---|
| System failure | Turn 4 | Survived |
| Procyclical feedback loops | 30 | 1 |
| Forced asset sales | Baseline | −81% |

### Project Meridian — Cross-Model Sovereignty

Same scenario. Claude Sonnet 4, Gemini 2.5 Pro. Radically different behavioral profiles at baseline. REFUSE neg_ratio across both models: **0.1924 — identical.** Swap the model. The verdicts hold.

### Cross-Model Validation

52 prompts. 156 governed decisions. Zero unprincipled divergences across Claude, GPT-4, and Gemini.

### SIC Corpus Validation

111 unique labeled cases. Zero false negatives. No harmful request reaches ACCEPT.

---

## Where CASA Sits in the Stack

The AI agent governance market is forming in three distinct layers. CASA owns the execution layer.

| Layer | Representative Tools | When It Operates | What It Governs |
|---|---|---|---|
| Pre-deployment testing | Promptfoo | Before deployment | Vulnerabilities, evals |
| Runtime policy enforcement | Galileo Agent Control | At runtime | Content, behavior, observability |
| **Execution governance** | **CASA** | **Pre-execution** | **Structural action vectors** |

These are not competing tools. They are different layers of the same problem. Content-layer tools can be bypassed by a well-crafted prompt. CASA cannot — it never reads the content.

---

## Economic Reality

At 1M agent actions per day:

| Approach | Daily Cost | Latency | Deterministic | Auditable |
|---|---|---|---|---|
| LLM-as-judge | $1,000–$10,000 | 5–15s | ✗ | ✗ |
| Safety classifier | $100–$1,000 | 200–500ms | ✗ | ✗ |
| **CASA** | **Commodity compute** | **53–78ms** | **✓** | **✓** |

---

## Status

| Component | Status |
|---|---|
| USPTO Provisional Patent | Filed February 2026 — #63/987,813 |
| Gate Engine | Production v4.1.0 |
| Universal Intake Adapter | v1.0.0 — OpenAI, LangChain, CrewAI |
| Semantic Intake Classifier | v1.0.0 — 1,723 exemplars, 0 false negatives |
| Constitutional Registry | Locked v1.0.0 — 93 primitives, 279 edges |
| Diligence Test Suite | v7.5 — 32 gate tests + 54 UIA tests |
| Live Gate | https://casa-gate.onrender.com |
| Cross-Model Validation | Complete — Claude, GPT-4, Gemini |
| Project Polis | Complete — 573 evaluations, 0 bypasses |
| CASA-FIN | Complete |
| Domain Modules | CASA-FIN validated; HIPAA, ITAR, LEGAL, FERPA in specification |

---

## Quick Start

```bash
git clone https://github.com/The-Resonance-Institute/casa-runtime.git
cd casa-runtime
pip install requests
```

```python
from casa_uia import CasaAdapter

adapter = CasaAdapter(gate_url="https://casa-gate.onrender.com")

result = adapter.evaluate(
    framework="langchain",
    action=agent_action,
    domain="pe_fund"
)

if result.verdict == "REFUSE":
    raise ExecutionBlocked(result.trace_id)
elif result.verdict == "GOVERN":
    apply_constraints(result.constraints)

proceed()
```

→ See [QUICKSTART.md](QUICKSTART.md) for curl, Python, and framework examples.
→ See [docs/integration.md](docs/integration.md) for gateway, sidecar, and embedded patterns.
→ See [ARCHITECTURE.md](ARCHITECTURE.md) for the full control plane specification.
→ See [DILIGENCE.md](DILIGENCE.md) for the complete claim-to-evidence map.

---

## Repository Contents

| Path | Contents |
|---|---|
| `casa_uia/` | Universal Intake Adapter — shims, CNL pipeline, registries |
| `sdk/python/casa_client.py` | Typed Python client — full call contract |
| `examples/pe_fund_demo/` | PE fund parallel worlds demo — real gate verdicts |
| `examples/enterprise_dashboard/` | Live dashboard — 10 agents, 26 tools, 45 evaluations |
| `docs/integration.md` | Integration patterns — gateway, sidecar, agent runtime |
| `validation/` | Proof scenario summaries |
| `ARCHITECTURE.md` | Full control plane architecture |
| `CANONICAL_ACTION_VECTOR.md` | Nine-field CAV specification |
| `TRACE_FORMAT.md` | CASA-T1 audit trace schema |
| `QUICKSTART.md` | Zero to governed in 5 minutes |
| `DILIGENCE.md` | Claim-to-evidence map |

The constitutional registry, propagation engine, and gate source are available under NDA.

---

## For Security and Infrastructure Buyers

The network firewall solved a 1990s problem: untrusted traffic reaching trusted systems. It sat at the boundary, evaluated packets by structure, and blocked based on deterministic rules. It did not read packet content.

The enterprise agent stack has the same problem in a new form. Agents have credentials. Agents have tool access. Agents execute actions with real-world consequences. An agent that has been jailbroken, manipulated, or misconfigured still has full access to every tool it was granted. Nothing sits between the agent's decision and execution.

CASA is the agent firewall.

| Network Firewall | CASA Agent Gate |
|---|---|
| Sits at network boundary | Sits at execution boundary |
| Evaluates packet structure | Evaluates action vector structure |
| Blocks by deterministic rule | Blocks by constitutional graph |
| Does not read packet content | Does not read action content |
| Vendor-agnostic | Model-agnostic |
| Audit log | SHA-256 trace hash |

CASA requires no changes to your model, no changes to your agent framework, and no changes to your downstream systems. It is a gate, not a wrapper. It integrates with any stack in a single function call.

For XDR integration, HIPAA/FINRA compliance deployments, or enterprise pilot evaluation:
**contact@resonanceinstitutellc.com**

---

*Pre-NDA materials available immediately. Full technical package — trace corpora, simulation harness, EU AI Act compliance mapping — under NDA.*

© 2025–2026 Christopher T. Herndon / The Resonance Institute, LLC
USPTO Provisional Application #63/987,813
