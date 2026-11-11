param([switch]$ForceReportRefresh)
$ErrorActionPreference = 'Stop'
$Here = $PSScriptRoot
$Project = Split-Path -Parent $Here
$Root = Split-Path -Parent $Project
. (Join-Path $Here 'rebase_mcf_helpers.ps1')
$Policy = Get-Content (Join-Path $Project 'release-policy.json') -Raw | ConvertFrom-Json
$Changeset = Get-Content (Join-Path $Project 'changesets\v3-design-54.json') -Raw | ConvertFrom-Json
$Build = Get-Content (Join-Path $Project 'neoui_reports\VERIFIED_MEDIA_BT_BUILD.json') -Raw | ConvertFrom-Json
$V1Path = Join-Path $Project 'neoui_workspace\asset_dump\skin3_neoui_v1_payload.mcf'
$V2Path = Join-Path $Project 'neoui_workspace\asset_dump\skin3_neoui_v2_pilot.mcf'
$DesignPath = Join-Path $Project 'neoui_build\NeoUI_v3_MEDIA_BT_skin3.mcf'
$OutPath = Join-Path $Project 'neoui_build\NeoUI_v3_v2_based_candidate.mcf'
$RestorePath = Join-Path $Project 'neoui_build\NeoUI_v3_v2_restore_rehearsal.mcf'
$ReportPath = Join-Path $Project 'neoui_reports\V2_BASED_BUILD.json'

$v1Bytes = [IO.File]::ReadAllBytes($V1Path)
$v2Bytes = [IO.File]::ReadAllBytes($V2Path)
$designBytes = [IO.File]::ReadAllBytes($DesignPath)
$v1Info = Get-McfIdentity $v1Bytes
$v2Info = Get-McfIdentity $v2Bytes
$designInfo = Get-McfIdentity $designBytes
if ($v1Info.sha1 -ne $Policy.known_reference_states.neoui_v1.sha1 -or $v1Info.sha256 -ne $Policy.known_reference_states.neoui_v1.sha256) { throw 'v1 reference hash mismatch' }
if ($v2Info.sha1 -ne $Policy.known_reference_states.neoui_v2_pilot.sha1 -or $v2Info.sha256 -ne $Policy.known_reference_states.neoui_v2_pilot.sha256) { throw 'v2 reference hash mismatch' }
if ($designInfo.sha256 -ne $Build.candidate_sha256 -or $designInfo.sha256 -ne $Changeset.target.sha256) { throw 'v3 design reference hash mismatch' }
$v1 = Read-McfBytes $v1Bytes
$v2 = Read-McfBytes $v2Bytes
$design = Read-McfBytes $designBytes
if ($v1.Rows.Count -ne 2345 -or $v2.Rows.Count -ne 2345 -or $design.Rows.Count -ne 2345) { throw 'unexpected MCF record count' }
if ($v1.Rows.Count -ne $v2.Rows.Count -or $v1.Rows.Count -ne $design.Rows.Count) { throw 'container record counts differ' }
for ($n = 0; $n -lt $v1.Rows.Count; $n++) {
    if ($v1.Rows[$n].Id -ne $v2.Rows[$n].Id -or $v1.Rows[$n].Id -ne $design.Rows[$n].Id) { throw 'MCF record ID/order mismatch' }
}
$targetIds = [Collections.Generic.HashSet[int]]::new()
$replacements = @{}
foreach ($entry in $Changeset.changes) {
    $id = [int]$entry.mcf_id
    if (-not $targetIds.Add($id)) { throw "duplicate design target $id" }
    $before = $v1.ById[$id]
    $base = $v2.ById[$id]
    $after = $design.ById[$id]
    if (-not $before -or -not $base -or -not $after) { throw "missing record $id" }
    if ((Get-Sha256 $before.Record) -ne $entry.source_record_sha256) { throw "v1 source record mismatch for $id" }
    if ((Get-Sha256 $base.Record) -ne $entry.source_record_sha256) { throw "v2 target differs from reviewed v1 source for $id; conflict needs review" }
    if ((Get-Sha256 $after.Record) -ne $entry.new_record_sha256) { throw "design record mismatch for $id" }
    $replacements[$id] = $after.Record
}
if ($targetIds.Count -ne 54) { throw "expected 54 explicitly reviewed design targets; found $($targetIds.Count)" }
$v2OnlyIds = [Collections.Generic.List[int]]::new()
for ($n = 0; $n -lt $v1.Rows.Count; $n++) {
    $id = [int]$v1.Rows[$n].Id
    if (-not (Test-ByteEqual $v1.Rows[$n].Record $v2.Rows[$n].Record)) { $v2OnlyIds.Add($id) }
}
if ($v2OnlyIds.Count -ne 94) { throw "expected 94 v2 changes from v1; found $($v2OnlyIds.Count)" }
foreach ($id in $v2OnlyIds) { if ($targetIds.Contains($id)) { throw "v2/design overlap at $id" } }
$candidateBytes = Build-McfBytes $v2 $replacements
$candidate = Read-McfBytes $candidateBytes
$changed = [Collections.Generic.List[int]]::new()
for ($n = 0; $n -lt $candidate.Rows.Count; $n++) {
    $id = [int]$candidate.Rows[$n].Id
    if (-not (Test-ByteEqual $candidate.Rows[$n].Record $v2.Rows[$n].Record)) { $changed.Add($id) }
    if ($v2OnlyIds.Contains($id) -and -not (Test-ByteEqual $candidate.Rows[$n].Record $v2.Rows[$n].Record)) { throw "v2-only record not preserved: $id" }
}
$expectedChanged = @($targetIds | Sort-Object)
$actualChanged = @($changed | Sort-Object)
if (($actualChanged -join ',') -ne ($expectedChanged -join ',')) { throw 'candidate changed record set differs from the exact 54-ID whitelist' }
$restoreMap = @{}
foreach ($id in $targetIds) { $restoreMap[$id] = $v2.ById[$id].Record }
$restoredBytes = Build-McfBytes $candidate $restoreMap
$restoreExact = Test-ByteEqual $restoredBytes $v2Bytes
if (-not $restoreExact) { throw 'exact v2 restoration rehearsal failed' }
Write-ImmutableArtifact $OutPath $candidateBytes
Write-ImmutableArtifact $RestorePath $restoredBytes
$candidateIdentity = Get-McfIdentity $candidateBytes
$restoreIdentity = Get-McfIdentity $restoredBytes
$report = [ordered]@{
    status = 'OFFLINE V2-BASED CANDIDATE; RELEASE BLOCKED; NOT VEHICLE-TESTED'
    strategy = 'start from exact v2 pilot; replace only the 54 explicitly reviewed design records'
    firmware = $Policy.firmware
    mu = $Policy.mu
    source_v1 = $v1Info
    source_v2 = $v2Info
    source_v3_design = $designInfo
    candidate = [ordered]@{ path = 'neoui_build/NeoUI_v3_v2_based_candidate.mcf'; bytes = $candidateIdentity.bytes; sha1 = $candidateIdentity.sha1; sha256 = $candidateIdentity.sha256; record_count = $candidate.Rows.Count }
    changes_against_v2 = @($actualChanged)
    changed_record_count = $actualChanged.Count
    v2_changes_from_v1_preserved = $v2OnlyIds.Count
    v2_changed_ids_preserved = @($v2OnlyIds | Sort-Object)
    overlap_ids = @()
    source_record_checks = 'all 54 v2 target records matched the v1 source hashes recorded in the design changeset'
    candidate_validation = 'MCF header/TOC/record CRCs, offsets, record count and exact 54-ID whitelist verified'
    restore_rehearsal = [ordered]@{ path = 'neoui_build/NeoUI_v3_v2_restore_rehearsal.mcf'; byte_identical_to_v2 = $restoreExact; bytes = $restoreIdentity.bytes; sha1 = $restoreIdentity.sha1; sha256 = $restoreIdentity.sha256 }
    live_baseline_evidence = 'user screenshots: firmware/MU exact; skin3 MCF SHA1+size match v2; selected skin unknown; SHA256 and UTC unavailable; 3 shared metadata hashes match local lineage; info.txt source review and mount semantics pending'
    release_ready = $false
    installation_package = 'not generated: release gates and QNX failure-path validation remain open; no absolute fail-safe guarantee can be made'
    release_blockers = @('selected skin/index unknown','device SHA256 and UTC unavailable','info.txt lineage and QNX mount semantics need review','post-reboot v2 function unconfirmed','final capacity plan and backup/rollback failure-path exercise not validated on QNX','explicit release review and authorization required')
}
$reportJson = $report | ConvertTo-Json -Depth 20
[IO.File]::WriteAllText($ReportPath, $reportJson, [Text.UTF8Encoding]::new($false))
Write-Host "PASS: v2-based candidate; changed=$($actualChanged.Count); v2-only records retained=$($v2OnlyIds.Count); exact restore=$restoreExact"
Write-Host "CANDIDATE_SHA256=$($candidateIdentity.sha256)"
Write-Host 'RELEASE_READY=false'