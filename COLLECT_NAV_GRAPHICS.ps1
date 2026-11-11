# NeoUI Navigation Resource Collector v1.0
# READ-ONLY: Copies selected extracted firmware files to a local ZIP. Does not modify car, SD, or firmware.
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceRoot,
    [string]$OutputZip
)
$ErrorActionPreference = 'Stop'

$sourcePath = (Resolve-Path -LiteralPath $SourceRoot).Path
if (Test-Path -LiteralPath (Join-Path $sourcePath 'lba0') -PathType Container) {
    $sourcePath = Join-Path $sourcePath 'lba0'
}
$region = Join-Path $sourcePath 'navigation\resources\app\sk\eu'
if (-not (Test-Path -LiteralPath $region -PathType Container)) {
    throw "European navigation resource folder not found: $region . Check -SourceRoot points to your extracted app50 image."
}
if ([string]::IsNullOrWhiteSpace($OutputZip)) {
    $OutputZip = Join-Path (Split-Path -Path $sourcePath -Parent) 'Kodiaq_NeoUI_Navigation_Research.zip'
}
$OutputZip = [System.IO.Path]::GetFullPath($OutputZip)
if (Test-Path -LiteralPath $OutputZip) {
    throw "Output already exists (not overwriting): $OutputZip . Rename or move the old file."
}

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("NeoUI_nav_" + [guid]::NewGuid().ToString('N'))
$destRegion = Join-Path $tempDir 'navigation\resources\app\vw\eu'
New-Item -ItemType Directory -Path $destRegion -Force | Out-Null
$copied = New-Object System.Collections.Generic.List[string]

function Copy-NavFile([string]$relative) {
    $src = Join-Path $region $relative
    if (-not (Test-Path -LiteralPath $src -PathType Leaf)) { return }
    $dst = Join-Path $destRegion $relative
    $dstFolder = Split-Path -Path $dst -Parent
    New-Item -ItemType Directory -Path $dstFolder -Force | Out-Null
    Copy-Item -LiteralPath $src -Destination $dst
    $copied.Add($relative)
}

try {
    # Map road colours, typography settings and day/night schemas.
    foreach ($sub in @('MapConfigs', 'MapConfigs\1280x640')) {
        $folder = Join-Path $region $sub
        if (Test-Path -LiteralPath $folder -PathType Container) {
            Get-ChildItem -LiteralPath $folder -File | Where-Object {
                $_.Name -like '*.mxf.gz' -or $_.Name -like '*.fcx'
            } | ForEach-Object { Copy-NavFile (Join-Path $sub $_.Name) }
        }
    }
    # Graphic container and resource category mappings for POIs and map markers.
    foreach ($file in @(
        'images.cff', 'resourceConfig.xml', 'amzoomconfig.xml', 'amzoomconfig_1280x640.xml',
        'poi\poi_vw.pc.gz', 'poi\petrol_stations.pc.gz',
        'roadicon\roadicon.ri.gz', 'textures\textures.cff',
        'pcconfig\iconsmappings.xml', 'gui\bitmap.skn',
        'gui\road_name_marker.png', 'gui\Street_Pin_Shadow2D.png',
        'gui\Street_Pin_Shadow3D.png', 'gui\1\road_name_marker.png'
    )) { Copy-NavFile $file }
    if ($copied.Count -eq 0) {
        throw 'No requested navigation resources were found. No ZIP created.'
    }
    $note = @(
        'Kodiaq NeoUI Navigation Research v1.0',
        'Source: extracted firmware app50 image, not live car',
        'Region: eu',
        'Read-only collection. No firmware or map files changed.',
        'Copy count: ' + $copied.Count,
        '',
        'Included relative paths:'
    ) + $copied.ToArray()
    $note | Set-Content -LiteralPath (Join-Path $tempDir 'manifest.txt') -Encoding UTF8
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $OutputZip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
    Write-Host 'NAV RESEARCH PACKAGE READY' -ForegroundColor Green
    Write-Host ('Output: ' + $OutputZip)
    Write-Host ('Copied files: ' + $copied.Count)
    Write-Host 'Original firmware and car are unchanged.'
} finally {
    if (Test-Path -LiteralPath $tempDir) {
        Remove-Item -LiteralPath $tempDir -Recurse -Force
    }
}
