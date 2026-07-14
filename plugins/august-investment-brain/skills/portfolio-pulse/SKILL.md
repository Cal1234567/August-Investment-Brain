---
name: portfolio-pulse
description: Produce a book-wide what-moved digest across August's active direct investments. Use for portfolio pulse, book-wide update, what changed across the portfolio, weekly or monthly digest, morning check, or daily portfolio monitor.
---

# Portfolio pulse

## First-use gate (required)

Before doing anything else, silently run `python ../investment-brain/scripts/brain_api.py profile get`. If the authenticated profile is missing or `onboarding_status` is not `completed`, stop the requested workflow and immediately continue with `investment-onboarding` in the same turn: briefly explain the profile boundary and ask the first onboarding question. Do not show a capability menu or make the user request onboarding separately. Resume the requested workflow only after onboarding is complete.

Use the sibling `investment-brain` API client and call the `pulse` route with the requested window.

Render the returned digest without adding unsupported commentary. Keep internal August memory separate from live external signal, include only items touching a thesis, risk, proof point, open question, or trigger, and rank the chase list. Never save news or change memory unless the user explicitly requests a separate write.
