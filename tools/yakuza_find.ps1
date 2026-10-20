# yakuza_find.ps1 -- find a value's RAM address in Yakuza: Dead Souls
#                   (BLUS30826 01.00) by DIFFING two snapshots.
#
# WHY THIS EXISTS
# ---------------
# The 24 published codes in this repo have fixed addresses. That is fine for
# them, but it means anything NOT already published has to be found the hard
# way: pick a number you can see on screen, change it in-game, and locate the
# one memory word that followed. That is how the god-mode HP field was found
# for another title on this console.
#
# The method is copied from the tool that is hardware-verified on this same
# console (SHC-cheats-for-ps3), including its hard-won gotchas:
#
#   * The PS3 is BIG-ENDIAN. 557 is the bytes 00 00 02 2D. Decoding
#     little-endian finds nothing at all. This tool decodes big-endian.
#   * getmem addr= needs the 0x prefix; setmem addr= must NOT have it.
#   * len= per read is capped at 256 bytes.
#   * The PS3MAPI server is single-threaded -- requests must be sequential.
#   * Single-value searches are useless on this hardware (large ascending
#     integer tables make every small number appear hundreds of times).
#     Only a DIFF between two snapshots isolates the real field.
#
# SAFETY
# ------
# This tool READS ONLY. There is no code path here that writes to the console.
# It produces candidate addresses for you to inspect and then try by hand with
# yakuza_mem.ps1. That separation is deliberate: a bad guess should cost you a
# read, never a corrupted game state.
#
# USAGE
#   Snapshot A (value is X on screen):
#     powershell -ExecutionPolicy Bypass -File yakuza_find.ps1 -IP <ip> -Mode snap -Out a.json
#   ... change the value in game (spend money, take damage) ...
#   Snapshot B (value is now Y):
#     powershell -ExecutionPolicy Bypass -File yakuza_find.ps1 -IP <ip> -Mode snap -Out b.json
#   Diff them:
#     powershell -ExecutionPolicy Bypass -File yakuza_find.ps1 -Mode diff -A a.json -B b.json -From 500 -To 400

param(
    [string] $IP = "PS3_IP_HERE",

    [ValidateSet("snap","diff","read")] [string] $Mode = "snap",

    # snapshot files
    [string] $Out = "snap.json",
    [string] $A = "",
    [string] $B = "",

    # ---- region to snapshot ---------------------------------------------------
    # Yakuza's heap geometry is NOT known yet -- these are starting guesses
    # based on the same engine family. Narrow them once we learn more.
    [uint32] $Start = 0x30000000,
    [uint32] $End   = 0x31000000,   # 16 MB default: keep snapshots small first
    [uint32] $Step  = 0x1000,       # read granularity

    # ---- diff filter ---------------------------------------------------------
    # only report addresses whose value moved from $From to $To (0 = no filter)
    # NOTE: these are [int64] on purpose. A 32-bit word can be up to 0xFFFFFFFF,
    # which overflows [int] and crashes the parameter binder.
    [int64] $From = 0,
    [int64] $To   = 0,
    [int] $MaxHits = 40,

    # ---- direct read ---------------------------------------------------------
    [string] $Addr = ""
)

$ErrorActionPreference = "Stop"

$READ_CAP = 256   # PS3MAPI len= cap, observed

function Invoke-Ps3([string]$path) {
    return ((curl.exe -s --max-time 20 "http://$IP/$path") -join "")
}

function Show([string]$m, [string]$c = "Gray") { Write-Host $m -ForegroundColor $c }

function Get-Pid {
    $cpursx = Invoke-Ps3 "cpursx.ps3"
    if ($cpursx -notmatch "webMAN|wMAN") {
        Show "  Not webMAN MOD at $IP (is the PS3 on?)" Red
        exit 1
    }
    if ($cpursx -match "pid=([0-9A-Fa-f]{8})") {
        $p = "0x" + $matches[1]
        if ($cpursx -notmatch "BLUS30826") {
            Show "  WARNING: running title is not BLUS30826." Yellow
        }
        return $p
    }
    Show "  No game running. Launch Yakuza first." Red
    exit 1
}

# Read a chunk. Returns array of bytes, or $null.
function Get-Bytes([uint32]$addr, [int]$len, [string]$proc) {
    $fmt = "{0:X8}" -f $addr
    $r = Invoke-Ps3 "getmem.ps3mapi?proc=$proc&addr=0x$fmt&len=$len"
    $m = [regex]::Match($r, [regex]::Escape($fmt) + "\s+((?:[0-9A-F]{2}\s+){1,})")
    if (-not $m.Success) { return $null }
    $hex = ($m.Groups[1].Value.Trim() -replace '\s+', '')
    if ($hex.Length -lt 2) { return $null }
    $n = [int]($hex.Length / 2)
    $out = New-Object byte[] $n
    for ($i = 0; $i -lt $n; $i++) { $out[$i] = [Convert]::ToByte($hex.Substring($i*2, 2), 16) }
    return $out
}

function Read-Word([byte[]]$bytes, [int]$off) {
    # BIG-ENDIAN, per the PS3's PowerPC CPU
    return ([uint32]$bytes[$off] -shl 24) -bor ([uint32]$bytes[$off+1] -shl 16) -bor `
           ([uint32]$bytes[$off+2] -shl 8) -bor [uint32]$bytes[$off+3]
}

# ---------------------------------------------------------------------------
Show ""
Show "==============================================================================" Cyan
Show "  Yakuza: Dead Souls -- value finder (read-only, big-endian)   PS3MAPI"        Cyan
Show "==============================================================================" Cyan
Show ""

if ($Mode -eq "diff") {
    # ---- pure offline diff, no console needed ------------------------------
    if (-not $A -or -not $B) { Show "  -Mode diff needs -A <file> -B <file>" Red; exit 1 }
    if (-not (Test-Path $A)) { Show "  missing $A" Red; exit 1 }
    if (-not (Test-Path $B)) { Show "  missing $B" Red; exit 1 }

    $sa = Get-Content $A -Raw | ConvertFrom-Json
    $sb = Get-Content $B -Raw | ConvertFrom-Json

    Show ("  A: {0}  base {1}  {2} words" -f $A, $sa.base, $sa.words.Count) Gray
    Show ("  B: {0}  base {1}  {2} words" -f $B, $sb.base, $sb.words.Count) Gray
    if ($sa.base -ne $sb.base) {
        Show "  WARNING: snapshots cover different base addresses -- diff may be meaningless." Yellow
    }
    Show ""

    # base is stored as "0x30000000"; parse once, safely.
    $baseNum = [Convert]::ToUInt32(([string]$sa.base -replace '^0x', ''), 16)

    $wa = $sa.words
    $wb = $sb.words
    $n = [Math]::Min($wa.Count, $wb.Count)
    Show ("  comparing {0} words ..." -f $n) DarkGray

    $hits = @()
    for ($i = 0; $i -lt $n; $i++) {
        $va = [int64][uint32]$wa[$i]
        $vb = [int64][uint32]$wb[$i]
        if ($va -eq $vb) { continue }

        if ($From -ne 0 -or $To -ne 0) {
            # caller knows the on-screen numbers; require the exact transition
            if ($va -ne $From -or $vb -ne $To) { continue }
        } else {
            # no expected values: ignore the known junk fills
            # Compare as [int64] against explicit decimal values.
            # Do NOT write these as bare 0x literals: PowerShell parses
            # 0xAAAAAAAA as the NEGATIVE int32 -1431655766, and [uint32] of a
            # negative throws. Decimal literals cannot go wrong.
            $f1  = 1065353216   # 0x3F800000  float 1.0
            $f55 = 1431655765   # 0x55555555  free fill
            $fAA = 2863311530   # 0xAAAAAAAA  free fill
            if ($vb -eq $f1  -or $va -eq $f1)  { continue }
            if ($vb -eq $f55 -or $va -eq $f55) { continue }
            if ($vb -eq $fAA -or $va -eq $fAA) { continue }
        }

        # uint32 arithmetic wraps if done via [uint32] cast; do it in int64.
        # $baseNum must be a NUMBER here -- if it arrives as a string the
        # :X8 format silently prints its decimal value instead of hex.
        $addr = [int64]$baseNum + [int64]($i) * 4
        # ToString on a real UInt32. Do NOT use [string]::Format("{0:X8}", ...)
        # with an Int64 here: it silently formats as DECIMAL, which is how this
        # printed 805306408 instead of 0x30000028.
        $addrHex = ([uint32]$addr).ToString("X8")
        $hits += @{ addr = $addrHex; from = $va; to = $vb }
        if ($hits.Count -ge $MaxHits) { break }
    }

    Show ""
    if ($hits.Count -eq 0) {
        Show "  No candidates." Yellow
        Show "  Things to check, in order:" DarkGray
        Show "    1. Are you sure the on-screen values were what you passed -From / -To?" DarkGray
        Show "    2. Was the region you snapshotted the right one? (see -Start / -End)" DarkGray
        Show "    3. Big-endian: if you read the value off a hex editor you may have it byte-swapped." DarkGray
        Show "    4. A value shown on screen is often NOT stored raw (it may be a derived" DarkGray
        Show "       display value, or scaled by 10 or 100)." DarkGray
    } else {
        Show ("  {0} candidate(s):" -f $hits.Count) Green
        Show ""
        Show ("    {0,-12}  {1,12}  ->  {2,-12}" -f "address", "before", "after") Cyan
        foreach ($h in $hits) {
            # $h.addr is already a formatted hex STRING. Do not re-format it:
            # applying :X to a string prints its decimal value instead.
            $line = "    0x" + $h.addr +
                    ([string]$h.from).PadLeft(12) + "  ->  " +
                    ([string]$h.to).PadRight(12)
            Show $line Gray
        }
        Show ""
        Show "  Next: try each with" DarkGray
        Show "    yakuza_mem.ps1 -IP <ip> -Mode poke -Code `<name`> -Value <hex>" DarkGray
    }
    Show ""
    exit 0
}

# ---- console required from here -------------------------------------------
$proc = Get-Pid
Show ("  game pid : {0}" -f $proc) Green

if ($Mode -eq "read") {
    if (-not $Addr) { Show "  -Mode read needs -Addr <hex>" Red; exit 1 }
    $fmt = "{0:X8}" -f [Convert]::ToUInt32($Addr, 16)
    $b = Get-Bytes ([Convert]::ToUInt32($fmt,16)) 16 $proc
    if ($null -eq $b) { Show "  could not read 0x$fmt" Red; exit 1 }
    Show ""
    Show ("  0x{0} : {1}" -f $fmt, (($b | ForEach-Object { "{0:X2}" -f $_ }) -join " ")) Gray
    Show ("  as big-endian u32  : {0}" -f (Read-Word $b 0)) Green
    Show ("  as big-endian u32+4: {0}" -f (Read-Word $b 4)) Green
    Show ""
    exit 0
}

# ---- snapshot --------------------------------------------------------------
$size = [uint32]($End - $Start)
Show ("  snapshotting 0x{0:X8} - 0x{1:X8}  ({2:N0} bytes)" -f $Start, $End, $size) Gray
Show ""

$words = New-Object 'System.Collections.Generic.List[uint32]'
$addr = $Start
$done = 0
$failed = 0

while ($addr -lt $End) {
    $b = Get-Bytes $addr $READ_CAP $proc
    if ($null -eq $b -or $b.Length -lt 4) {
        # an unreadable chunk is normal (unmapped page) -- record zeros, keep going
        $failed++
        $count = [int]($READ_CAP / 4)
        for ($i = 0; $i -lt $count; $i++) { $words.Add([uint32]0) }
    } else {
        $count = [int]($b.Length / 4)
        for ($i = 0; $i -lt $count; $i++) { $words.Add((Read-Word $b ($i*4))) }
    }
    $addr = [uint32]($addr + $READ_CAP)
    $done++

    if (($done % 256) -eq 0) {
        $pct = [int](100 * ($addr - $Start) / $size)
        Write-Host ("`r  ... {0}%   ({1} chunks, {2} unreadable)   " -f $pct, $done, $failed) -NoNewline -ForegroundColor DarkGray
    }
}
Write-Host ""
Show ""

@{
    base  = ("0x{0:X8}" -f $Start)
    end   = ("0x{0:X8}" -f $End)
    pid   = $proc
    title = "BLUS30826"
    words = $words.ToArray()
} | ConvertTo-Json -Depth 3 -Compress | Set-Content $Out

Show ("  wrote {0}" -f $Out) Green
Show ("  {0} chunks read, {1} unreadable (unmapped pages -- normal)" -f $done, $failed) DarkGray
Show ""
Show "  Now change the value ON SCREEN in the game, then take a second snapshot" DarkGray
Show "  with -Out <other file>, and run -Mode diff -A <first> -B <second>." DarkGray
Show ""
