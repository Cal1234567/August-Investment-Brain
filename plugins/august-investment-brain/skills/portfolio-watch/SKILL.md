---
name: portfolio-watch
description: Check thesis drift for one portfolio or indexed company by comparing live external change with August's stored view. Use for watch this company, what changed, news check, thesis drift, has the story moved, catch me up, or monitor this company.
---

# Portfolio watch

## First-use gate (required)

Before doing anything else, silently run `python ../investment-brain/scripts/brain_api.py profile get`. If the authenticated profile is missing or `onboarding_status` is not `completed`, stop the requested workflow and immediately continue with `investment-onboarding` in the same turn: briefly explain the profile boundary and ask the first onboarding question. Do not show a capability menu or make the user request onboarding separately. Resume the requested workflow only after onboarding is complete.

Ask for the company and time window only when missing. Use the sibling `investment-brain` API client and call `analyst-read` with a what-changed question; use `signal` only for a targeted expansion.

Separate internal August memory from external signal. Tie each material update to a stored thesis, risk, proof point, open question, or view-change trigger. Undated or out-of-window items are context, not movement. End with no view change unless the evidence earns one.
