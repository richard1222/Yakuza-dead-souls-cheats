# Start here — Yakuza: Dead Souls (USA) cheats

`BLUS30826` / app `01.00`. Everything here is for the **USA** disc only.

## The one page you need

| if you are at the console | read |
|---|---|
| applying a runtime code and watching the screen | **`TASK_FOR_MUSE_RUNTIME.md`** ← start here |
| testing the save-patch route instead | `TASK_FOR_MUSE.md` |

`TASK_FOR_MUSE_RUNTIME.md` is the fast route: a plain HTTP memory write over
webMAN MOD's PS3MAPI. Nothing is installed, nothing touches your disk, and
quitting the game puts it back to stock.

**Do not use Artemis.** It is not the route here.

## The rule that matters

A code counts only once **the effect has been seen on the console**. Not
"the address looks right". Not "the tool printed success". Seen, in the game.

A freeze or a crash is a **result**, not a failure. Report it and it goes in the
repo as a finding.

## What is actually known

| | |
|---|---|
| disc | `BLUS30826`, app `01.00` — confirmed from the disc |
| addresses | match the upstream US set **24/24** |
| applied to this game on hardware | **never** |
| verified in game | **nothing yet** |

That last row is the point of this whole exercise. Nothing is dressed up.

## Files

**Briefs**
- `TASK_FOR_MUSE_RUNTIME.md` — apply one runtime code, watch the health bar
- `TASK_FOR_MUSE.md` — save-patch route (`[Max Money]`), slower, needs a save on USB
- `START_HERE.md` — the repo's own orientation

**Tools** (`tools/`)
- `yakuza_mem.ps1` — reads and writes codes over PS3MAPI. Read-only by default; needs `-Force` to write.
- `yakuza_find.ps1` — **read-only** value finder. Snapshots RAM twice and diffs, to locate an address not already published.
- `verify_mem_tool.py` / `test_yakuza_find.py` — prove the two tools above are correct
- `read_self.py` — measures where a PS3 SELF stops being plaintext

**Data**
- `codelists/` — the 24 runtime codes
- `patches/` — save patches

**Docs**
- `README.md` — the full picture, including the honest status table
- `USING_RUNTIME_CHEATS.md` — runtime codes in detail, with the gotchas
- `VERIFY_SAVEPATCH.md` — how a row gets filled in
- `SOURCES.md`, `DISC.md` — where everything came from

## The short version

1. Get the PS3's IP: **XMB → Settings → Network Settings → Connection Status**.
2. `powershell -NoProfile -ExecutionPolicy Bypass -File tools\yakuza_mem.ps1 -IP <ps3-ip> -Mode status`
3. If that prints a pid and a value, follow `TASK_FOR_MUSE_RUNTIME.md` from Part 1.
4. If it does not, **stop and report** — that is the result.
