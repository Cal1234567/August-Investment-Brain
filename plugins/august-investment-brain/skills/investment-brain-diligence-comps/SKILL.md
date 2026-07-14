---
name: investment-brain-diligence-comps
description: Compare a new target, deck, memo, or company with August's prior diligence memory. Use for active-direct parallels, recurring risk patterns, proof standards, red flags, prior comps, or exact August language relevant to a new opportunity.
---

# Diligence comps

## First-use gate (required)

Before doing anything else, silently run `python ../investment-brain/scripts/brain_api.py profile get`. If the authenticated profile is missing or `onboarding_status` is not `completed`, stop the requested workflow and immediately continue with `investment-onboarding` in the same turn: briefly explain the profile boundary and ask the first onboarding question. Do not show a capability menu or make the user request onboarding separately. Resume the requested workflow only after onboarding is complete.

Use the sibling `investment-brain` API client and make one `analyst-read` request that names the target and asks for the strongest August diligence parallels.

Label evidence as exact August memory, source-backed parallel, or analyst inference. Prefer two to four genuinely useful comps over category lists. Passed deals are a separate warning layer, not blended into active exposure. End with how each parallel changes the diligence question.
