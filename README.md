# August Investment Brain — skills marketplace

Client-side skills for August Group's Investment Brain: analyst reads over shared
company memory, portfolio pulse and watch, deal screens, diligence workflows, and a
private per-user investment profile.

## What this is (and isn't)

This repository contains **only the client**: skill instructions and a thin
authenticated API script. It holds no investment data, no credentials, and no server
code. All data lives behind August's hosted API, which requires a Microsoft Entra
sign-in from the August tenant **and** per-user allowlisting. Installing these skills
without that access authenticates nothing and returns nothing.

## Install (Claude Code)

```
/plugin marketplace add Cal1234567/August-Investment-Brain
/plugin install august-investment-brain@august-investment-brain
```

Then configure the endpoint (values provided internally; they are standard
public-client identifiers, not secrets — see `plugins/august-investment-brain/HOSTED-AUTH.md`):

```powershell
./plugins/august-investment-brain/scripts/install.ps1 `
  -BrainApiUrl "<provided internally>" `
  -EntraTenantId "<provided internally>" `
  -EntraClientId "<provided internally>" `
  -ApiScope "<provided internally>"
```

First use opens a Microsoft sign-in in your browser. If your account is not
provisioned for the Brain, ask Cal Shannon (cal@augustgroup.com).

## Skills included

See `plugins/august-investment-brain/bundle.json` for the authoritative list:
the analyst front door (investment-brain), onboarding, deal-screen, diligence-next,
diligence comps, pass-patterns, portfolio-pulse, portfolio-watch, red-team,
team-view, what-did-we-know, log-decision, create-brain-skill, and the investments
mode contract.
