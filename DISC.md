# Disc record — Yakuza: Dead Souls (USA)

A reproducible record of what was read off the USA disc, so the repo's
region claims can be re-checked rather than taken on trust.

**No game data is stored in this repo.** Only metadata and hashes are recorded
here. You need your own copy of the disc to reproduce this.

## The disc

| | |
|---|---|
| file | `Yakuza - Dead Souls (USA).iso` |
| size | 21,724,135,424 bytes |
| disc volume ID | `YAKUZA: DEAD SOULS` |
| application ID | `*PLAYSTATION(R)3` |
| generator | `*SCEI BD/DVD Generator` |
| UDF version | 2.50 |
| disc created | 2011-12-29 |

## `PS3_GAME/PARAM.SFO` (1,040 bytes)

Read with `tools/parse_sfo.py`.

| field | format | value |
|---|---|---|
| `TITLE_ID` | utf8 | **`BLUS30826`** |
| `TITLE` | utf8 | `YAKUZA: Dead Souls` |
| `APP_VER` | utf8 | `01.00` |
| `VERSION` | utf8 | `01.00` |
| `CATEGORY` | utf8 | `DG` |
| `BOOTABLE` | uint32 | 1 |
| `PARENTAL_LEVEL` | uint32 | 9 |
| `PS3_SYSTEM_VER` | utf8 | `03.7300` |
| `ATTRIBUTE` | uint32 | 0 |
| `RESOLUTION` | uint32 | 63 |
| `SOUND_FORMAT` | uint32 | 263 |

**Why this matters:** `TITLE_ID = BLUS30826` is the USA serial, read from the
disc itself. This converts the repo's region assumption into a checked fact for
the disc. `APP_VER = 01.00` matches the `01.00` in Aldo's runtime code filename.

## `PS3_GAME/USRDIR/EBOOT.BIN` (22,029,744 bytes)

| | |
|---|---|
| size | 22,029,744 bytes |
| SHA-256 | `8d03544bf7e71702e70c813342948281b8cb180e9a744425731a1d0c9abf4bca` |
| magic | `SCE\0` — a **SELF** (signed/encrypted ELF) |

**What this means:** the executable is encrypted, as a retail disc should be.
Its code cannot be inspected off-console, so the runtime code addresses in
[`SOURCES.md`](SOURCES.md) **cannot be checked against this disc from a PC**.
That question can only be settled by loading codes on the console.

## How to reproduce

On Windows, with 7-Zip installed:

```
& "C:\Program Files\7-Zip\7z.exe" l "Yakuza - Dead Souls (USA).iso"
& "C:\Program Files\7-Zip\7z.exe" e "Yakuza - Dead Souls (USA).iso" -o. "PS3_GAME\PARAM.SFO"
python tools/parse_sfo.py PARAM.SFO
```

Expect `TITLE_ID = BLUS30826`. 7-Zip may report a UDF "Headers Error" and
"data after the end of archive" on this image; the files still extract correctly,
verified by size.

To check the executable hash:

```
certutil -hashfile EBOOT.BIN SHA256
```

Expect `8d03544bf7e71702e70c813342948281b8cb180e9a744425731a1d0c9abf4bca`.

## Status

- **Disc serial:** confirmed (`BLUS30826`), read from the disc.
- **App version:** confirmed (`01.00`), read from the disc.
- **Runtime code addresses:** still unconfirmed — executable is encrypted.
- **Savepatch:** separate path, does not involve the disc. See
  [`VERIFY_SAVEPATCH.md`](VERIFY_SAVEPATCH.md).
