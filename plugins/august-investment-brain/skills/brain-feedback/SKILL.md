---
name: brain-feedback
description: Log feedback on an August Investment Brain answer — a wrong figure, wrong fact, missing or stale information, a bad source, or formatting — into the Brain's shared triage queue. Use when the user disputes, corrects, or flags a Brain answer, says "that figure is wrong", "the Brain is off here", "flag this", "report this answer", or "give the Brain feedback". Logging feedback never changes Brain memory; it queues a repair for review.
---

# Brain feedback

## First-use gate (required)

Run the `investment-brain` first-use gate before anything else: silently `python ../investment-brain/scripts/brain_api.py profile get`; if the profile is missing or incomplete, continue with `investment-onboarding` in the same turn and resume only after it completes.

## Workflow

1. Gather from the conversation — ask only for what is genuinely missing:
   - the disputed or deficient part of the answer, quoted (`answer_excerpt`),
   - what the user says is wrong or missing, with their correction or evidence if given (`feedback`),
   - the company and the original question, when known.
2. Pick `kind`: `wrong_figure`, `wrong_fact`, `missing`, `stale`, `wrong_source`, `formatting`, or `other`.
3. Submit one call:
   `python ../investment-brain/scripts/brain_api.py call feedback --json '{"company": "...", "question": "...", "answer_excerpt": "...", "feedback": "...", "kind": "..."}'`
   Do not supply attribution fields; the server derives the submitter from authentication.
4. Report the returned confirmation plainly. Make clear the feedback is queued for triage — it does not change Brain memory or future answers until a repair is reviewed and applied.
5. If the user also wants the right answer now, continue with `investment-brain` to re-verify against sources — feedback and re-verification are separate steps.

Never log feedback the user did not express, never retry an uncertain write automatically, and never present logging feedback as having fixed the underlying data.
