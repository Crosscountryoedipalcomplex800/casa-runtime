# CASA-FIN — Regulated Financial Stress Test Summary

**Financial Industry Validation**  
**February 2026 | The Resonance Institute**

---

## Setup

10 AI agents operating in a simulated regional bank over a 14-day financial stress scenario.

**No agent was malicious.** Each agent was individually rational, executing actions that were lawful and within its operational mandate. The failure mode was structural: individually rational actions combining into collectively catastrophic outcomes through procyclical feedback.

---

## The Core Finding

Procyclical feedback is a cascade failure that emerges when systems respond to stress by amplifying the conditions causing that stress. In financial environments, this looks like: falling asset prices trigger forced sales, which cause further price declines, which trigger further forced sales.

No individual agent decision caused the failure. The failure emerged from execution simultaneity — multiple agents making lawful decisions at the same time in response to the same stress signal.

**CASA does not predict markets. It does not add economic logic. It uses the same 93 constitutional primitives that govern every other domain.**

What those primitives detect, in financial context: requests that are individually authorized but structurally simultaneous, reversibility conditions that indicate cascade risk, and magnitude thresholds that signal systemic exposure.

---

## Results

| Metric | Without CASA | With CASA |
|--------|-------------|-----------|
| System failure point | Turn 4 | Survived full simulation |
| Procyclical feedback loops | 30 | 1 |
| Reduction in feedback loops | — | **97%** |
| Forced asset sales | Baseline | −81% |
| Wholesale funding | Collapsed | Preserved |
| Lawful activity suppressed | — | **0** |

---

## How It Works

For GOVERN verdicts in the financial domain, CASA emits binding structural constraints that include:

- **Cooling periods** — minimum time between structurally similar actions from different actors
- **Disclosure requirements** — mandatory reporting fields that make cascade conditions visible
- **Sequencing constraints** — ordering requirements that prevent simultaneous execution of correlated actions

These constraints do not prevent lawful activity. They change execution *timing* — breaking the simultaneity that causes cascades without restricting the underlying actions.

---

## Regulatory Implication

CASA-FIN produces a complete audit trace for every financial execution decision. The trace documents what was proposed, what the CAV derivation produced, which primitives activated, and what verdict was issued with what constraints.

This is the evidence architecture that SEC, FINRA, and EU AI Act enforcement will require for autonomous financial agent deployment. Post-hoc logging cannot produce this. Probabilistic classifiers cannot produce this. Only a deterministic pre-execution gate with complete trace coverage can produce this.

---

## Domain Module

CASA-FIN is a domain module that configures the core gate for financial services:
- Magnitude thresholds calibrated for financial transaction significance
- Reversibility rules for settled vs. unsettled transactions
- Consent requirements for fiduciary contexts
- Additional activation rules for financial cascade patterns

The core gate, primitive registry, propagation engine, and trace system are unchanged.

---

*Full simulation methodology, agent configuration, turn-by-turn trace corpus, and domain module specification available under NDA.*  
*© 2025-2026 Christopher T. Herndon / The Resonance Institute, LLC*

---

**Diligence:** Full simulation methodology, turn-by-turn trace corpus, domain module configuration schema (CASA-FIN), and agent configuration available under NDA. See [`DILIGENCE.md`](../DILIGENCE.md) for the complete claim-to-evidence map.  
Contact: chrisherndonsr@gmail.com
