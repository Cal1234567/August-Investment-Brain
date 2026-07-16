# Investment Brain API

All routes are under the configured `/api` base and require authenticated bearer credentials.

- `POST /analyst-read` — `{question, company?, days?, start_date?, end_date?}`
- `POST /signal` — live external change for one company
- `POST /pulse` — book-wide movement
- `POST /trace` — source trail for the preceding formal answer
- `POST /activity` — formal workflow history
- `POST /company` — targeted Company Memory expansion
- `POST /search` — narrow proof/debug search. REQUIRES `kind`: one of `chunks`, `claims`, `atoms`, `insights`, `overlaps`, `x` (plus `query`, `company?`, `limit?`). A missing `kind` is a 400, a disallowed one a 403 — neither is an authentication problem.
- `POST /memory` — explicit approved memory or investment write
- `POST /feedback` — log user feedback on an answer into the triage queue: `{feedback, kind?, company?, question?, answer_excerpt?}`; `GET /feedback` lists the caller's own submissions. Never a memory write.
- `GET /me/profile` — authenticated user's investment working profile
- `POST /me/onboarding` — complete the authenticated user's onboarding
- `PATCH /me/profile` — update only supplied fields on the authenticated user's profile

Normal workflow responses are `{ok, tool, text}`. Profile responses are `{ok, profile, text}`. The server derives profile identity from authentication; never include a principal or user ID in profile payloads.
