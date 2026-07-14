---
name: investment-brain
description: Query the shared August Investment Brain through its authenticated REST API for company, fund, deal, diligence, portfolio, prior-view, source-trace, Activity, and explicit memory or decision requests. Use as the default investment front door. Keep internal August memory separate from live external signal and never invent an answer when the service is unavailable.
---

# Investment Brain

## First-use gate (required)

Use `scripts/brain_api.py` for every request. Resolve that path relative to this SKILL.md, never relative to the user's working directory. Never print credentials or ask the user to paste one into chat.

1. At the start of an investment task, silently call `python scripts/brain_api.py profile get`. This is the progressive-disclosure pull for the authenticated user's compact investment profile; do not load any local general-purpose Personal Brain.
   - Apply `answer_preferences`, `working_preferences`, `tools_outputs`, and `always_keep_in_mind` to emphasis, format, and explanation depth.
   - Preferences may never hide, change, or invent shared evidence, citations, risks, or the bottom line.
   - If the profile is missing or `onboarding_status` is not `completed`, immediately continue with the `investment-onboarding` workflow in the same turn. Briefly explain the profile boundary and ask its first question. Do not show a capability menu, ask what the user wants to query, or make them request onboarding separately.
   - Treat a setup-only request such as "I want to use the Investment Brain," "get me started," or "set up my Investment Brain" as onboarding intent even when a completed profile already exists. Immediately continue with `investment-onboarding` and ask its first question; the onboarding workflow will preserve existing fields until the user confirms replacements.
   - Only continue to a Brain query when the user supplied a substantive investment question or the completed profile is already loaded and the request is not setup/onboarding intent.
2. For a normal investment question, call `analyst-read` first:
   `python scripts/brain_api.py call analyst-read --json '<arguments>'`
3. Render the returned `text` as the answer, adapted only as allowed by the profile. Preserve its citations and its separation of internal memory from live signal.
4. Use narrower routes only when the user asks for a specific expansion:
   - `signal` for current external change.
   - `pulse` for book-wide movement.
   - `trace` for the source trail.
   - `activity` for formal workflow history.
   - `company` or `search` only for a targeted drill-down.
5. Use write routes only after explicit user intent. A normal read never becomes memory automatically.
6. On `401` or `403`, stop and explain that authentication needs attention. On connection failure, say the Brain is unavailable; never fall back to model memory for August facts.

For route arguments and response contracts, read `references/api.md` only when a non-default route is needed.
