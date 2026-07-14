# Hosted Brain skill design patterns

## Choose the route

| User workflow | Route | Rule |
|---|---|---|
| Company, deal, fund, diligence, thesis, risk, prior-view, or comparison question | `analyst-read` | Default front door. Put the complete analytical request in `question`; include `company` only when useful. |
| Recent external change for one company | `signal` | Keep live evidence separate from August memory. |
| Book-wide recent movement | `pulse` | Use for portfolio-wide time-window scans. |
| Evidence behind a prior formal answer | `trace` | Expand the preceding answer; do not invent a trace identifier. |
| Formal Brain workflow history | `activity` | Activity is what ran, not conversation history or saved memory. |
| One targeted Company Memory expansion | `company` | Use only when the workflow needs a specific expansion beyond the front door. |
| Narrow proof or debug lookup | `search` | Keep support/debug mechanics out of the user-facing answer. |
| Explicit save from a user-approved action | `memory` | Require `--write`; reconfirm intent and never retry an uncertain write. |

## Generated skill contract

Every custom skill must:

1. Run `python ../investment-brain/scripts/brain_api.py profile get` before its workflow.
2. Continue into `investment-onboarding` when the authenticated profile is missing or incomplete.
3. Call the hosted client with `python ../investment-brain/scripts/brain_api.py call <route> --json '<arguments>'`.
4. Render the returned `text`, preserving citations and the separation between internal memory and live external signal.
5. Stop on `401`, `403`, or connection failure. It must not substitute model knowledge for August evidence.
6. Avoid direct database, Azure Key Vault, server-code, local Personal Brain, or credential access.

## Good workflow examples

- "Make a customer-reference checker" becomes a read skill using `analyst-read`, with a company input and an output contract that distinguishes stored reference evidence from open diligence gaps.
- "Make a weekly portfolio movers skill" becomes a `pulse` skill with a requested time window and a concise mover/no-mover format.
- "Make a skill that saves our decision" becomes a `memory` skill only after the user confirms it is an explicit write workflow; the generated skill records only user-directed content.

## What custom skills cannot do

A custom skill does not receive unrestricted access to every database table. It composes the authenticated capabilities the hosted API exposes. Admin ingestion, schema changes, raw credentials, and server maintenance remain outside the teammate skill boundary unless August deliberately publishes a separate authorized route.