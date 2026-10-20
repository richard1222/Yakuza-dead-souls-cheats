# Yakuza: Dead Souls cheats — USA (BLUS-30826)

Cheats for the **USA** PS3 release of *Yakuza: Dead Souls*, aimed at real CFW
hardware. No emulator results are claimed, and **no cheat has been verified
yet** — codes only count as verified once they have been applied on a console
and the effect seen in game. Every table below says what has actually been done.

**Status:** Artemis is **ruled out** — the game froze with it enabled *and*
disabled, so it was never the cause (attempt 4 in
[What has been tried on hardware](#what-has-been-tried-on-hardware)). The working
route on this console is **live memory pokes over webMAN MOD's PS3MAPI HTTP
endpoints** — no Artemis, no launch hook. That method is **already
hardware-verified on this same console** for another title
([`SHC-cheats-for-ps3`](https://github.com/richard1222/SHC-cheats-for-ps3));
this repo applies it to `BLUS30826`.

- **Game:** Yakuza: Dead Souls (Ryu ga Gotoku OF THE END)
- **Disc serial:** `BLUS-30826` (USA) — **confirmed**, read from the disc
  (`PARAM.SFO`). See [`DISC.md`](DISC.md).
- **App version:** `01.00`
- **Target hardware:** PS3 slim 2001a, CFW 4.93 Evilnat
- **Verdict so far:** the disc and addresses are mapped; **no code has been run
  on a console yet**. See [What is verified](#what-is-verified).

## Why this repo exists

Nothing **verified** has been published for the **USA** disc.

The raw material does exist, but it is scattered and mislabelled:

- The runtime codes for the US build sit **unlabelled** in Aldo's Artemis
  database — the entry has no serial in it at all, which is why a search for
  "BLUS30826 cheats" does not find them.
- GameHacking.org has an entry for the **Europe** disc (`BLES-01399`) and
  **none for the US serial**.
- The big save-edit set is packaged for Europe, though an explicit US
  `BLUS30826` savepatch does exist in Apollo.

That matters because runtime codes are compiled addresses. They point at offsets
inside the boot executable, and the US and EU builds are different executables.
An EU code applied to a US disc is not "probably fine" — it will usually write to
the wrong place or do nothing. You can see this directly: for the same cheat, the
US and EU sets use different code addresses.

So the goal is simple:

> **Produce cheats that are actually valid for BLUS-30826, and prove each one on
> hardware before publishing it.**

The gap this repo fills is not "no addresses exist." It is: **no single,
region-correct, hardware-verified, properly credited USA collection exists.**
That is what we are building.

Full survey of every source found, with what each one covers:
[`SOURCES.md`](SOURCES.md).

The verification procedure, and what each savepatch code actually writes:
[`VERIFY_SAVEPATCH.md`](VERIFY_SAVEPATCH.md).

**Handing this to someone else?** [`TASK_FOR_MUSE.md`](TASK_FOR_MUSE.md) is a
step-by-step brief: make a save, get it off the console, apply one code, report
the result. It states the rules so a helper does not accidentally claim a
result this repo would not accept.

Our own savepatch (built from a code table, cross-checked against the published
set, structurally validated): `patches\BLUS30826.our.savepatch`. Built by
[`tools/build_savepatch.py`](tools/build_savepatch.py), checked by
[`tools/validate_savepatch.py`](tools/validate_savepatch.py), and the validator
itself is proven by [`tools/test_validator.py`](tools/test_validator.py).

**Runtime codes (a cheat engine on the console):**
[`USING_RUNTIME_CHEATS.md`](USING_RUNTIME_CHEATS.md) and
`codelists\Yakuza Dead Souls BLUS30826 01.00.ncl`. **Read the warning in that
file first:** the codelist is built and correct in form, but it has never been
applied on a console. Use the **PS3MAPI** route, *not* Artemis — see
[The route that works](#the-route-that-works). It is not "ready to use" — it is
untested.

What was read off the disc, and how to reproduce it:
[`DISC.md`](DISC.md).

## The disc (confirmed)

The USA disc has been read directly, so the target is a checked fact rather
than an assumption. From `PS3_GAME/PARAM.SFO`:

| field | value |
|---|---|
| `TITLE_ID` | **`BLUS30826`** |
| `TITLE` | `YAKUZA: Dead Souls` |
| `APP_VER` | `01.00` |
| `PS3_SYSTEM_VER` | `03.7300` |

So the disc is the USA build, application version `01.00`.

**What this settles:** the serial and game version are known and correct. The
Aldo runtime code file is `Yakuza Dead Souls 01.00.ncl`, which matches this
version.

**What it does not settle:** the runtime code addresses themselves.
`USRDIR/EBOOT.BIN` is a `SCE\0` **SELF** — a signed, encrypted executable, as a
retail disc should be. Its code cannot be read off-console, so the runtime
addresses still cannot be checked from a PC. That needs the console.

Full record and how to reproduce it: [`DISC.md`](DISC.md).

## What has been tried on hardware

The rule for this repo is that only console evidence counts. Console evidence
includes failures — a freeze, a crash, or a code that does nothing is a result,
and it is recorded here rather than quietly deleted.

| # | what was done | result | conclusion |
|---|---|---|---|
| 1 | Artemis enabled in webMAN MOD (1.47.50b), game launched | **console froze** — screen stuck, audio stopped | see below |
| 2 | Artemis confirmed `Enabled` via `/netstatus.ps3?artemis`; game launched again | **froze again**; `art.log` showed `Attached PID=…` | reproduced |
| 3 | Console restarted to clear Artemis (could not be shut off without a restart) | Artemis off; PS3 clean | — |
| 4 | **Artemis confirmed `Disabled`**, game launched | **froze a third time** | **Artemis is NOT the cause** |
| 5 | Rebooted, launched again | **ran normally** | freeze is **intermittent**, not caused by Artemis |

### What the freezes do and do not show

**Established:**

- The game froze **three times** with Artemis both **on and off**. Since attempt 4
  froze with Artemis `Disabled`, **Artemis is ruled out as the cause.**
- Attempt 5 ran normally with no config change, so the freeze is **intermittent**.
- On the first freeze **no code was ever attached** and **no `Artemis PS3 / Start
  to Attach` notification appeared**.

**Not established:**

- The cause of the intermittent freeze. An earlier theory — the game installed
  **twice** at once (`/dev_hdd0/PS3ISO/Yakuza - Dead Souls (USA).iso` **and**
  `/dev_hdd0/GAMES/Yakuza - Dead Souls (USA)`) — remains **untested**. A JB folder
  named by title rather than by serial is a known source of odd behaviour.
- That any *individual cheat code* is broken. No code has ever been applied. A
  code that was never written to memory cannot freeze a game.

**Conclusion:** the freeze is unrelated to cheats, and unrelated to Artemis. The
runtime codes remain **untested**, not failed.

### The route that works

Live memory writes over **webMAN MOD's PS3MAPI HTTP endpoints**. This needs no
Artemis, no NetCheat, and nothing installed — a browser or a shell is enough.
The method is **already verified on real hardware** for Super Heroine Chronicle
on this same console, where Infinite SP, Unlimited Turns and a god-mode HP lock
all worked.

```
GET http://<PS3IP>/getmem.ps3mapi?proc=<pid>&addr=0x0154BDA4&len=4      (addr needs 0x)
GET http://<PS3IP>/setmem.ps3mapi?proc=<pid>&addr=0154BDA4&oper=0&val=35981264   (no 0x)
```

`oper` accepts `0`=Set, `38`=And, `124`=Or, `94`=Xor, `43`=Add, `45`=Sub.

Notes learned the hard way on this console, worth knowing before you write
anything:

- `getmem` `addr=` **needs** the `0x` prefix; `setmem` `addr=` **must not** have it.
- `len=` per read is capped at **256 bytes**.
- The PS3MAPI server is **single-threaded** — parallel requests drop connections.
  Read sequentially.
- The **PS3 is big-endian**. `557` is the bytes `00 00 02 2D`. Searching
  little-endian finds nothing at all.
- The `pid=` changes every launch, so read it from `http://<IP>/cpursx.ps3`
  instead of hardcoding it.

**A ready-made tool for this game is in
[`tools/yakuza_mem.ps1`](tools/yakuza_mem.ps1):**

```powershell
# read-only status — writes nothing
powershell -NoProfile -ExecutionPolicy Bypass -File tools/yakuza_mem.ps1 -IP <ip> -Mode status

# dry run (default) — shows what would change
powershell -NoProfile -ExecutionPolicy Bypass -File tools/yakuza_mem.ps1 -IP <ip> -Mode poke -Code "Infinite Health"

# write it
powershell -NoProfile -ExecutionPolicy Bypass -File tools/yakuza_mem.ps1 -IP <ip> -Mode poke -Code "Infinite Health" -Force
```

It reads its code table from this repo's codelist and has been checked to match
**24/24** — it cannot drift from the verified set. It refuses to run without an
IP, refuses to write blind if it cannot read the address first, and reports
failure rather than claiming success when the console is unreachable.

> **Still unverified.** No code has been applied to *this* game yet. The addresses
> match the upstream US set 24/24, but matching is not applying — a row in the
> table below only fills in when the effect is seen on screen.

### What is verified

Nothing has been applied successfully on the console yet. This table fills in as
codes are confirmed. The procedure to fill it in is in
[`VERIFY_SAVEPATCH.md`](VERIFY_SAVEPATCH.md).

### Savepatch codes (Apollo `BLUS30826.savepatch`)

Our patch contains **28 code blocks / 40 code lines**. Every row below is a real
block in `patches/BLUS30826.our.savepatch`; the grouping matches the patch's own
`[GROUP:…]` headings.

**Money and progression**

| cheat | applied on console | effect seen in game | notes |
|---|---|---|---|
| Max Money | not yet | not yet | single 32-bit write — the region test |
| Max EXP | not yet | not yet | |
| Max Soul Points | not yet | not yet | 8-bit write |
| Level 98 | not yet | not yet | **32-bit write at an odd offset — see plan step 5** |

**Casino and minigame counters**

| cheat | applied on console | effect seen in game | notes |
|---|---|---|---|
| Max Casino Chips | not yet | not yet | |
| Max Wooden Tag | not yet | not yet | |
| Max Mahjong Sticks | not yet | not yet | |
| Max PachinKO Balls | not yet | not yet | |
| Max Slots Token | not yet | not yet | |
| Max Zombies Reward Points | not yet | not yet | |

**Health**

| cheat | applied on console | effect seen in game | notes |
|---|---|---|---|
| 9999/9999 HP | not yet | not yet | may affect enemies |

**Difficulty modifier (choose one — all four share one address)**

| cheat | applied on console | effect seen in game | notes |
|---|---|---|---|
| Normal / Hard / Ex-Hard / Dead Souls (Of The End) | not yet | not yet | mutually exclusive; applying two overwrites the first |

**Inventory**

| cheat | applied on console | effect seen in game | notes |
|---|---|---|---|
| Inf Ammo | not yet | not yet | 12 writes; must clear inventory slots 1–6 first |
| Max All Storage Items (Except Weapons) | not yet | not yet | 299-slot multi-write — most invasive code here |

**Minigame challenge (top payouts)**

| cheat | applied on console | effect seen in game | notes |
|---|---|---|---|
| Top Pachinko Payout | not yet | not yet | |
| Top Slots Payout | not yet | not yet | |
| Cee-Lo | not yet | not yet | |
| Cho-Han | not yet | not yet | |
| Koi-Koi | not yet | not yet | |
| Oicho-Kabu | not yet | not yet | |
| Roulette | not yet | not yet | |
| Poker | not yet | not yet | |
| Blackjack | not yet | not yet | |
| Baccarat | not yet | not yet | |
| Boxcelios | not yet | not yet | 8-bit write |

### Runtime codes (Aldo, unlabelled US set)

| cheat | applied on console | effect seen in game | notes |
|---|---|---|---|
| all 12 codes | not yet | not yet | region label itself is unconfirmed — see [`SOURCES.md`](SOURCES.md#how-the-region-was-established). Apply through **PS3MAPI**, not Artemis — see [The route that works](#the-route-that-works). |

Codes in this repo are only listed as working once they have been booted and
seen to work on the USA disc. An address that has been *found* but not *tested*
is marked as such and kept out of any release.

### What does NOT count as verification

Read this before ticking anything in the table above. It is the rule most
often broken by accident, including by people trying to help.

**A downloaded save is not verification.** Testing a patch against a save taken
from GameFAQs, Apollo's save database, or anywhere else proves only that our
patch writes bytes where it says it does. It does **not** prove the game reads
those bytes as money, HP, or level, because it was never loaded on a console.
A downloaded-save result is a *sanity check on the patch*, and may be recorded
as such — never as a verified cheat.

**An emulator result is not verification.** RPCS3 (or any emulator) is useful
for functional testing, but memory layout and timing differ from real
hardware. This repo records emulator results separately or not at all.

**"The address is correct" is not verification.** Understanding what a code
*should* do is not evidence that it *does* it.

The only thing that fills a row in the table above is: the code was applied on
the console, the game was loaded, and the effect was seen on screen. Anything
less is labelled as what it is.

### If you are helping with this repo

Useful contributions, in rough order of value:

1. **A result from a real console** — including a failure or a crash. A crash
   is a real finding and belongs in the table.
2. **A save file inspection** — the file list of a `BLUS30826` save, to confirm
   `USER01` and the folder layout. Do not publish the save itself.
3. **A correction** to the source survey in [`SOURCES.md`](SOURCES.md).

Please do **not**:

- mark anything verified without a console test
- use Europe (`BLES01399`) code addresses on the USA build — they differ, see
  [`SOURCES.md`](SOURCES.md#how-the-region-was-established)
- publish save files, `PARAM.PFD`, account IDs, or anything else personal
  (a PS3 save carries the original account's ID; it is not yours to share)
- commit Apollo's `BLUS30826.savepatch` — it is GPL-3.0 and is fetched on
  demand instead. Our own patch is `patches/BLUS30826.our.savepatch`.

### PC-side save tools

Three tools for looking at a save on the PC. They exist to make a patch
*understandable*, not to apply it — see the warning below.

| tool | what it does |
|---|---|
| [`tools/save_inspector.py`](tools/save_inspector.py) | lists a save folder's files, reads `PARAM.SFO`, shows the bytes at every offset the patch targets |
| [`tools/savepatch_apply.py`](tools/savepatch_apply.py) | dry-runs a patch against a `USER01` and prints every byte it would change |
| [`tools/compare_regions.py`](tools/compare_regions.py) | diffs two `.savepatch` files by offset — how the US/EU difference was found |
| [`tools/read_self.py`](tools/read_self.py) | reads a PS3 SELF (e.g. `EBOOT.BIN`) and **measures** where plaintext ends and ciphertext begins. Never decrypts. |
| [`tools/test_read_self.py`](tools/test_read_self.py) | self-test for the above, on synthetic files with known properties |

```
python tools/save_inspector.py  <save_folder> [--patch <file>]
python tools/savepatch_apply.py <patch> <USER01> [--only "Max Money"] [--write <out>]
python tools/compare_regions.py <a.savepatch> <b.savepatch>
python tools/read_self.py       <EBOOT.BIN> [--quiet-scan]
```

`read_self.py` exists because "the EBOOT is encrypted" was being asserted
without evidence. It reports the plaintext SELF header, then walks the file in
chunks and measures entropy and printable-character ratio, so the boundary
between header and ciphertext is a **measurement, not a claim**. On the
`BLUS30826` EBOOT the result is: ciphertext begins in the very first 4 KB chunk
(entropy 7.95–7.96, ~37% printable — the rate you get from random bytes) and
stays that way for the whole 22 MB. The same holds for
`data/module/ps3/dfengine.sprx` and `ogrez_shader_ps3.ppu.sprx`.

It deliberately does **not** try to enumerate segments. An earlier version
declared `header_size` (0x980) to be a segment table; the bytes there turned out
to be random, and rather than print a table of nonsense parsed from ciphertext
the tool now says so and skips it.

`savepatch_apply.py` **writes nothing unless `--write` is passed**, and never
overwrites its input. Dry run is the default on purpose.

> **A save patched on the PC will be rejected by the console.** A PS3 save is
> encrypted and `PARAM.PFD` is a signature over it. These tools do no
> encryption and no signing. They are for understanding a patch and for
> checking, after the fact, that bytes landed where the patch claims. The only
> way to patch a real save is Apollo Save Tool **on the console**, which
> re-encrypts and re-signs.

Two things these tools deliberately do, because both were learned the hard way:

- **The target list is read from the patch, never hardcoded.** An earlier
  version of `save_inspector.py` hardcoded three offsets (`0x0000`, `0x0004`,
  `0x0008`) that do not match the real patch, and would print bytes from the
  file header while labelling them `Max Money`. It looked authoritative and was
  wrong. Reading the patch means it cannot drift.
- **Out-of-range offsets are reported as `OUT OF RANGE`, not as a value.** A
  byte read past the end of a short file is not a result.

## What this repo is not

- It is **not** a copy of the Europe cheats with the serial changed. Those
  addresses do not carry over.
- It is **not** a save file. No game data or save files are distributed here.
- It is **not** a piracy aid. You need your own legitimately obtained copy of
  the game.

## Game folder vs ISO

Two containers for the same game. Either works; they differ in how you get it
onto the console, not in what the cheats do.

| | ISO (`.iso`) | Game folder (JB folder) |
|---|---|---|
| transfer | one ~21.7 GB file | thousands of small files |
| partial failure | re-copy the whole thing | re-copy one file |
| verification | one hash for one file | per-file hashes |
| webMAN / multiMAN | reads from `PS3ISO/` | reads from `GAMES/` |
| load time | same | same |

**A game folder is better for transfer reliability** — a dropped FTP session
costs you one file, not 20 GB. An ISO is simpler to verify, because there is
exactly one hash to check.

### Important: neither container changes the cheats

- **Savepatch codes act on your save file.** The container is irrelevant.
- **Runtime codes act on the game's memory while it runs.** Also identical.
- **Patching the executable is not on the table either way.** `EBOOT.BIN` is a
  `SCE\0` SELF — signed and encrypted — and extracting the ISO does **not**
  decrypt it. See [`DISC.md`](DISC.md).

So: extracting the ISO changes nothing about what is verifiable. It is a
transfer choice, not a cheat-enabling one.

What a game folder *does* give you is access to the **non-encrypted files** —
textures, audio, configs — which the ISO makes no easier to reach. Those are the
only route to learning anything new about addresses from a PC.

### Layout

| where | path the console expects |
|---|---|
| internal drive | `dev_hdd0/GAMES/BLUS30826/` |
| USB drive (root) | `GAMES/BLUS30826/` |

The folder must be named by serial. Inside it is `PS3_GAME/` and
`PS3_DISC.SFB`, exactly as on the disc.

## Cheat types

There are two fundamentally different kinds, and it matters which one a code is:

**Runtime codes** patch the game's memory while it runs. They need a cheat
engine on the console (this is the NetCheat / Artemis style of code, written as
`address value` pairs). They reset when you quit the game.

**Save edits** modify the save file on disk. They survive a reboot and need no
cheat engine running — you edit the save, then load it. The large body of
existing *Dead Souls* cheats are save edits of this kind, because save editing
does not require knowing anything about the executable.

Where a cheat can be done either way, both are noted, because save editing is
much easier for an ordinary player.

## Using these cheats

### Runtime codes on CFW

> **Do not use Artemis on this hardware.** It was tested and is unnecessary — the
> game froze with Artemis both enabled and disabled, so it is not the cause, and
> it is not needed for any code here.
>
> Use a **live memory write over PS3MAPI** instead. Start the game normally, then
> write the address/value pair. See
> [The route that works](#the-route-that-works).

1. Put the game on the console's internal drive or a USB drive.
2. Load your cheat engine of choice — on this setup, **PS3MAPI**, not Artemis.
3. Select the game by its serial, `BLUS-30826`.
4. Enter the code from this repo, or its address/value pair from the `.ncl`.
5. Write the value, then check the effect in game.

The game must be running before runtime codes take effect.

### Save edits

1. Copy your save off the console, or use a save manager on the console.
2. Back the save up first — always. A bad edit can corrupt it.
3. Apply the edit to the `USER01` file inside the save.
4. Load the save in-game.

The exact save container differs between regions. Do not assume an EU save
recipe applies to a US save without checking.

To get the USA savepatch and check it:

```
python tools/fetch_savepatch.py
```

It downloads Apollo's `BLUS30826.savepatch`, verifies it against a pinned
SHA-256, and stages it for you. It refuses to write a file that does not match,
so a substituted patch (for example, the EU one) fails loudly rather than
quietly corrupting a save. Step-by-step test order:
[`VERIFY_SAVEPATCH.md`](VERIFY_SAVEPATCH.md).

## Credits and sources

Existing work that this repo builds on or cross-checks against:

- **jgduff1** — the US runtime code set (unlabelled in Aldo's Artemis database)
  and the only cheat PKG set found that explicitly names `BLUS30826`
- **luc-ita** — four NetCheat PS3 runtime codes for Europe (GameHacking.org)
- **jijibecali** — the Europe runtime code set (Aldo's database)
- **krustytoe**, **www55.atwiki.jp**, **savedata.jp**, and *Game Genie For PS3*
  — the original save-editor code set, packaged by Apollo as `BLUS30826.savepatch`
- **bucanero / Apollo Save Tool** — the `BLUS30826` save patch set and patcher

Where a credit is due it is given on the specific code. If you believe
something here is uncredited or miscredited, open an issue.

A per-code attribution table lives in
[`SOURCES.md`](SOURCES.md#1-runtime-codes-artemis--netcheat).

## Compatibility

| region | serial | covered by this repo |
|---|---|---|
| USA | `BLUS-30826` | **yes — this is the target (confirmed from disc)** |
| Europe | `BLES-01399` | no — addresses differ, use the existing EU sets |
| Japan | `BLJM60316` | no |
| PSN (US) | `NPUB31509` | no |
| PSN (EU) | `NPEB02034` | no |

## License and intent

Cheats and documentation here are shared for personal use with a legitimately
owned copy of the game. Reuse with credit is fine.
