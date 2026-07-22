param([switch]$AllowPersonalInvestments)
$ErrorActionPreference='Stop'
$pluginRoot=Split-Path -Parent $PSScriptRoot
$bundle=Get-Content -Raw (Join-Path $pluginRoot 'bundle.json') | ConvertFrom-Json
$source=Join-Path $pluginRoot 'skills'
$claudePersonal=Join-Path $env:USERPROFILE '.claude\skills'
$codexHome=$env:CODEX_HOME
if([string]::IsNullOrWhiteSpace($codexHome)){$codexHome=Join-Path $env:USERPROFILE '.codex'}
$codex=Join-Path $codexHome 'skills'
$claude=$claudePersonal
$claudeMode='personal skill files'
$pluginId='august-investment-brain@august-investment-brain'
$settingsPath=Join-Path $env:USERPROFILE '.claude\settings.json'
$installedPath=Join-Path $env:USERPROFILE '.claude\plugins\installed_plugins.json'

if((Test-Path $settingsPath) -and (Test-Path $installedPath)){
    try {
        $settings=Get-Content -Raw $settingsPath | ConvertFrom-Json
        $enabled=$settings.enabledPlugins.$pluginId -eq $true
        $installed=Get-Content -Raw $installedPath | ConvertFrom-Json
        $entry=$installed.plugins.$pluginId
        if($enabled -and $entry.installPath){
            $candidate=Join-Path $entry.installPath 'skills'
            if(Test-Path $candidate){
                $claude=$candidate
                $claudeMode='enabled plugin cache'
            }
        }
    } catch {
        Write-Host "WARNING: could not inspect Claude plugin state ($($_.Exception.Message)); checking personal skill files."
    }
}

$failures=@()
foreach($name in $bundle.skills){
    $expected=Join-Path $source "$name\SKILL.md"
    $a=Join-Path $claude "$name\SKILL.md"
    $b=Join-Path $codex "$name\SKILL.md"
    if(-not (Test-Path $expected)){$failures += "$name missing from canonical source"; continue}
    if(-not (Test-Path $a)){$failures += "$name missing from Claude $claudeMode"}
    elseif((Get-FileHash $expected).Hash -ne (Get-FileHash $a).Hash){$failures += "$name differs between source and Claude $claudeMode"}
    if(-not (Test-Path $b)){$failures += "$name missing from Codex personal skill files"}
    elseif((Get-FileHash $expected).Hash -ne (Get-FileHash $b).Hash){$failures += "$name differs between source and Codex"}
    if($claude -ne $claudePersonal -and (Test-Path (Join-Path $claudePersonal $name))){
        $failures += "$name duplicated in Claude personal skills while the plugin is enabled"
    }
}

$retiredRoots=@($claudePersonal,$codex,$claude) | Select-Object -Unique
foreach($name in @($bundle.retired_skills)){
    if(-not $name){continue}
    if($AllowPersonalInvestments -and $name -eq 'investments'){continue}
    foreach($root in $retiredRoots){
        if(Test-Path (Join-Path $root $name)){$failures += "$name still discoverable under $root"}
    }
}

if($failures.Count){$failures | Select-Object -Unique | ForEach-Object {Write-Error $_}; exit 1}
Write-Host "PASS: exactly $($bundle.skills.Count) Investment Brain skills verified (Claude: $claudeMode; Codex: personal skill files)."
