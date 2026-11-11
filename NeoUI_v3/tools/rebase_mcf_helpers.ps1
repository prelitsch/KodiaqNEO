function Get-Sha256([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant() }
    finally { $sha.Dispose() }
}
function Get-Sha1([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA1]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant() }
    finally { $sha.Dispose() }
}
function Get-McfIdentity([byte[]]$Bytes) { return [pscustomobject]@{ bytes=$Bytes.Length; sha1=(Get-Sha1 $Bytes); sha256=(Get-Sha256 $Bytes) } }
if (-not ('NeoUiCrc32' -as [type])) {
Add-Type -TypeDefinition @"
public static class NeoUiCrc32 {
    public static uint Compute(byte[] data, int start, int length) {
        uint crc = 0xffffffffU;
        int end = start + length;
        for (int i = start; i < end; i++) {
            crc ^= data[i];
            for (int bit = 0; bit < 8; bit++)
                crc = (crc & 1U) != 0 ? (crc >> 1) ^ 0xedb88320U : crc >> 1;
        }
        return ~crc;
    }
}
"@
}
function Get-Crc32([byte[]]$Bytes,[int]$Start,[int]$Length) {
    return [NeoUiCrc32]::Compute($Bytes,$Start,$Length)
}function Read-McfBytes([byte[]]$Bytes) {
    if ($Bytes.Length -lt 56 -or $Bytes[0] -ne 137 -or [Text.Encoding]::ASCII.GetString($Bytes,1,3) -ne 'MCF') { throw 'bad MCF signature/header' }
    $count = [int][BitConverter]::ToUInt32($Bytes,48)
    $tocEnd = 52 + 16*$count
    if ($count -le 0 -or $tocEnd+4 -gt $Bytes.Length) { throw 'invalid MCF count/TOC bounds' }
    if ((Get-Crc32 $Bytes 0 16) -ne [BitConverter]::ToUInt32($Bytes,16)) { throw 'MCF header CRC mismatch' }
    if ((Get-Crc32 $Bytes 20 24) -ne [BitConverter]::ToUInt32($Bytes,44)) { throw 'MCF TOC header CRC mismatch' }
    if ((Get-Crc32 $Bytes 48 ($tocEnd-48)) -ne [BitConverter]::ToUInt32($Bytes,$tocEnd)) { throw 'MCF TOC data CRC mismatch' }
    $rows = [Collections.Generic.List[object]]::new(); $byId=@{}; $last=$tocEnd+4
    for ($n=0; $n -lt $count; $n++) {
        $p=52+16*$n; $tag=[Text.Encoding]::ASCII.GetString($Bytes,$p,4); $id=[int][BitConverter]::ToUInt32($Bytes,$p+4); $off=[int][BitConverter]::ToUInt32($Bytes,$p+8); $size=[int][BitConverter]::ToUInt32($Bytes,$p+12)
        if ($tag -ne 'IMG ' -or $id -lt 0 -or $byId.ContainsKey($id) -or $off -ne $last -or $size -lt 40 -or $off+$size -gt $Bytes.Length) { throw "invalid MCF index row $n id=$id" }
        if ([Text.Encoding]::ASCII.GetString($Bytes,$off,4) -ne 'IMG ' -or [int][BitConverter]::ToUInt32($Bytes,$off+4) -ne $id) { throw "invalid image header id=$id" }
        $zsize=[int][BitConverter]::ToUInt32($Bytes,$off+12)
        if ($zsize -lt 0 -or 36+$zsize -gt $size-4) { throw "invalid compressed payload bounds id=$id" }
        if ((Get-Crc32 $Bytes $off 24) -ne [BitConverter]::ToUInt32($Bytes,$off+24)) { throw "image header CRC id=$id" }
        if ((Get-Crc32 $Bytes ($off+28) ($size-32)) -ne [BitConverter]::ToUInt32($Bytes,$off+$size-4)) { throw "image record CRC id=$id" }
        $record=[byte[]]::new($size); [Array]::Copy($Bytes,$off,$record,0,$size)
        $row=[pscustomobject]@{ Id=$id; Index=$n; Offset=$off; Size=$size; Record=$record }
        $rows.Add($row); $byId[$id]=$row; $last=$off+$size
    }
    if ($last -ne $Bytes.Length) { throw 'unexpected MCF suffix/trailing bytes' }
    return [pscustomobject]@{ Bytes=$Bytes; Rows=$rows; ById=$byId; TocEnd=$tocEnd; PrefixLength=($tocEnd+4) }
}
function Build-McfBytes($Parsed,[hashtable]$Replacement) {
    $prefix=[byte[]]::new($Parsed.PrefixLength); [Array]::Copy($Parsed.Bytes,0,$prefix,0,$Parsed.PrefixLength)
    $stream=[IO.MemoryStream]::new()
    try {
        $stream.Write($prefix,0,$prefix.Length); $offset=$prefix.Length
        foreach ($row in $Parsed.Rows) {
            $record=$row.Record
            if ($Replacement.ContainsKey([int]$row.Id)) { $record=[byte[]]$Replacement[[int]$row.Id] }
            $entry=52+16*$row.Index
            [Array]::Copy([BitConverter]::GetBytes([uint32]$offset),0,$stream.GetBuffer(),$entry+8,4)
            [Array]::Copy([BitConverter]::GetBytes([uint32]$record.Length),0,$stream.GetBuffer(),$entry+12,4)
            $stream.Write($record,0,$record.Length); $offset += $record.Length
        }
        $built=$stream.ToArray(); $crc=Get-Crc32 $built 48 ($Parsed.TocEnd-48); [Array]::Copy([BitConverter]::GetBytes([uint32]$crc),0,$built,$Parsed.TocEnd,4)
        return ,$built
    } finally { $stream.Dispose() }
}
function Test-ByteEqual([byte[]]$A,[byte[]]$B) {
    if ($A.Length -ne $B.Length) { return $false }
    for ($i=0; $i -lt $A.Length; $i++) { if ($A[$i] -ne $B[$i]) { return $false } }
    return $true
}
function Write-ImmutableArtifact([string]$Path,[byte[]]$Bytes) {
    if (Test-Path -LiteralPath $Path) {
        $existing=[IO.File]::ReadAllBytes($Path)
        if (-not (Test-ByteEqual $existing $Bytes)) { throw "refusing to overwrite different immutable artifact: $Path" }
        return
    }
    [IO.File]::WriteAllBytes($Path,$Bytes)
}