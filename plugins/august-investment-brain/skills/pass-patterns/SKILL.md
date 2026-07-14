---
name: pass-patterns
description: Analyze recurring reasons August passed on direct deals and apply those patterns to a named opportunity. Use for why do we pass, pass patterns, what kills our deals, red-flag library, pass DNA, or whether a deal trips prior warning patterns.
---

# Pass patterns

## First-use gate (required)

Before doing anything else, silently run `python ../investment-brain/scripts/brain_api.py profile get`. If the authenticated profile is missing or `onboarding_status` is not `completed`, stop the requested workflow and immediately continue with `investment-onboarding` in the same turn: briefly explain the profile boundary and ask the first onboarding question. Do not show a capability menu or make the user request onboarding separately. Resume the requested workflow only after onboarding is complete.

Use the sibling `investment-brain` API client and call `analyst-read` with a question that asks for cited recurring patterns from passed-deal memory.

Each pattern must name the prior deals and source basis behind it. Distinguish recorded pass reasons from residue inferred from risks or open questions. When applying patterns to a live target, state whether each match is sourced or inferred and name the earliest diligence question that would settle it.
