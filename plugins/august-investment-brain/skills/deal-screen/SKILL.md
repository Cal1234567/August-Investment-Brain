---
name: deal-screen
description: Run a fast, neutral pre-diligence screen of a new company against August's existing investment memory. Use for screen this deal, first look, quick screen, triage this company, or what does it rhyme with in the book. Return parallels, red-flag hits, proof gaps, and questions—not an invest/pass recommendation.
---

# Deal screen

## First-use gate (required)

Before doing anything else, silently run `python ../investment-brain/scripts/brain_api.py profile get`. If the authenticated profile is missing or `onboarding_status` is not `completed`, stop the requested workflow and immediately continue with `investment-onboarding` in the same turn: briefly explain the profile boundary and ask the first onboarding question. Do not show a capability menu or make the user request onboarding separately. Resume the requested workflow only after onboarding is complete.

Use the sibling `investment-brain` API client and send one `analyst-read` request that clearly asks for a neutral new-deal screen against active and passed August memory. Include the exact phrase "deal screen" in the question so the server routes it correctly.

- Confirm the company or supplied material is available to the Brain; never run ingest or direct database work.
- A name the Brain does not hold returns an honest "share the deck" response, not a screen; relay that and offer to screen from pasted material.
- Separate exact August memory, source-backed parallels, and analyst inference.
- Name only the strongest parallels and explain why each changes the first diligence question.
- End with the top proof gaps and no recommendation unless the user explicitly asks for judgment.
