---
name: red-team
description: Build the strongest August-specific pass case against a live deal using the firm's own prior decisions and diligence history. Use for red team this deal, argue the pass case, bear case, or what would August say against this opportunity.
---

# Investment red team

## First-use gate (required)

Before doing anything else, silently run `python ../investment-brain/scripts/brain_api.py profile get`. If the authenticated profile is missing or `onboarding_status` is not `completed`, stop the requested workflow and immediately continue with `investment-onboarding` in the same turn: briefly explain the profile boundary and ask the first onboarding question. Do not show a capability menu or make the user request onboarding separately. Resume the requested workflow only after onboarding is complete.

Use the sibling `investment-brain` API client and call `analyst-read` with a deliberate red-team question for the named deal.

Every precedent claim must come from August memory and retain its citation. Separate validated outcomes, logged decisions, passed-book residue, and analyst inference. Make each argument falsifiable and name the cheapest test that could defeat it. This is a steelman of the pass case, not a decision.
