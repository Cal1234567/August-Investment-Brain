param(
    [string]$BrainApiUrl = "",
    [string]$ApiKeyFile = "",
    [string]$EntraTenantId = "",
    [string]$EntraClientId = "",
    [string]$ApiScope = "",
    [switch]$PreservePersonalInvestments
)

$ErrorActionPreference = 'Stop'
$pluginRoot = Split-Path -Parent $PSScriptRoot
$bundle = Get-Content -Raw (Join-Path $pluginRoot 'bundle.json') | ConvertFrom-Json
$sourceRoot = Join-Path $pluginRoot 'skills'
$MarketplaceUrl = 'https://github.com/Cal1234567/August-Investment-Brain.git'
$MarketplaceName = 'august-investment-brain'

# Claude Code gets the skills via the self-updating marketplace PLUGIN, not raw
# file copies (Cal, 2026-07-17: no one does manual updates). Raw copies into
# ~/.claude/skills never update and shadow the plugin's versions. Codex has no
# plugin system, so it still receives file copies below.
$claudeViaPlugin = $false
$claudeCli = Get-Command claude -ErrorAction SilentlyContinue
if($claudeCli){
    try {
        & $claudeCli.Source plugin marketplace add $MarketplaceUrl 2>&1 | Out-Null
    } catch {}
    try {
        & $claudeCli.Source plugin install "$MarketplaceName@$MarketplaceName" 2>&1 | Out-Null
    } catch {}
    $kmPath = Join-Path $env:USERPROFILE '.claude\plugins\known_marketplaces.json'
    if(Test-Path $kmPath){
        try {
            $km = Get-Content -Raw $kmPath | ConvertFrom-Json
            if($km.$MarketplaceName){
                $km.$MarketplaceName | Add-Member -NotePropertyName autoUpdate -NotePropertyValue $true -Force
                $km | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $kmPath -Encoding utf8NoBOM
                $claudeViaPlugin = $true
                Write-Host "PLUGIN [Claude]: marketplace registered with auto-update ON (no manual updates needed)"
            }
        } catch {
            Write-Host "WARNING: could not enable auto-update ($($_.Exception.Message)); falling back to file copies."
        }
    }
}
if(-not $claudeViaPlugin){
    Write-Host "NOTE [Claude]: plugin route unavailable; installing file copies (these update only when this script re-runs)."
}

$targets = @(
    @{ Name='Codex'; Root=(Join-Path ($env:CODEX_HOME ?? (Join-Path $env:USERPROFILE '.codex')) 'skills') }
)
if(-not $claudeViaPlugin){
    $targets = @(@{ Name='Claude'; Root=(Join-Path $env:USERPROFILE '.claude\skills') }) + $targets
}
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupRoot = Join-Path $env:USERPROFILE ".august\investment-brain\backups\$stamp"

$entraRequested = $EntraTenantId -or $EntraClientId -or $ApiScope
if($entraRequested -and (-not $EntraTenantId -or -not $EntraClientId -or -not $ApiScope)){
    throw "Hosted authentication requires -EntraTenantId, -EntraClientId, and -ApiScope together."
}
if($entraRequested){
    $python = Get-Command python -ErrorAction SilentlyContinue
    if(-not $python){throw "Python is required to install the Investment Brain client."}
    & $python.Source -c "import msal" 2>$null
    if($LASTEXITCODE -ne 0){
        Write-Host "Installing Microsoft Entra authentication dependency (MSAL)..."
        & $python.Source -m pip install --user --disable-pip-version-check -r (Join-Path $pluginRoot 'requirements-client.txt')
        if($LASTEXITCODE -ne 0){
            throw "Could not install MSAL. Run: python -m pip install --user 'msal>=1.31,<2'"
        }
    }
}

# Migration: earlier installs copied skills into ~/.claude/skills as raw files.
# Once the plugin owns them, those copies shadow the plugin's versions and never
# update — back them up and remove them.
if($claudeViaPlugin){
    $claudeSkillsRoot = Join-Path $env:USERPROFILE '.claude\skills'
    foreach($name in (@($bundle.skills) + @($bundle.retired_skills))){
        if(-not $name){continue}
        if($PreservePersonalInvestments -and $name -eq 'investments'){continue}
        $stale = Join-Path $claudeSkillsRoot $name
        if(Test-Path $stale){
            $backup = Join-Path $backupRoot "Claude\$name"
            New-Item -ItemType Directory -Force -Path (Split-Path $backup) | Out-Null
            Copy-Item -LiteralPath $stale -Destination $backup -Recurse -Force
            Remove-Item -LiteralPath $stale -Recurse -Force
            Write-Host "MIGRATED [Claude]: $name (raw copy removed; plugin owns it now)"
        }
    }
}

foreach($target in $targets){
    New-Item -ItemType Directory -Force -Path $target.Root | Out-Null
    foreach($name in $bundle.skills){
        $source = Join-Path $sourceRoot $name
        $destination = Join-Path $target.Root $name
        if(-not (Test-Path (Join-Path $source 'SKILL.md'))){throw "Missing bundled skill: $name"}
        if(Test-Path $destination){
            $backup = Join-Path $backupRoot "$($target.Name)\$name"
            New-Item -ItemType Directory -Force -Path (Split-Path $backup) | Out-Null
            Copy-Item -LiteralPath $destination -Destination $backup -Recurse -Force
            Remove-Item -LiteralPath $destination -Recurse -Force
        }
        Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force
        Write-Host "INSTALLED [$($target.Name)]: $name"
    }
    foreach($name in @($bundle.retired_skills)){
        if(-not $name){continue}
        if($PreservePersonalInvestments -and $name -eq 'investments'){
            Write-Host "PRESERVED [$($target.Name)]: investments (personal overlay; not retired)"
            continue
        }
        $stale = Join-Path $target.Root $name
        if(Test-Path $stale){
            $backup = Join-Path $backupRoot "$($target.Name)\$name"
            New-Item -ItemType Directory -Force -Path (Split-Path $backup) | Out-Null
            Copy-Item -LiteralPath $stale -Destination $backup -Recurse -Force
            Remove-Item -LiteralPath $stale -Recurse -Force
            Write-Host "RETIRED [$($target.Name)]: $name (folded into investment-brain)"
        }
    }
}

if($BrainApiUrl -or $ApiKeyFile -or $entraRequested){
    $configDir = Join-Path $env:USERPROFILE '.august\investment-brain'
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    $configPath = Join-Path $configDir 'config.json'
    $existing = if(Test-Path $configPath){Get-Content -Raw $configPath | ConvertFrom-Json}else{[pscustomobject]@{}}
    $config = [ordered]@{
        base_url = if($BrainApiUrl){$BrainApiUrl.TrimEnd('/')}else{$existing.base_url}
        api_key_file = if($ApiKeyFile){[IO.Path]::GetFullPath($ApiKeyFile)}else{$existing.api_key_file}
        tenant_id = if($EntraTenantId){$EntraTenantId}else{$existing.tenant_id}
        client_id = if($EntraClientId){$EntraClientId}else{$existing.client_id}
        api_scope = if($ApiScope){$ApiScope}else{$existing.api_scope}
    }
    if($ApiKeyFile -and -not (Test-Path -LiteralPath $config.api_key_file)){throw "API key file does not exist: $($config.api_key_file)"}
    $config | ConvertTo-Json | Set-Content -LiteralPath $configPath -Encoding utf8NoBOM
    Write-Host "CONFIGURED: $configPath"
}

if($claudeViaPlugin){
    Write-Host "Claude: skills served by the auto-updating plugin. Codex: $($bundle.skills.Count) skills installed as files."
} else {
    Write-Host "Installed $($bundle.skills.Count) shared Investment Brain skills into Claude and Codex."
}
if(Test-Path $backupRoot){Write-Host "Backups: $backupRoot"}
