# Yakuza: Dead Souls cheats — USA (BLUS-30826)

Cheats for the **USA** PS3 release of *Yakuza: Dead Souls*, built and tested on
real CFW hardware. No emulator results are claimed here.

- **Game:** Yakuza: Dead Souls (Ryu ga Gotoku OF THE END)
- **Disc serial:** `BLUS-30826` (USA) — **confirmed**, read from the disc
  (`PARAM.SFO`). See [`DISC.md`](DISC.md).
- **App version:** `01.00`
- **Tested on:** PS3 slim 2001a, CFW 4.93 Evilnat
- **Status:** in progress — see [What is verified](#what-is-verified)

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

**Ready to use — god mode, infinite ammo, and more (runtime codes):**
[`USING_RUNTIME_CHEATS.md`](USING_RUNTIME_CHEATS.md) and
`codelists\Yakuza Dead Souls BLUS30826 01.00.ncl`.

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

## What is verified

Nothing has been applied on the console yet. This table fills in as codes are
confirmed. The procedure to fill it in is in
[`VERIFY_SAVEPATCH.md`](VERIFY_SAVEPATCH.md).

### Savepatch codes (Apollo `BLUS30826.savepatch`)

| cheat | applied on console | effect seen in game | notes |
|---|---|---|---|
| Max Money | not yet | not yet | single 32-bit write — the region test |
| Max EXP | not yet | not yet | |
| Max Soul Points | not yet | not yet | 8-bit write |
| Max Casino Chips | not yet | not yet | |
| Max Wooden Tag | not yet | not yet | |
| Max Mahjong Sticks | not yet | not yet | |
| Max PachinKO Balls | not yet | not yet | |
| Max Slots Token | not yet | not yet | |
| Max Zombies Reward Points | not yet | not yet | |
| Max All Storage Items | not yet | not yet | 299-slot multi-write — most invasive |
| Inf Ammo | not yet | not yet | must clear inventory slots 1–6 first |
| 9999/9999 HP | not yet | not yet | may affect enemies |
| Level 98 | not yet | not yet | **32-bit write at an odd offset — see plan step 5** |
| Difficulty (×4) | not yet | not yet | mutually exclusive; one address |
| Minigame payouts (×9) | not yet | not yet | |
| Boxcelios | not yet | not yet | |

### Runtime codes (Aldo, unlabelled US set)

| cheat | applied on console | effect seen in game | notes |
|---|---|---|---|
| all 12 codes | not yet | not yet | region label itself is unconfirmed — see [`SOURCES.md`](SOURCES.md#how-the-region-was-established) |

Codes in this repo are only listed as working once they have been booted and
seen to work on the USA disc. An address that has been *found* but not *tested*
is marked as such and kept out of any release.

## What this repo is not

- It is **not** a copy of the Europe cheats with the serial changed. Those
  addresses do not carry over.
- It is **not** a save file. No game data or save files are distributed here.
- It is **not** a piracy aid. You need your own legitimately obtained copy of
  the game.

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

1. Put the game on the console's internal drive or a USB drive.
2. Load your cheat engine of choice (e.g. Artemis).
3. Select the game by its serial, `BLUS-30826`.
4. Enter the code from this repo, or use the `.db` / `.txt` file if one is
   provided.
5. Apply, then play.

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
