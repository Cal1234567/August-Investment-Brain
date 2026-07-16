# August Investment Brain — skills marketplace

> **Generated repo — do not edit here.** The plugin is edited in the private investment-brain monorepo (distribution/plugins/august-investment-brain) and synced with distribution/sync-channel.ps1. Direct edits will be overwritten by the next sync.

Client-side skills for August Group's Investment Brain: analyst reads over shared
company memory, portfolio pulse and watch, deal screens, diligence workflows, and a
private per-user investment profile.

## What this is (and isn't)

This repository contains **only the client**: skill instructions and a thin
authenticated API script. It holds no investment data, no credentials, and no server
code. The connection identifiers baked into the client are Microsoft public-client
values (designed to ship inside distributed apps); they grant nothing by themselves.
All data lives behind August's hosted API, which requires a Microsoft Entra sign-in
from the August tenant **and** per-user allowlisting. Installing these skills without
that access authenticates nothing and returns nothing.

## Install (Claude Code)

```
/plugin marketplace add Cal1234567/August-Investment-Brain
/plugin install august-investment-brain@august-investment-brain
```

No configuration needed. Ask any investment question (e.g. "what are our active
directs"); a Microsoft sign-in opens in your browser on first use. Sign in with your
August account. If your account is not provisioned for the Brain, ask
Cal Shannon (cal@augustgroup.com).

If sign-in reports a missing MSAL package, run:
`python -m pip install --user "msal>=1.31,<2"`

Advanced: environment variables (`BRAIN_API_URL`, `BRAIN_ENTRA_TENANT_ID`,
`BRAIN_ENTRA_CLIENT_ID`, `BRAIN_API_SCOPE`) or `~/.august/investment-brain/config.json`
override the baked-in defaults — see `plugins/august-investment-brain/HOSTED-AUTH.md`.

## Skills included

See `plugins/august-investment-brain/bundle.json` for the authoritative list:
the analyst front door (investment-brain), onboarding, deal-screen, diligence-next,
diligence comps, pass-patterns, portfolio-pulse, portfolio-watch, red-team,
team-view, what-did-we-know, log-decision, create-brain-skill, and the investments
mode contract.
