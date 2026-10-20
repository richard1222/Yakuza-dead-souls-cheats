# How to use the runtime cheats (god mode, infinite ammo, etc.)

Runtime codes patch the game's memory while it runs. They give you **Infinite
Health** (god mode) and **Infinite Ammo**, plus items, money and ability points.
They reset when you quit the game.

There is a ready-to-use Artemis codelist in this folder:

```
codelists\Yakuza Dead Souls BLUS30826 01.00.ncl
```

It is named for your serial and app version, so Artemis picks it up by itself.

> **These codes are NOT verified on hardware yet.** They are the set authored by
> **jgduff1**, taken from Aldo's database. See the warning at the bottom — read
> it before you rely on any of them.

## What you need

- The game running on your CFW console (4.93 Evilnat).
- **Artemis** (or another PS3 cheat engine that loads `.ncl` codelists).
- This `.ncl` file copied to the console.

## Install

1. Copy the `.ncl` file onto your console (USB drive, or FTP). A common place
   for Artemis codelists is on the internal drive next to Artemis itself — put it
   wherever your Artemis build reads `.ncl` files from, or browse to it manually.

2. Start the game and get **in-game** (in a save you don't mind testing on).

3. Open Artemis and load the codelist. Because the filename contains
   `BLUS30826 01.00`, it matches your disc (`TITLE_ID = BLUS30826`,
   `APP_VER = 01.00`, both read from your disc).

4. Tick the codes you want.

5. **Apply, then play.** Runtime codes do nothing until the game is running.

6. To remove them, untick and re-apply, or just quit the game. Nothing is
   written to your save or your disc.

## Crash safety — do this first

> **Read this before you tick anything.**

These codes are **unverified on your system**. An unverified memory patch can
freeze or crash the game. Before you start:

1. **Save your game first**, in a slot you can reload.
2. Back that save up (copy it off the console).
3. Apply **one code at a time** to start with. If something freezes, you know
   which code did it.
4. Test on a save you don't care about losing, not your main one.

If a code freezes the game, that is a real result — tell me and it goes in the
repo as such. It is not a failure on your part.

## The codes, and what to expect

**Memory vs ASM:** each cheat comes in two flavours. The **Memory** version
writes a value to a fixed address. The **ASM** version patches the instruction
instead, which usually holds up better while playing. If one doesn't work, try
the other. **Don't enable both versions of the same cheat at once.**

| cheat | codes | notes |
|---|---|---|
| **Infinite Health** (god mode) | Memory + ASM | **⚠ see warning below** |
| **Infinite Ammo + No Reload** | Memory + ASM | the one you asked for |
| Infinite Items | Memory + ASM | 6 addresses in the ASM version |
| Max Level On 1 Kill + Lots Of Ability Points | Memory + ASM | |
| Lots + Infinite Ability Points On Start | Memory + ASM | apply before loading a save |
| Lots Of Money When Buy + Sell + Gain | Memory + ASM | money rises as you trade |
| Partner Have Infinite Medkit | Memory + ASM | companion only |

### ⚠ The Infinite Health warning

The original author's own note, kept verbatim:

> *"It also affects enemies, but the Shotgun still kills them."*

So this is **not clean god mode**. It may make enemies very tough as well as
you. That is the author's documented behaviour, not a bug in this file. If you
find enemies are unkillable except by shotgun, that is expected.

## If a code doesn't work

Possible reasons, in order of likelihood:

1. **Wrong game version.** These target `01.00`. Your disc is `01.00`, confirmed
   from `PARAM.SFO`, so this should be right — but if your copy is a different
   dump, addresses can differ.
2. **Code needs the other flavour.** Try ASM if Memory failed, or vice versa.
3. **Applied at the wrong time.** Some codes must be on *before* loading a save.
4. **The code is simply wrong for this build.** This is the genuinely open
   question — see below.

## The honest status

**Nothing in this file has been tested on real hardware by us.** The addresses
come from jgduff1's set for the US build, found unlabelled in Aldo's Artemis
database. Strong reasons to think it is the right set for your disc:

- Your disc is confirmed `BLUS30826`, app `01.00`.
- The file targets app `01.00`, matching.
- Its code addresses **differ** from the Europe set for the same cheats, so it
  is a genuinely different build from `BLES01399`.
- jgduff1's PKG thread names `BLUS30826` explicitly.

But the executable on your disc is **encrypted**, so the addresses could not be
checked against the binary off-console. **Until you run them, they are
unverified.** Please report back what actually happens, including crashes —
that is what fills in the verified table in the [README](README.md).

## Credit

All 12 codes are by **jgduff1**. Repackaged here under a `BLUS30826` filename so
it loads correctly; the code values are unchanged. Source: Aldo's PS3 Artemis
Codelist Database.
