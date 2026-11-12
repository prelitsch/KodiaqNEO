param(
    [ValidateSet('Build','Audit','Test','DesignRehearsal','IconRehearsal','Release')]
    [string]$Mode='Build',
    [string[]]$Changed=@(),
    [string]$PreviousBuild,
    [string]$PythonPath=$env:NEOUI_PYTHON
)
$ErrorActionPreference='Stop'
if ($Mode -eq 'Release') {
    throw 'INSTALLATION RELEASE BLOCKED. Build creates PC-validated offline candidates only; it does not authorize vehicle operations.'
}
if (-not $PythonPath) {
    $localPython=Join-Path $PSScriptRoot 'neoui_workspace/python-path.txt'
    if (Test-Path -LiteralPath $localPython) {
        $configured=(Get-Content -LiteralPath $localPython -Raw).Trim()
        if (Test-Path -LiteralPath $configured -PathType Leaf) { $PythonPath=$configured }
    }
}
if (-not $PythonPath) {
    foreach ($name in @('python','python3','py')) {
        $command=Get-Command $name -ErrorAction SilentlyContinue
        if ($command) { $PythonPath=$command.Source; break }
    }
}
if (-not $PythonPath) { throw 'Python 3.10+ is required. Set NEOUI_PYTHON or pass -PythonPath with the full interpreter path.' }
& $PythonPath -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.10+ interpreter check failed.' }
function Invoke-NeoTool([string]$Name,[string[]]$ToolArgs=@()) {
    & $PythonPath (Join-Path $PSScriptRoot "tools/$Name") @ToolArgs
    if ($LASTEXITCODE -ne 0) { throw "NeoUI tool failed: $Name ($LASTEXITCODE)" }
}
switch ($Mode) {
    'Test' { Invoke-NeoTool 'test_visual_revision.py' }
    'DesignRehearsal' { Invoke-NeoTool 'visual_build.py' }
    'IconRehearsal' { Invoke-NeoTool 'visual_build.py' @('--rehearse-icon') }
    default {
        $arguments=@()
        foreach ($name in $Changed) { $arguments+=@('--changed',$name) }
        if ($PreviousBuild) { $arguments+=@('--previous-build',$PreviousBuild) }
        if ($Mode -eq 'Audit') { $arguments+='--audit' }
        Invoke-NeoTool 'build_visual_revision.py' $arguments
    }
}
Write-Host 'OFFLINE COMPLETE. Original inputs and release policy preserved; no SD or vehicle access.'
