param([switch]$AllowPersonalInvestments)
$ErrorActionPreference='Stop'
$pluginRoot=Split-Path -Parent $PSScriptRoot
$bundle=Get-Content -Raw (Join-Path $pluginRoot 'bundle.json') | ConvertFrom-Json
$claude=Join-Path $env:USERPROFILE '.claude\skills'
$codex=Join-Path ($env:CODEX_HOME ?? (Join-Path $env:USERPROFILE '.codex')) 'skills'
$failures=@()
foreach($name in $bundle.skills){
    $a=Join-Path $claude "$name\SKILL.md"
    $b=Join-Path $codex "$name\SKILL.md"
    if(-not (Test-Path $a) -or -not (Test-Path $b)){$failures += "$name missing"; continue}
    if((Get-FileHash $a).Hash -ne (Get-FileHash $b).Hash){$failures += "$name differs between platforms"}
}
if($failures.Count){$failures | ForEach-Object {Write-Error $_}; exit 1}
Write-Host "PASS: $($bundle.skills.Count) Investment Brain skills available across Claude and Codex."
