# Yakuza Dead Souls (BLUS30826 01.00) -- live memory status / poke tool
#
# Method is copied from the SUPER HEROINE CHRONICLE tool that is verified
# working on this same console:
#
#     GET http://<IP>/getmem.ps3mapi?proc=<pid>&addr=0xADDR&len=N   (addr needs 0x)
#     GET http://<IP>/setmem.ps3mapi?proc=<pid>&addr=ADDR&oper=0&val=VALUE  (no 0x)
#
# No Artemis. Artemis froze this console every time it was tried.

param(
    [string] $IP = "PS3_IP_HERE",
    [ValidateSet("status","poke")] [string] $Mode = "status",
    [string] $Code = "",
    [string] $Value = "",
    [switch] $Force
)

$ErrorActionPreference = "Stop"

if ($IP -eq "PS3_IP_HERE") {
    Write-Host "SET YOUR PS3 IP FIRST (edit the `$IP line at the top of this script)." -ForegroundColor Yellow
    exit 1
}

# ---- the codes, from codelists\Yakuza Dead Souls BLUS30826 01.00.ncl --------
# addr/value are exactly as they appear in the codelist. Verified 24/24 against
# the upstream US set (bucanero/ArtemisPS3).
$CODES = @(
    @{ name = "Infinite Health";                              addr = "0154BDA4"; val = "35981264" },
    @{ name = "Infinite Health [ASM]";                        addr = "002E7EC0"; val = "60000000" },
    @{ name = "Infinite Health [ASM] (2)";                    addr = "002E7E9C"; val = "60000000" },
    @{ name = "Infinite Ammo + No Reload";                    addr = "01536720"; val = "0004" },
    @{ name = "Infinite Ammo + No Reload (2)";                addr = "3476E924"; val = "00000005" },
    @{ name = "Infinite Ammo + No Reload [ASM]";              addr = "00AAA9A8"; val = "60000000" },
    @{ name = "Infinite Ammo + No Reload [ASM] (2)";          addr = "0052D1C0"; val = "60000000" },
    @{ name = "Lots Of Money When Buy + Sell + Gain";         addr = "01537E08"; val = "00013880" },
    @{ name = "Lots Of Money When Buy + Sell + Gain [ASM]";   addr = "00AAD658"; val = "93BC0000" },
    @{ name = "Max Level On 1 Kill + Lots Of Ability Points"; addr = "0154BDB8"; val = "00000050" },
    @{ name = "Max Level On 1 Kill [ASM]";                    addr = "00AAEFB8"; val = "905E0018" },
    @{ name = "Max Level On 1 Kill [ASM] (2)";                addr = "00AAEFBC"; val = "905E001C" },
    @{ name = "Lots + Infinite Ability Points On Start";      addr = "0154BDC6"; val = "E600" },
    @{ name = "Lots + Infinite Ability Points [ASM]";         addr = "00AAF030"; val = "98C30026" },
    @{ name = "Infinite Items";                               addr = "01534DE8"; val = "00000001" },
    @{ name = "Infinite Items [ASM]";                         addr = "00AA9748"; val = "30630000" },
    @{ name = "Infinite Items [ASM] (2)";                     addr = "00AA9768"; val = "B0640006" },
    @{ name = "Infinite Items [ASM] (3)";                     addr = "00AA977C"; val = "B0A40000" },
    @{ name = "Infinite Items [ASM] (4)";                     addr = "00AA9780"; val = "B0A40002" },
    @{ name = "Infinite Items [ASM] (5)";                     addr = "00AA9788"; val = "B0A40004" },
    @{ name = "Infinite Items [ASM] (6)";                     addr = "00AA9790"; val = "B0A40006" },
    @{ name = "Partner Have Infinite Medkit";                 addr = "308EE23C"; val = "00000003" },
    @{ name = "Partner Have Infinite Medkit [ASM]";           addr = "00D47424"; val = "30840000" },
    @{ name = "Partner Have Infinite Medkit [ASM] (2)";       addr = "00D47428"; val = "90830018" }
)

$script:proc = ""

function Invoke-Ps3([string]$path) {
    return ((curl.exe -s --max-time 15 "http://$IP/$path") -join "")
}

function Get-Ps3Mem([string]$addrHex, [int]$len = 4) {
    $fmt = "{0:X8}" -f [Convert]::ToUInt32($addrHex, 16)
    # getmem wants the 0x prefix
    $r = Invoke-Ps3 "getmem.ps3mapi?proc=$script:proc&addr=0x$fmt&len=$len"
    $m = [regex]::Match($r, [regex]::Escape($fmt) + "\s+((?:[0-9A-F]{2}\s+){1,})")
    if ($m.Success) { return ($m.Groups[1].Value.Trim() -replace '\s+', '') }
    return $null
}

function Set-Ps3Mem([string]$addrHex, [string]$valHex) {
    # setmem must NOT have the 0x prefix
    Invoke-Ps3 "setmem.ps3mapi?proc=$script:proc&addr=$addrHex&oper=0&val=$valHex" | Out-Null
}

function Show([string]$m, [string]$c = "Gray") { Write-Host $m -ForegroundColor $c }

Write-Host ""
Show "==============================================================================" Cyan
Show "  Yakuza: Dead Souls (BLUS30826 01.00) -- live memory  (webMAN / PS3MAPI)"     Cyan
Show "==============================================================================" Cyan
Show ""

Write-Host "[1/3] Finding webMAN MOD at $IP ... " -NoNewline
try { $cpursx = Invoke-Ps3 "cpursx.ps3" } catch {
    Show "FAILED" Red; Show "      Cannot reach http://$IP/ -- PS3 on? webMAN running?" Red; exit 1
}
if ($cpursx -notmatch "webMAN|wMAN") { Show "NOT webMAN" Red; exit 1 }
Show "yes" Green

Write-Host "[2/3] Finding the running game ... " -NoNewline
if ($cpursx -match "pid=([0-9A-Fa-f]{8})") {
    $script:proc = "0x" + $matches[1]
} else {
    Show "NO GAME RUNNING" Red; Show "      Launch Yakuza first, then re-run." Red; exit 1
}
Show ("pid=" + $script:proc) Green
if ($cpursx -notmatch "BLUS30826") {
    Show "      WARNING: running title is not BLUS30826." Yellow
}

Write-Host "[3/3] $Mode" -NoNewline
Show ""; Show ""

if ($Mode -eq "status") {
    Show "  Reading the 3 'cleanest' addresses (no writes in status mode)."
    Show ""
    foreach ($c in ($CODES | Where-Object { $_.name -in @("Infinite Health","Infinite Ammo + No Reload","Lots Of Money When Buy + Sell + Gain") })) {
        $cur = Get-Ps3Mem $c.addr 4
        if ($null -eq $cur) {
            Show ("  {0,-42} 0x{1,-8} = <no read>" -f $c.name, $c.addr) Red
        } else {
            Show ("  {0,-42} 0x{1,-8} = {2}" -f $c.name, $c.addr, $cur) Gray
            Show ("  {0,-42} {1,-19}   code wants {2}" -f "", "currently:", $c.val) DarkGray
        }
    }
    Show ""
    Show "Status only: nothing was written." DarkGray
    Show ""
    exit 0
}

# ---- poke -------------------------------------------------------------------
if (-not $Code) { Show "  --poke needs -Code <name>. Available:" Yellow; $CODES | ForEach-Object { Show ("    " + $_.name) }; exit 1 }

$target = $CODES | Where-Object { $_.name -ieq $Code } | Select-Object -First 1
if (-not $target) { Show "  No code named '$Code'. Names are listed with an empty -Code." Red; exit 1 }

$val = if ($Value) { $Value } else { $target.val }

Show ("  {0}" -f $target.name) Cyan
Show ("    address : 0x{0}" -f $target.addr)
Show ("    write   : {0}" -f $val)
Show ""

$before = Get-Ps3Mem $target.addr 4
$beforeTxt = if ($null -eq $before) { "<no read>" } else { $before }
Show ("    before  : {0}" -f $beforeTxt)

if ($null -eq $before) { Show "    REFUSING: could not read the address, so I will not write blind." Red; exit 1 }

if (-not $Force) {
    Show ""
    Show "    Dry run. Nothing written. Re-run with -Force to actually write." Yellow
    exit 0
}

Set-Ps3Mem $target.addr $val
Start-Sleep -Milliseconds 300
$after = Get-Ps3Mem $target.addr 4
$afterTxt = if ($null -eq $after) { "<no read>" } else { $after }
Show ("    after   : {0}" -f $afterTxt)
Show ""
if ($after -eq $val) { Show "    WROTE OK -- now check the effect in game." Green }
else { Show "    write did not take (readback differs)." Yellow }
Show ""
