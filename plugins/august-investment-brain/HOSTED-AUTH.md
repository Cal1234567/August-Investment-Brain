# Hosted Microsoft Entra authentication

The distributed client is a public/native client. It never contains a client
secret. The first hosted request opens Microsoft's system-browser sign-in so
Conditional Access can evaluate the device. Later requests use silent refresh.

Since 2026-07-14 the hosted defaults (API URL, tenant, client ID, scope) are baked into `skills/investment-brain/scripts/brain_api.py` — a fresh install needs NO configuration. The installer below is only for overriding those defaults (e.g. a test server or local API-key mode):

```powershell
./scripts/install.ps1 `
  -BrainApiUrl "https://<brain-app>/api" `
  -EntraTenantId "<august-tenant-id>" `
  -EntraClientId "<public-client-app-id>" `
  -ApiScope "api://<brain-api-app-id>/access_as_user"
```

Configuration is stored at
`~/.august/investment-brain/config.json`. Environment variables
`BRAIN_API_URL`, `BRAIN_ENTRA_TENANT_ID`, `BRAIN_ENTRA_CLIENT_ID`,
`BRAIN_API_SCOPE`, and `BRAIN_TOKEN_CACHE_FILE` override file values.

`BRAIN_API_KEY` and existing API-key files retain precedence for local pilot
use. Hosted distribution requires the `requirements-client.txt` MSAL package.
