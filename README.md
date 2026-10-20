# Yakuza: Dead Souls cheats — USA (BLUS-30826)

Cheats for the **USA** PS3 release of *Yakuza: Dead Souls*, built and tested on
real CFW hardware. No emulator results are claimed here.

- **Game:** Yakuza: Dead Souls (Ryu ga Gotoku OF THE END)
- **Disc serial:** `BLUS-30826` (USA)
- **Tested on:** PS3 slim 2001a, CFW 4.93 Evilnat
- **Status:** in progress — see [What is verified](#what-is-verified)

## Why this repo exists

Nothing useful has been published for the **USA** disc.

Every cheat collection that covers this game targets the **Europe** disc
(`BLES-01399`). GameHacking.org has an entry for Europe and **none at all for
BLUS-30826**. The save-editor codes in circulation likewise target the EU
`USER01` save file.

That matters because these are compiled addresses. Cheat codes for a PS3 game
point at offsets inside the boot ELF, and the US and EU builds are different
executables. An EU code applied to a US disc is not "probably fine" — it will
usually write to the wrong place or do nothing.

So the goal is simple:

> **Produce cheats that are actually valid for BLUS-30826, and prove each one on
> hardware before publishing it.**

## What is verified

Nothing yet. This table fills in as codes are confirmed on the console.

| cheat | status | notes |
|---|---|---|
| — | — | — |

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

## Credits and sources

Existing work that this repo builds on or cross-checks against, all of which
targets the Europe disc:

- **luc-ita** — four NetCheat PS3 runtime codes (GameHacking.org)
- **krustytoe**, **www55.atwiki.jp**, **savedata.jp** — the original save-editor
  code set (via save-editor.com)
- **Apollo Save Tool** — the `BLES01399.savepatch` save patch set

Where a credit is due it is given on the specific code. If you believe
something here is uncredited or miscredited, open an issue.

## Compatibility

| region | serial | covered by this repo |
|---|---|---|
| USA | `BLUS-30826` | **yes — this is the target** |
| Europe | `BLES-01399` | no — addresses differ, use the existing EU sets |
| Japan | `BLJM60316` | no |
| PSN (US) | `NPUB31509` | no |
| PSN (EU) | `NPEB02034` | no |

## License and intent

Cheats and documentation here are shared for personal use with a legitimately
owned copy of the game. Reuse with credit is fine.
