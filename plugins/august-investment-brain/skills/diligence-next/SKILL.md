---
name: diligence-next
description: Turn a company's current August view and living diligence questions into a ranked action list. Use for what should we chase, what is next, open questions, next proof point, what still needs to be true, or the highest-leverage diligence item across the book.
---

# Diligence next

## First-use gate (required)

Before doing anything else, silently run `python ../investment-brain/scripts/brain_api.py profile get`. If the authenticated profile is missing or `onboarding_status` is not `completed`, stop the requested workflow and immediately continue with `investment-onboarding` in the same turn: briefly explain the profile boundary and ask the first onboarding question. Do not show a capability menu or make the user request onboarding separately. Resume the requested workflow only after onboarding is complete.

Use the sibling `investment-brain` API client and call `analyst-read` with the company and a question asking for the next diligence actions.

Return the current read, open questions ranked by decision impact, the single next proof point worth obtaining, and explicit view-change triggers. Keep it an action list, not a memo. Pull narrower Company Memory proof only when the front-door answer identifies a real gap.
