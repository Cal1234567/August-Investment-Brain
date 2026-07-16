---
name: create-brain-skill
description: Create a teammate-owned Investment Brain skill that uses August's authenticated Azure-hosted service. Use when someone asks to make, fork, customize, or productize an investment workflow that should reuse shared company evidence, organization context, source traces, Activity, live external signal, or the authenticated user's investment profile.
---

# Create Brain Skill

## First-use gate (required)

Run the `investment-brain` first-use gate before designing or testing: silently `python ../investment-brain/scripts/brain_api.py profile get`; if the profile is missing or incomplete, continue with `investment-onboarding` in the same turn and resume only after it completes.

## Build the skill

1. Turn the request into one concrete example: what the user says, what hosted Brain evidence it needs, and what the answer should look like. Ask one short question only when that cannot be inferred.
2. Read `references/design-patterns.md`. Choose the narrowest safe hosted route; default to `analyst-read` for investment questions.
3. Read the closest sibling skill only when it materially helps. Reuse its workflow shape, not its name or prose.
4. Choose a short hyphen-case name and a trigger-rich description. Do not use `investment-brain`, `investment-onboarding`, or the name of an existing installed skill.
5. Run `scripts/scaffold_brain_skill.py` relative to this SKILL.md. Install to both Claude and Codex unless the user names only one surface. For example:

   `python scripts/scaffold_brain_skill.py portfolio-concentration-check --description "Check portfolio concentration against August's shared investment memory. Use for concentration review, exposure overlap, or portfolio clustering." --workflow "Identify the strongest shared exposures, cite the supporting August evidence, and end with the top concentration questions." --route analyst-read --platform both`

6. Open each generated `SKILL.md` and tighten the workflow for the user's exact inputs, route arguments, and output contract. Keep it concise. Preserve the generated first-use gate and security boundaries.
7. Validate the skill folder with the available skill validator. Then run a harmless authenticated read when practical. Never test a write route against production unless the user explicitly asked for that write.

## Required boundaries

- Use the sibling `investment-brain/scripts/brain_api.py` client for every hosted request. Never connect to Azure Postgres, Key Vault, or internal server modules from a custom skill.
- Treat the hosted API as the product boundary. A generated skill may use only routes exposed to that authenticated user.
- Load the authenticated User Memory Profile first. It may shape format and emphasis, but never alter shared evidence or citations.
- Keep internal August memory separate from live external signal.
- Default reads to `analyst-read`. Use `company`, `search`, `signal`, `pulse`, `trace`, or `activity` only when the workflow specifically earns them.
- Generate a `memory` route only for an explicit user-directed save workflow and pass `--write`. The generated skill must reconfirm intent at execution time and must never retry an uncertain write.
- Stop cleanly on authentication, authorization, or connection failure. Never fall back to model memory for August facts.

## Handoff

Report the new skill name, where it was installed, its trigger examples, and the hosted route it uses. Say plainly when a requested capability is not exposed by the hosted API.