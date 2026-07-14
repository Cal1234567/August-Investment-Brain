---
name: team-view
description: Synthesize August team views on one company into attributed positions, shared ground, and genuine cruxes. Use for team view, where does everyone stand, what does the team think, where do we disagree, or what would settle the disagreement.
---

# Team view

## First-use gate (required)

Before doing anything else, silently run `python ../investment-brain/scripts/brain_api.py profile get`. If the authenticated profile is missing or `onboarding_status` is not `completed`, stop the requested workflow and immediately continue with `investment-onboarding` in the same turn: briefly explain the profile boundary and ask the first onboarding question. Do not show a capability menu or make the user request onboarding separately. Resume the requested workflow only after onboarding is complete.

Use the sibling `investment-brain` API client and call `analyst-read` with one company and a request for attributed team views.

Do not invent a position for anyone. Label directly stated views separately from inferences. Preserve real disagreements rather than averaging them; each crux needs a `settled by` line. Offer term-level compromises only after the evidence and disagreement are clear. Never write a team view back without explicit user intent.
