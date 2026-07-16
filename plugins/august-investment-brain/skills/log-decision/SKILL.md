---
name: log-decision
description: Capture an explicit August investment decision, pass, investment, sizing call, or view change in the shared Brain. Use only when the user clearly asks to log, journal, save, or remember a durable investment judgment. Never trigger from ordinary discussion or model-generated conclusions.
---

# Log decision

## First-use gate (required)

Run the `investment-brain` first-use gate before anything else: silently `python ../investment-brain/scripts/brain_api.py profile get`; if the profile is missing or incomplete, continue with `investment-onboarding` in the same turn and resume only after it completes.

Extract a compact, self-contained decision statement naming the subject, decision, rationale, date context, and what would change the view. Reflect it once for confirmation when any material field is uncertain.

After explicit user intent, use the sibling `investment-brain` API client and call `memory` with `action=save_insight`, `source_type=decision`, and the relevant company/theme. Do not supply attribution fields; the server derives the actor from authentication. Report success or failure plainly and never retry an uncertain write automatically.
