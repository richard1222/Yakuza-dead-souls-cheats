# Source sweep — Yakuza: Dead Souls cheats (as of 2026-10-20)

Every source found that carries cheats or codes for Yakuza: Dead Souls, what it
covers, and whether it is usable for the **USA** disc (BLUS-30826).

Sources are grouped by whether they are **runtime** codes (patch memory while the
game runs; need Artemis/NetCheat on CFW) or **save edits** (modify the save file;
no cheat engine needed).

---

## 1. Runtime codes (Artemis / NetCheat)

### 1a. Aldo's PS3 Artemis Codelist Database — USA set (UNLABELLED)

- **Index:** <http://ps3.aldostools.org/codelist.html>
- **Actual file host:** `aldostools/webMAN-MOD` repo,
  `_Projects_/codelists/Yakuza Dead Souls 01.00.ncl`
- **Direct:**
  `https://raw.githubusercontent.com/aldostools/webMAN-MOD/master/_Projects_/codelists/Yakuza%20Dead%20Souls%2001.00.ncl`
- **Size:** 1,199 bytes · **Author:** jgduff1 · **Version field:** 01.00
- **Coverage:** a **non-EU build**, almost certainly USA. **The file does not
  name a serial** — the titleid column is blank in Aldo's index, and the .ncl
  contains only a name, no `PARAM.SFO` / alternative-names block. See
  [How the region was established](#how-the-region-was-established) below.
  This is the single most useful find of the sweep.

Codes, each with a Memory and an ASM variant (verbatim from the file):

| cheat | code type | address(es) |
|---|---|---|
| Infinite Ammo + No Reload | Memory | `01536720 0004`, `3476E924 00000005` |
| Infinite Ammo + No Reload | ASM | `00AAA9A8 60000000`, `0052D1C0 60000000` |
| Max Level On 1 Kill + Lots Of Ability Points | Memory | `0154BDB8 00000050` |
| Max Level On 1 Kill + Lots Of Ability Points | ASM | `00AAEFB8 905E0018`, `00AAEFBC 905E001C` |
| Lots + Infinite Ability Points On Start | Memory | `0154BDC6 E600` |
| Lots + Infinite Ability Points On Start | ASM | `00AAF030 98C30026` |
| Infinite Health | Memory | `0154BDA4 35981264` |
| Infinite Health | ASM | `002E7EC0 60000000`, `002E7E9C 60000000` |
| Lots Of Money When Buy + Sell + Gain | Memory | `01537E08 00013880` |
| Lots Of Money When Buy + Sell + Gain | ASM | `00AAD658 93BC0000` |
| Partner Has Infinite Medkit | Memory | `308EE23C 00000003` |
| Partner Has Infinite Medkit | ASM | `00D47424 30840000`, `00D47428 90830018` |
| Infinite Items | Memory | `01534DE8 00000001` |
| Infinite Items | ASM | `00AA9748 30630000`, `00AA9768 B0640006`, `00AA977C B0A40000`, `00AA9780 B0A40002`, `00AA9788 B0A40004`, `00AA9790 B0A40006` |

Note carried in the file itself: *"Infinite Health also affects enemies, but the
Shotgun still kills them."*

### 1b. Aldo's database — Europe set

- **File:** `Yakuza Dead Souls BLES01399 01.00.ncl` (2,610 bytes)
- **Author:** jijibecali · carries an `Alternative Names` block
  (*"Ryu Ga Gotoku Of The End"*)
- **Coverage:** Europe, named in the filename. Its code addresses differ from the
  unlabelled set for the same cheats — which is the evidence that they are two
  different builds (see below).

| cheat | addresses |
|---|---|
| Infinite Money | `01537E08 1F000000` |
| Max Exp | `0154BDBC 00FF0000` |
| 255 Balls | `0154BDC6 FF` |
| Have Items | ~119 addresses, `01534DD5` … `015366F8` |

Note: the EU set is **not** a superset of the unlabelled set. They cover
overlapping but different cheats, with different values and different code
addresses. Neither one can be substituted for the other.

### How the region was established

The unlabelled set is *claimed* as US here, so the reasoning is stated rather
than assumed:

1. **Aldo's own index lists Dead Souls twice** — once with a blank serial
   (1,199 bytes) and once as `BLES01399` (2,610 bytes). Two entries means two
   targets, and one of them is Europe.
2. **The code addresses differ from the EU set for the same cheat.** Compiled
   code addresses are per-executable, so different addresses ⇒ different builds:
   - max level on 1 kill: unlabelled `00AAEFB8` vs GameHacking EU `00AAEFAC`
   - infinite health: unlabelled `002E7EC0`/`002E7E9C` vs GameHacking EU `01023EDC`/`01023F20`
3. **The three addresses that DO match** (`01534DE8`, `01537E08`, `0154BDC6`)
   are data/stat offsets (money, items, points) that mean the same thing in both
   sets. Shared data offsets are expected; shared *code* offsets would not be.
4. **jgduff1's PKG thread (1d) names BLUS30826** alongside BLES01399, and the
   cheat list matches this file's cheats closely.

That is enough to treat it as the US set for testing, but **not** enough to
publish it labelled "USA" as established fact. Treat it as *US, to be confirmed
on hardware* — which is exactly what our repo's verify-on-hardware rule is for.

### 1c. GameHacking.org — Europe only, 4 codes

- **Entry:** <https://gamehacking.org/game/145966> (BLES-01399)
- **Author:** luc-ita · **Device:** NetCheat PS3
- **No USA entry exists.**

| cheat | codes |
|---|---|
| 1-Hit Kill *(see notes)* | `002C5488 38600000`, `002C5490 80BE0D64`, `002C5494 B0650004` |
| Always full of life | `01023EDC 80850194`, `01023F20 83DF0D64`, `01023F28 B3BE0004` |
| Kill an enemy to reach max level | `00AAEFAC 60000000` |
| Sniper gauge always full | `002C7548 FF800890`, `002C7550 60000000` |

### 1d. jgduff1's Cheats PKG collection (lebonforum / playgame)

- **Thread:** <https://playgame.lebonforum.com/t860p30-cheats-pkgs-pour-cfw-v4-xx-par-jgduff>
- **Coverage:** explicitly **BLES01399 & BLUS30826 & NPUB31509** — the only
  source found that names the USA serial. Distributed as ready-made **PKG**
  cheat packages, 8 variants.

Cheat list: Infinite Ammo/No Reload, Infinite Items, Lots Of Money When
Buy/Sell/Gain, Max Level On 1 Kill, Lots/Infinite Ability Points On Start,
Partner Has Infinite Medkit.

Notes from the author: install Infinite Ammo/No Reload *after* the
"shoot and reload" tutorial; disable Infinite Items before selling.

---

## 2. Save edits (no cheat engine needed)

### 2a. Apollo Save Tool — USA savepatch (28 codes)

- **Page:** <https://bucanero.github.io/apollo-patches/PS3/BLUS30826.html>
- **Raw:**
  `https://cdn.jsdelivr.net/gh/bucanero/apollo-patches@main/PS3/BLUS30826.savepatch`
- **Repo:** `bucanero/apollo-patches` (GPL-3.0) · 1,527 bytes
- **Credit in file:** *"From Game Genie For PS3 & krustytoe"*, plus
  `www55.atwiki.jp` (9999/9999 HP) and `savedata.jp` (difficulty)
- **Target file:** `USER01`

Codes: Level 98, Max Money, Max EXP, Max Soul Points, Max Casino Chips, Max
Wooden Tag, Max Mahjong Sticks, Max PachinKO Balls, Max Slots Token, Max
Zombies Reward Points, Max All Storage Items (except weapons), Inf Ammo, 9999 HP,
difficulty modifier (Normal/Hard/Ex-Hard/Dead Souls), and minigame
payouts (Pachinko, Slots, Cee-Lo, Cho-Han, Koi-Koi, Oicho-Kabu, Roulette, Poker,
Blackjack, Baccarat, Boxcelios).

**USA-only difference:** the US set adds **"Level 98"** (`2001ca01 00000062`),
which the EU savepatch does not have.

Most addresses are identical between US and EU savepatches (money `20008B48`,
EXP `2001CAFC`, HP `2001CAE4`, minigames, difficulty). Save layout is largely
shared; the executable is not.

### 2b. Apollo Save Database — complete saves

- **Page:** <https://bucanero.github.io/apollo-saves/PS3/BLUS30826/>
- Two 100%-complete BLUS30826 saves (`00000001.zip` profile, `00000002.zip`).

### 2c. save-editor.com PS3 code list

- **Page:**
  <https://www.save-editor.com/tools_original/wse_ps3_save_editor_code_title.html?id=BLES01399>
- Same code set as Apollo's EU savepatch. Europe.

---

## 3. Trophy / unlock guides (not cheats)

These list trophies and in-game unlocks only. No memory addresses.

- GameRevolution: <https://www.gamerevolution.com/guides/54671-yakuza-dead-souls-ps3-cheats>
- ChapterCheats: <https://www.chaptercheats.com/cheats/playstation3/103567/yakuza-dead-souls-cheat-codes>
- GameSpot: <https://www.gamespot.com/games/yakuza-dead-souls/cheats/>
- GameFAQs item guide: <https://gamefaqs.gamespot.com/ps3/998171-yakuza-dead-souls/faqs/79387/healing-cheat-and-miscellaneous-items>

In-game unlocks: beat the game → 1,000,000 yen, New Game+, Dead Souls
difficulty, Extra Hard difficulty.

---

## 4. What this means for our repo

**Runtime codes: a non-EU (US) set exists (1a), unconfirmed.** It was sitting
unlabelled in Aldo's database, which is why earlier searches missed it. It is the
right starting point, but it has not been run on a US console by anyone we can
see, and the file does not name a serial. Verify, do not re-derive.

**Save edits: a real USA set exists (2a).** 28 codes, explicitly labelled
`BLUS30826` by Apollo. Directly usable.

**So the honest position is:** our repo is not "make cheats from nothing." It is
**take the two existing USA sets, verify each code on hardware, document them
properly with credit, and publish a clean, region-labelled package** — which does
not exist today. The gap is a *verified, credited, USA-labelled* collection, not
a missing address list.

**Untested:** nothing here has been run on our console yet. Every code above is
reported by its author, not confirmed by us. The US runtime set in particular
carries a region label we inferred (see §1a) rather than read.

**Credit owed:** jgduff1 (US runtime set, and the only PKG naming BLUS30826),
jijibecali (EU runtime set), luc-ita (GameHacking), krustytoe / www55.atwiki.jp /
savedata.jp (save edits), bucanero / Apollo (savepatch packaging).

---

## 5. Serial reference

| region | serial | runtime set available | save set available |
|---|---|---|---|
| USA | BLUS-30826 | yes (1a, unlabelled in Aldo — region inferred; also 1d PKG names it) | yes (2a, 28 codes, labelled) |
| Europe | BLES-01399 | yes (1b, 1c, 1d) | yes |
| Japan | BLJM60316 | not found | not found |
| PSN US | NPUB31509 | listed in 1d PKG | not found |
| PSN EU | NPEB02034 | not found | not found |
