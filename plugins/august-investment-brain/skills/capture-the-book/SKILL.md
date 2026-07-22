---
name: capture-the-book
description: Run a posed-inference interview session that harvests August's DIRECTS house style, deal instincts, and blindspots from a senior investor (built for the head of directs) into attributed Brain memory. Directs and passed directs only — never the funds side. Use whenever a long-tenured August teammate wants to "run the book interview", "do a capture session", "put my knowledge in the Brain", "review what the Brain thinks about how we invest", or when Cal asks to prep or continue a capture-the-book session for his boss or another expert. The skill mines the corpus for falsifiable pattern inferences, poses them one at a time for CONFIRM / CORRECT / REJECT, and logs every response as attributed decision memory. Distinct from investment-onboarding (profile setup), log-decision (one-off decision capture), and investment-brain (Q&A). Requires the sibling investment-brain skill's authenticated API client.
---

# Capture the Book — posed-inference knowledge harvest

Goal: move the house style out of a senior investor's head into attributed, queryable
Brain memory — what August likes, what kills deals, and where the blindspots are.
The Brain holds documents; he holds judgment. This skill converts judgment into data.

**Scope: DIRECTS ONLY (Cal, 2026-07-22).** The expert user is the head of directs.
Mine, infer, and interview exclusively on direct positions and passed directs —
never fund commitments, fund managers, or the funds side of the book. In retrieval
this means preferring per-company direct reads and filtering out fund-bucket
results (". AEF", ". New Lane", ". MA & LF", ". Approved Fund Investments",
fund-typed companies); an inference must never cite fund evidence.

## First-use gate (required)

Run the `investment-brain` first-use gate before anything else: silently
`python ../investment-brain/scripts/brain_api.py profile get` (resolve relative to
this SKILL.md). If the profile is missing or `onboarding_status` is not
`completed`, continue with the `investment-onboarding` workflow in the same turn
and start the capture session only after it completes. Attribution for every
logged answer derives from this authentication — never write a name into
attribution fields.

## The one rule (Cal's design law, 2026-07-22 — non-negotiable)

**Every prompt is a posed inference. Never an open-ended question.**

Form (Cal, 2026-07-22 — the ASK comes first, so it never reads as a statement):
1. Open with the question, explicitly: "**True or false: [claim]?**"
2. Then the evidence: "The Brain thinks this because [N deals / memo language /
   named documents]."
3. Then the confidence level.
4. Close with the response ask: "Confirm, correct, or reject?"
Never bury the question after the evidence; he should know what he's judging
before he hears the case for it.

He responds one of three ways. CONFIRM / CORRECT / REJECT are intent categories
you classify from natural speech, NOT words he must say — never make him learn a
vocabulary, and never ask him to rephrase into the categories. "ya", "ye", "yep",
"sure", "that's right", a thumbs-up = CONFIRM. "no", "nah", "not really", "eh,
kind of but..." = CORRECT or REJECT by content. Classify by what his answer DOES
to the claim:
- **CONFIRM** — he agrees, in any words. Logged as validated house style.
- **CORRECT** — he agrees partly or replaces the claim with his own version. The
  gold. Log HIS version, not the inference.
- **REJECT** — he throws the whole claim out. Log the rejection; a wrong inference
  the Brain believed is a documented blindspot in the Brain's own model.
Only if you genuinely cannot classify from his words do you use the one posed
restatement allowed by the follow-up logic below.

Corrections and rejections are worth more than confirmations. Do not soften
inferences to make them agreeable; a sharp almost-right claim extracts more nuance
than a safe one.

**Language rule (Cal, 2026-07-22): plain and simple, zero detail sacrificed.** The
expert's job is to think about the CLAIM, so the wording must never make him think
about the sentence. Short sentences. No analyst jargon, no stacked clauses, no
parenthetical asides. Say "we passed on X because Y" not "the pass rationale
reflects Y-driven considerations." Every fact stays; the packaging gets simple. Banned: "which pass are you proudest of?", "what do we look for?",
or any question a blank page could receive. Open-ended prompts only when strictly
unavoidable, which is approximately never.

## Session flow

### 1. Prep (silent, before he sees anything)
Authenticate via the sibling client: `python ../investment-brain/scripts/brain_api.py profile get`
(resolve relative to this SKILL.md).

**The opening set is CURATED, not generated (Cal, 2026-07-22).** Fetch the bank
from Brain memory — NEVER from any bundled file (the bank contains confidential
deal intelligence and lives only behind the authenticated API):
`call search --json '{"kind": "insights", "query": "capture-the-book inference bank curated session", "limit": 3}'`
Use the newest row whose text starts "CAPTURE-THE-BOOK INFERENCE BANK" (highest
rev wins). Pose its inferences VERBATIM, in order. If no bank row is found, STOP
and say the bank is missing — never improvise questions in its place. Before
starting, search Brain memory (theme=house_style) for prior session logs and skip
any inference already settled. What IS dynamic:
- **Follow-ups inside the session** — governed by ONE test, applied after every
  response: *can you already write the one-sentence "Standing rule" line of the
  log?* If yes → log it and move to the next inference. If no → ask exactly one
  follow-up to pin it down, then re-apply the test. Hard cap: TWO follow-ups per
  inference, then log the best standing rule you have and move on regardless.
  Every follow-up must itself be a posed claim, never open-ended.
  By response type, this works out to:
  - **CONFIRM, nothing added** → standing rule = the inference. Log, next. Never
    follow up on a plain confirm.
  - **CONFIRM + new nuance** ("exactly — and also...") → if the nuance changes the
    rule, one follow-up to pin it ("so the rule is X plus Y — right?"); else log
    and move on.
  - **CORRECT** → always one follow-up: restate HIS version as a claim ("so the
    rule is actually X — right?"). A second only if his correction exposed a
    boundary still fuzzy ("does that hold for the Z case too?").
  - **REJECT** → one follow-up posing the most likely replacement claim ("then
    what's true instead is Y — right?"). If he already gave the replacement,
    restate-to-pin instead.
  - **Ambiguous response** (can't tell which of the three it was) → one posed
    restatement to classify it; this counts against the cap.
- **Future banks** — when the current bank is exhausted, draft the next 8-10 from
  the updated corpus (including his logged answers) using the retrieval mechanics
  below, and give the DRAFT to Cal for review before any session uses it. New
  inferences never reach the expert unreviewed.

Verified retrieval mechanics (smoke-tested 2026-07-22 — use these, not the dead ends):
- **Passed-book roster**: `call search` with `{"kind": "claims", "query": "<theme>", "status": "passed", "limit": ...}` — status-filtered search enumerates passed
  names with their claims. Sweep several themes (business model, valuation, team,
  traction) to build the roster + per-company texture.
- **Dead end — do not use**: book-wide "why do we pass" questions through
  `analyst-read` route to the ACTIVE-portfolio scope, which excludes passed names
  by design. Pass-pattern asks work per-company, not book-wide.
- **The reasons gap is the premise**: most pass REASONS are not in the corpus (the
  corpus holds other firms' criteria, not August's). So inferences come from the
  SHAPE of the book — stage/sector/structure distributions of passed vs. active
  names, memo risk-language on actives, and the few recorded decision insights
  (where they exist). An inference built on shape
  ("we passed on every X except Y") is exactly the falsifiable kind this skill
  wants; state the evidence as counts of names, never invented reasons.

Generate **12-18 inferences** per session, each: specific, falsifiable,
evidence-cited, spanning these lenses —
- what August likes (proof points that recur before a yes)
- what kills deals (the real reasons, not the stated ones)
- sizing and structure instincts (SPVs, checks, follow-ons)
- sector and stage tilts
- process habits (who drives, what gets diligenced hardest, what gets skipped)
- inferred blindspots, ALSO posed as inferences ("the Brain finds no case where
  August passed on valuation alone — is price never the killer, or is that a hole
  in the record?")

Number them. Order hardest-to-agree-with first — his energy is highest early.

### 2. The session (~45 minutes, his pace)
Present one inference at a time: claim, evidence line, confidence. Take his
CONFIRM / CORRECT / REJECT plus whatever nuance he adds. Push back once if a
correction seems to contradict the evidence ("the record shows 3 counterexamples —
reconcile?") — reconciliation is where the deepest nuance lives. Then move on;
never relitigate.

**Log immediately after each response** — never batch to session end (a dropped
session loses everything). Use the sibling client:
`call memory --json '{"action": "save_insight", "source_type": "decision", "theme": "house_style", "company": "<company or omit>", "text": "<see logging format>"}'`
The server derives attribution from his authentication — never write a name into
attribution fields.

Logging format (one insight per response):
"HOUSE STYLE [CONFIRMED|CORRECTED|REJECTED] (capture-the-book session <date>):
Inference posed: <the claim + its evidence line>. Expert response: <his words,
close to verbatim>. Standing rule: <the one-sentence version the Brain should
carry forward>."

### 3. Backlog drip (strictly one per session)
End with exactly ONE per-company history question, posed as inference where
possible: "the Brain has no pass reason on file for <X> — its best inference from
the folder is <Y>. Right?" Log via the same route with the company set. Never
extend the drip past one; the backlog fills over months, not per session.

### 4. Close
- Report his correction rate (corrections+rejections / total). Tell him what it
  means: a falling rate across sessions = the Brain's model of the house converging
  on the real one. That number is the skill's health metric — record it in the
  session's final logged insight (theme: house_style, no company).
- Offer (don't push) a next session; note which lenses went uncovered.

## Boundaries
- Never write to Brain memory except through the attributed save_insight route
  shown above; never fabricate evidence counts — every inference's evidence line
  must come from actual retrieval this session.
- If retrieval is too thin to pose a defensible inference on some lens, skip the
  lens and say so in the close; do not pad with soft questions.
- His corrections overwrite nothing automatically — they land as new attributed
  insights; reconciling contradictions with existing memory is a later, human call.
- On auth failure or API unavailability: stop and say so. No offline mode.
