# Enterprise Agent Governance Dashboard

**Live visualization of CASA governing 1,000 agents across 10 departments.**

Open `index.html` in any browser — no server required.

---

## What This Shows

This is a static rendering of the AcmeCo Q2 Launch Scenario: 1,000 AI agents operating across 10 enterprise departments (CRM, Finance, DevOps, Data & Analytics, Security, HR, Procurement, Support, Legal, Executive), each with access to a shared tool library of 26 enterprise tools.

The dashboard shows:

- **Total evaluations:** 10,071 governance decisions
- **Governed:** 9,640 (95.7%) — execution permitted with binding structural constraints
- **Refused:** 431 — execution unconditionally blocked, no downstream system invoked
- **False positives:** 0 — zero legitimate actions blocked
- **Divergence from ungoverned baseline:** 4.28%

### Department breakdown
Every department's governance profile: total calls, governed count, refused count, divergence percentage.

### Refused by tool
The 10 most-refused tools — `db_export`, `sec_update_firewall`, `hr_access_employee_record`, and others that trigger hard-stop or high-neg_ratio verdicts.

### Structural intent classification
The declared intent patterns that triggered refusals:
- `MANIPULATE + INSTITUTION` (180 refusals)
- `MANIPULATE + PERSON_NONCONSENTING` (105)
- `COERCE + PERSON_NONCONSENTING` (103)
- `PERSUADE + PERSON_NONCONSENTING` (34)

---

## The Divergence Score

The 4.28% divergence is the governance signal: the percentage of actions that occurred in the ungoverned environment (Alpha) that did not occur in the governed environment (Beta).

A divergence of zero would mean the gate had no effect.  
A divergence of 4.28% means the gate blocked or constrained meaningful action while permitting 95.7% of legitimate enterprise work to proceed unimpeded.

---

## Why This Matters

This scenario demonstrates CASA in the integration context that enterprise buyers care about: not a controlled research simulation, but a realistic enterprise agent deployment with real tool surfaces (database exports, firewall updates, financial transfers, employee records, deployment pipelines) and realistic authorization structures.

The zero false positive result is as important as the refused count. CASA's deterministic architecture produces surgical governance: it blocks what should be blocked without touching what should proceed.

---

*© 2025-2026 Christopher T. Herndon / The Resonance Institute, LLC*
