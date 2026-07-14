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
$targets = @(
    @{ Name='Claude'; Root=(Join-Path $env:USERPROFILE '.claude\skills') },
    @{ Name='Codex'; Root=(Join-Path ($env:CODEX_HOME ?? (Join-Path $env:USERPROFILE '.codex')) 'skills') }
)
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

foreach($target in $targets){
    New-Item -ItemType Directory -Force -Path $target.Root | Out-Null
    foreach($name in $bundle.skills){
        if($PreservePersonalInvestments -and $name -eq 'investments' -and (Test-Path (Join-Path $target.Root $name))){
            Write-Host "PRESERVED [$($target.Name)]: investments (personal overlay)"
            continue
        }
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

Write-Host "Installed $($bundle.skills.Count) shared Investment Brain skills into Claude and Codex."
if(Test-Path $backupRoot){Write-Host "Backups: $backupRoot"}
