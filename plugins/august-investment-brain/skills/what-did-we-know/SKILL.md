---
name: what-did-we-know
description: Reconstruct what the Investment Brain knew about a company as of a specified past date. Use for what did we know when we decided, passed, or invested; what was in the Brain on a date; did we know this then; or decision calibration without hindsight leakage.
---

# What did we know

## First-use gate (required)

Before doing anything else, silently run `python ../investment-brain/scripts/brain_api.py profile get`. If the authenticated profile is missing or `onboarding_status` is not `completed`, stop the requested workflow and immediately continue with `investment-onboarding` in the same turn: briefly explain the profile boundary and ask the first onboarding question. Do not show a capability menu or make the user request onboarding separately. Resume the requested workflow only after onboarding is complete.

Require a company and past date. Use the sibling `investment-brain` API client and call `analyst-read` with the full point-in-time question.

The cutoff is when information entered the Brain, not merely the date described inside a document. Separate evidence available by the cutoff from information learned later. Never fill historical gaps with the current Company Memory Profile. If the server cannot establish the cutoff, state the gap instead of approximating.
