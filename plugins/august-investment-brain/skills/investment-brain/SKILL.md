---
name: investment-brain
description: Query the shared August Investment Brain through its authenticated REST API. Use automatically whenever the conversation touches August's portfolio, book, deals, funds, or diligence — even when the user does not name the Brain and even when other portfolio or memory skills also match; this skill wins for August firm questions. Covers company and fund reads, deal screens, red teams, team views, pass patterns, portfolio pulse and watch, point-in-time "what did we know", diligence next steps, prior-diligence comps, source traces, Activity, and explicit memory or decision requests. Defer to the user's personal memory systems for personal, non-August questions. Keep internal August memory separate from live external signal and never invent an answer when the service is unavailable.
---

# Investment Brain

The server owns intent routing, retrieval, evidence separation, and the output standard. Your job is thin: authenticate, pass the user's question through, render the answer faithfully.

## First-use gate (required)

Use `scripts/brain_api.py` for every request. Resolve that path relative to this SKILL.md, never relative to the user's working directory. Never print credentials or ask the user to paste one into chat. If a call fails because MSAL is missing, run `python -m pip install --user "msal>=1.31,<2"` yourself and retry once.

1. At the start of an investment task, silently call `python scripts/brain_api.py profile get`. This is the progressive-disclosure pull for the authenticated user's compact investment profile; do not load any local general-purpose Personal Brain.
   - Apply `answer_preferences`, `working_preferences`, `tools_outputs`, and `always_keep_in_mind` to emphasis, format, and explanation depth. Preferences may never hide, change, or invent shared evidence, citations, risks, or the bottom line.
   - If the profile is missing or `onboarding_status` is not `completed`, immediately continue with the `investment-onboarding` workflow in the same turn. Briefly explain the profile boundary and ask its first question. Do not show a capability menu, ask what the user wants to query, or make them request onboarding separately.
   - Treat a setup-only request such as "I want to use the Investment Brain," "get me started," or "set up my Investment Brain" as onboarding intent even when a completed profile already exists. Immediately continue with `investment-onboarding` and ask its first question; the onboarding workflow will preserve existing fields until the user confirms replacements.

## Answering

2. For any investment question, call `analyst-read` with the user's ask, close to verbatim:
   `python scripts/brain_api.py call analyst-read --json '<arguments>'`
3. Render the returned `text` as the answer, adapted only as allowed by the profile. Preserve its citations and its separation of internal memory from live signal.
4. Named workflows are the same single `analyst-read` call — just phrase the question so the server routes it:
   - **Deal screen** (screen / triage / first look at a new company): include the exact phrase "deal screen" and name the target; ask for a neutral screen against active and passed August memory.
   - **Red team** (bear case / argue the pass): ask for the strongest August-specific pass case against the named deal.
   - **Team view** (where does everyone stand): one company; ask for attributed team views, shared ground, and cruxes.
   - **Pass patterns** (why do we pass / what kills our deals): ask for cited recurring patterns from passed-deal memory, applied to the named opportunity if one is given.
   - **What did we know** (decision calibration): requires a company and a past date; ask the full point-in-time question ("what did we know about X as of <month year>").
   - **Diligence next** (what should we chase): name the company; ask for the ranked next diligence actions.
   - **Diligence comps** (does this rhyme with the book): name the target; ask for the strongest August diligence parallels.
   - **Portfolio watch** (what changed / thesis drift for one company): ask a what-changed question for the company and window.
   - **Portfolio pulse** (book-wide digest): use the `pulse` route with the requested window instead of `analyst-read`.
5. Use narrower routes only when the user asks for a specific expansion: `signal` for current external change, `trace` for the source trail, `activity` for formal workflow history, `company` or `search` for a targeted drill-down. For route arguments and response contracts, read `references/api.md` only when a non-default route is needed.
6. Use write routes only after explicit user intent. A normal read never becomes memory automatically.
   - If the user disputes or corrects an answer, re-verify against sources (`search`, `trace`) and offer once to log it with `brain-feedback` so the underlying data gets repaired.
7. On `401` or `403`, stop and explain that authentication needs attention. On connection failure, say the Brain is unavailable; never fall back to model memory for August facts.
