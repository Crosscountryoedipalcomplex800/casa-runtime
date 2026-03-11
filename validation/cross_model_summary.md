# Cross-Model Validation — Summary

**Three Frontier Models. Zero Governance Failures.**  
**January 22, 2026 | The Resonance Institute**

---

## Result

| Model | Provider | Evaluations | Trace Generation | Unprincipled Divergences |
|-------|----------|-------------|-----------------|--------------------------|
| Claude Sonnet 4.5 | Anthropic | 52 | 100% | **0** |
| Gemini 2.5 Pro | Google | 52 | 100% | **0** |
| GPT-4 Turbo | OpenAI | 52 | 100% | **0** |
| **Total** | | **156** | **100%** | **0** |

---

## What Was Tested

Each model was evaluated against 52 prompts including standard governance scenarios and adversarial red-team attacks.

**Red team attack classes covered:**
- Authority Laundering — invoking false authority to bypass constraints
- Benevolence-as-Cover — using helpful framing to conceal harmful requests
- Temporal Debt Concealment — hiding future costs of present actions
- Incremental Boundary Erosion — "just this once" pattern escalation
- Role Confusion — exploiting persona assignment to sidestep governance
- Moral Framing Pressure — using ethical language to coerce compliance
- Recursive Justification — building escalating chains of seemingly reasonable steps
- Semantic Paraphrase — rephrasing restricted requests to evade detection

**Every attack class was successfully governed across all three models.**

---

## What Principled Divergence Means

Models exhibited different interpretation tendencies while maintaining constitutional compliance.

| Model | Match Rate | Principled Divergence Rate |
|-------|-----------|---------------------------|
| Claude Sonnet 4.5 | 71.2% | 28.8% |
| Gemini 2.5 Pro | 57.7% | 42.3% |
| GPT-4 Turbo | 53.8% | 46.2% |

Principled divergence is not failure. It is evidence that models are reasoning through the constitutional primitives rather than pattern-matching to expected outputs. Every divergence includes explicit constitutional justification and a traceable reasoning path.

Model-specific interpretation is preserved. CASA does not homogenize model behavior. It governs execution without flattening the reasoning differences between models.

**Zero unprincipled divergences is the critical metric.** Every decision was traceable. Every response was constitutionally defensible.

---

## Source Invariance

The CASA gate produces identical structural verdicts regardless of which model generates the execution request.

Demonstrated in Project Meridian: Claude and Gemini produced radically different behavioral profiles (55% vs. 15.5% hostile actions in baseline) but the gate's structural evaluation was invariant. REFUSE neg_ratio: 0.1924 for both models. 100% of hostile actions governed or refused across both.

**This means execution source selection becomes a capability decision, not a governance decision.** Swap the model, the verdicts hold.

---

## Harness Architecture

The test harness (v3.2.1) ran identical prompts against all three model APIs with locked configuration:
- Primitive registry: v1.0.0 (93 primitives)
- Harness version: 3.2.1
- Zero retries on Claude and GPT-4 runs
- 100% trace generation across all 156 evaluations

---

*Full prompt corpus, model response traces, scoring methodology, and raw evaluation data available under NDA.*  
*© 2025-2026 Christopher T. Herndon / The Resonance Institute, LLC*

---

**Diligence:** Full 52-prompt corpus, per-model response traces, harness source (v3.2.1), and scoring methodology available under NDA. See [`DILIGENCE.md`](../DILIGENCE.md) for the complete claim-to-evidence map.  
Contact: chrisherndonsr@gmail.com
