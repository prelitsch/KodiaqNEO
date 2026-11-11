param([ValidateSet('Audit','DesignRehearsal','IconRehearsal','Release')][string]$Mode='Audit')
$ErrorActionPreference='Stop'
if ($Mode -eq 'Release') { throw 'RELEASE BLOCKED: fresh installed baseline, predecessor-based build and authorized installer workflow are not approved. No deployment output created.' }
function Invoke-NeoTool([string]$Name,[string[]]$ToolArgs=@()) {
    & python (Join-Path $PSScriptRoot "tools/$Name") @ToolArgs
    if ($LASTEXITCODE -ne 0) { throw "NeoUI tool failed: $Name ($LASTEXITCODE)" }
}
Invoke-NeoTool 'reconcile_pipeline.py'
Invoke-NeoTool 'check_media_bt.py'
Invoke-NeoTool 'test_baseline_precheck.py'
Invoke-NeoTool 'test_visual_png.py'
if ($Mode -eq 'DesignRehearsal') { Invoke-NeoTool 'visual_build.py' }
if ($Mode -eq 'IconRehearsal') { Invoke-NeoTool 'visual_build.py' @('--rehearse-icon') }
Invoke-NeoTool 'refresh_verified_reports.py'
Write-Host 'OFFLINE COMPLETE. Existing graphics preserved. Live baseline UNKNOWN. No SD/vehicle access or installation.'
