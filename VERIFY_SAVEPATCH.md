# Savepatch verification plan — BLUS30826

How to verify the USA savepatch codes on real hardware, in an order that fails
cheap and catches problems early.

**Rule for this repo:** a code goes in the verified table only after it has been
applied on the console and its effect *seen in game*. Everything below is the
procedure; the results table is in the [README](README.md#what-is-verified).

---

## Why savepatch first

The savepatch route was chosen over runtime codes first because it:

- needs **no cheat engine** running (no Artemis config, no `.ncl` loading)
- is **non-destructive if you back up** — you edit a copy of the save
- is **easy to observe** — money and item counts are on screen immediately

It also immediately tests the single most valuable open question in the repo:
**does a `BLUS30826`-labelled patch actually apply to the USA save on hardware?**
If yes, the whole region question is settled for the save side.

## What you need

1. Your USA copy of the game, and a save file that has been played at least far
   enough to have money and an inventory.
2. **Apollo Save Tool** on the console (CFW), or `apollo-patcher` in a browser /
   the CLI, for applying the patch.
3. A **backup of the save**, taken before any edit.

## The patch

Apollo's own `BLUS30826.savepatch`, unmodified:

<https://cdn.jsdelivr.net/gh/bucanero/apollo-patches@main/PS3/BLUS30826.savepatch>

Target file inside the save folder: `USER01`.

## What each code does (decoded)

Decoded with `tools/decode_savepatch.py` against the Apollo Save Wizard format
reference. This is the plain-English meaning of each line, so a result can be
read unambiguously.

| code | operation | address | value | observable in game |
|---|---|---|---|---|
| Max Money | 32-bit write | `0x008B48` | `0x3B9AC9FF` (999,999,999) | money display |
| Max EXP | 32-bit write | `0x01CAFC` | `0x05F5E0FF` (99,999,999) | EXP bar / level |
| Max Soul Points | 8-bit write | `0x01CB06` | `0xFF` (255) | soul points |
| Max Casino Chips | 32-bit write | `0x008B4C` | `0x05F5E0FF` | casino chip count |
| Max Wooden Tag | 32-bit write | `0x008B50` | `0x05F5E0FF` | minigame counter |
| Max Mahjong Sticks | 32-bit write | `0x008B54` | `0x05F5E0FF` | minigame counter |
| Max PachinKO Balls | 32-bit write | `0x008B74` | `0x05F5E0FF` | minigame counter |
| Max Slots Token | 32-bit write | `0x008B78` | `0x0098967F` | minigame counter |
| Max Zombies Reward Points | 32-bit write | `0x008B7C` | `0x05F5E0FF` | reward points |
| Max All Storage Items | 16-bit **multi-write** | `0x005BDA`+8×n | `0x270F` (9999) ×**299 slots** | storage box contents |
| Inf Ammo | 12× 16-bit writes | `0x005B14`…`0x005B42` | item ids + `0xFFFF` counts | ammo count in slots 1–6 |
| 9999/9999 HP | 32-bit write | `0x01CAE4` | `0x270F270F` (9999/9999) | HP bar (see risk note) |
| Level 98 | 32-bit write | `0x01CA01` | `0x62` (98) | character level |
| Difficulty ×4 | 16-bit write | `0x000014` | `0x0101`/`0202`/`0303`/`0404` | difficulty shown on load |
| Minigame payouts ×9 | 32-bit writes | `0x018B84`…`0x01A274` | `0x000F423F` (999,999) | payout amounts |
| Boxcelios | 8-bit write | `0x01A167` | `0x64` (100) | minigame |

The `Max All Storage Items` line is `41005BDA 0000270F` / `412B0008 00000000`
— a 16-bit multi-write of 9999 repeated **299** times, 8 bytes apart, covering
`0x005BDA`–`0x00652B`. It is the single most invasive code in the set.

## Order to test in

Test in this order deliberately: cheapest and least destructive first, so a
problem is found before anything risky is applied.

### Step 0 — baseline and backup

1. Make a save with some money, some items, and a known level.
2. **Copy the save off the console.** This is the rollback.
3. Note down: money, EXP, level, HP, and one storage item count.

If anything later goes wrong, restore this copy. Do not skip this.

### Step 1 — Max Money (single 32-bit write, trivially observable)

1. Apply only `[Max Money]`.
2. Load the save.
3. Money should read **999,999,999**.

This one test settles whether the patch applies to the USA save at all. If money
is wrong, stop — nothing further will help until that's understood.

### Step 2 — Max EXP and Max Soul Points

Apply both. Load. EXP and soul points should be maxed.

Also watch for corruption of *neighbouring* values, since `Max Soul Points` is
only an 8-bit write.

### Step 3 — Difficulty (single 16-bit write at 0x14)

Apply **exactly one** of the four difficulty codes — they all write `0x000014`
and the last one applied wins. Load and confirm the difficulty.

### Step 4 — Minigame payouts

Apply one at a time if convenient; they are independent addresses and easy to
read. Payouts should be 999,999.

### Step 5 — [Level 98] — the one to watch

Apply this **on its own**, onto a freshly restored backup, and check:

- Does the level read 98?
- Are EXP / HP / soul points still sane afterwards?

This code is the one anomaly in the file: it is a **32-bit write at an odd
offset**, `0x01CA01`, where the other stat codes sit at `0x01CAFC` (EXP) and
`0x01CAE4` (HP). A 32-bit write there also sets bytes `0x01CA03` and `0x01CA04`
to zero. Whether that clobbers neighbouring data is **not knowable from the
patch file** — it needs this test.

If level 98 shows correctly and nothing else breaks, the code is fine and this
note can be dropped. If something else breaks, that is the finding, and this
code should be marked accordingly.

### Step 6 — 9999/9999 HP — the other risk

The code writes `0x270F270F` to `0x01CAE4`: that is 9999 in the low half and
9999 in the high half, i.e. current and max HP in one dword.

Watch for: HP stuck at 9999 but **enemies also becoming very tough**, since the
original Aldo runtime note says the equivalent runtime code affects enemies too.
Also confirm you can still take damage and die — a save with invulnerability
baked in may be undesirable long-term.

### Step 7 — Max All Storage Items (last, most invasive)

Do this **last**, on a backed-up save, because it writes 299 slots.

1. Apply and load.
2. Check the storage box is full of 9999-stacks.
3. Check the game does not crash when opening the box or scrolling it.

Known quirk from the patch author: this fills storage, and the Inf Ammo code
warns that item slots 1–6 must be cleared or they will be overwritten.

### Step 8 — Inf Ammo

Per the patch's own note: **clear inventory slots 1–6 first**, or the code will
replace whatever is there. Apply, then confirm ammo reads as infinite in those
slots and the weapons still fire.

## Things that would count as a failure

Record these honestly rather than working around them:

- Money does not change → the patch is not landing on the USA save; the region
  label is wrong, and that is a headline finding.
- Values correct but the save corrupts on reload → write is landing but the
  layout differs.
- Level 98 sets the level but breaks an adjacent stat → the odd offset matters.
- Any code crashes the game on load.

## Credit

The patch is authored by **Game Genie For PS3** and **krustytoe**, with the
9999 HP code from **www55.atwiki.jp** and the difficulty codes from
**savedata.jp**, packaged by **bucanero / Apollo Save Tool**. This repo only
verifies and documents it.
