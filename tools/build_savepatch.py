#!/usr/bin/env python3
"""Build our own BLUS30826.savepatch for Yakuza: Dead Souls (USA).

This is OUR patch file, written from the documented code table, not a copy of
Apollo's. It uses the SavePatch format described at:
  https://bucanero.github.io/apollo-lib/savepatch.html

Why generate instead of hand-typing: every code line is derived from one table
below, so it can be checked mechanically against Apollo's upstream file. If a
value here disagrees with upstream, `--check` fails loudly instead of shipping a
silently-wrong code.

The code values are the original save-editor set (Game Genie For PS3, krustytoe,
www55.atwiki.jp, savedata.jp), the same set Apollo packages. What we add is our
own file layout, our own grouping/defaults, and a per-code test status.

Usage:
    python tools/build_savepatch.py            # write patches/BLUS30826.our.savepatch
    python tools/build_savepatch.py --check    # verify against upstream, write nothing
    python tools/build_savepatch.py --stdout   # print the file
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SERIAL = "BLUS30826"
GAME = "Yakuza: Dead Souls"
TARGET = "USER01"

# ---------------------------------------------------------------------------
# THE CODE TABLE.  Every entry: (title, [code lines], status, note)
# status: "candidate" = not yet tested on hardware. Nothing here is claimed
# verified until VERIFY_SAVEPATCH.md has been run on the console.
# ---------------------------------------------------------------------------
CODES = [
    # --- money & progression ------------------------------------------------
    ("Max Money",
     ["20008B48 3B9AC9FF"], "candidate",
     "999,999,999. Single 32-bit write -- the region test."),
    ("Max EXP",
     ["2001CAFC 05F5E0FF"], "candidate",
     "99,999,999."),
    ("Max Soul Points",
     ["0001CB06 000000FF"], "candidate",
     "8-bit write (255). Watch neighbouring bytes."),
    ("Level 98",
     ["2001ca01 00000062"], "candidate",
     "32-bit write at an ODD offset 0x01CA01. Also zeroes 0x01CA03-04. "
     "Most uncertain code in the set."),

    # --- casino / minigame counters ----------------------------------------
    ("Max Casino Chips",
     ["20008B4C 05F5E0FF"], "candidate", ""),
    ("Max Wooden Tag",
     ["20008B50 05f5E0FF"], "candidate", ""),
    ("Max Mahjong Sticks",
     ["20008B54 05F5E0FF"], "candidate", ""),
    ("Max PachinKO Balls",
     ["20008B74 05F5E0FF"], "candidate", ""),
    ("Max Slots Token",
     ["20008B78 0098967F"], "candidate",
     "999,999 (0x0098967F), not 99,999,999 -- differs from its neighbours."),
    ("Max Zombies Reward Points",
     ["20008B7C 05F5E0FF"], "candidate", ""),

    # --- health -------------------------------------------------------------
    ("9999/9999 HP",
     ["2001CAE4 270F270F"], "candidate",
     "Current and max HP in one dword. Upstream notes the runtime equivalent "
     "affects enemies too."),

    # --- inventory ----------------------------------------------------------
    ("Inf Ammo (clear inventory slots 1-6 first)",
     ["10005B14 00000019",
      "10005B1A 0000FFFF",
      "10005B1C 0000001B",
      "10005B22 0000FFFF",
      "10005B24 0000001D",
      "10005B2A 0000FFFF",
      "10005B2C 0000001F",
      "10005B32 0000FFFF",
      "10005B34 00000021",
      "10005B3A 0000FFFF",
      "10005B3C 00000023",
      "10005B42 0000FFFF"], "candidate",
     "12x 16-bit writes: item ids with count 0xFFFF in slots 1-6. Anything in "
     "those slots is replaced."),
    ("Max All Storage Items (Except Weapons)",
     ["41005BDA 0000270F",
      "412B0008 00000000"], "candidate",
     "16-bit multi-write of 9999 into 299 slots (0x2B ones), stride 8. "
     "Most invasive code here."),
]

# Difficulty is a choose-one group: all four write the same address.
DIFFICULTY = [
    ("Normal",  "10000014 00000101"),
    ("Hard",    "10000014 00000202"),
    ("Ex-Hard", "10000014 00000303"),
    ("Dead Souls/Of The End", "10000014 00000404"),
]

MINIGAME = [
    ("Top Pachinko Payout", "20019EC4 0000270f"),
    ("Top Slots Payout",    "20019EC8 0000270f"),
    ("Cee-Lo",              "20018B84 000F423F"),
    ("Cho-Han",             "20018C14 000F423F"),
    ("Koi-Koi",             "20018CBC 000F423F"),
    ("Oicho-Kabu",          "200196A8 000F423F"),
    ("Roulette",            "20018D48 000F423F"),
    ("Poker",               "20018DD8 000F423F"),
    ("Blackjack",           "20018E64 000F423F"),
    ("Baccarat",            "2001A274 000F423F"),
    ("Boxcelios",           "0001A167 00000064"),
]

CODE_RE = re.compile(r"^[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8}$")


def normalise(line: str) -> str:
    """Upper-case and collapse whitespace so comparisons are exact."""
    return " ".join(line.split()).upper()


def render() -> str:
    out: list[str] = []
    w = out.append

    w(f"; {SERIAL}")
    w(f"; {GAME} (USA)")
    w("; Built by richard1222/Yakuza-dead-souls-cheats")
    w(";")
    w("; Code values: Game Genie For PS3 & krustytoe, with the 9999/9999 HP code")
    w("; from www55.atwiki.jp and the difficulty codes from savedata.jp.")
    w("; This file's layout is ours; the code values are the original set.")
    w(";")
    w("; STATUS: none of these is verified on hardware yet. Test order is in")
    w("; VERIFY_SAVEPATCH.md. Apply with Apollo Save Tool.")
    w(";")
    w("; Target file: " + TARGET)
    w("")
    w(f":{TARGET}")
    w("")

    w("[GROUP:Money and progression]")
    for title, lines, status, note in CODES[:4]:
        w(f"[{title}]")
        if note:
            for chunk in _wrap(note):
                w(f"; {chunk}")
        for ln in lines:
            w(ln)
        w("")

    w("[GROUP:Casino and minigame counters]")
    for title, lines, status, note in CODES[4:10]:
        w(f"[{title}]")
        if note:
            for chunk in _wrap(note):
                w(f"; {chunk}")
        for ln in lines:
            w(ln)
        w("")

    w("[GROUP:Health]")
    title, lines, status, note = CODES[10]
    w(f"[{title}]")
    for chunk in _wrap(note):
        w(f"; {chunk}")
    for ln in lines:
        w(ln)
    w("")

    w("[GROUP:Difficulty Modifier (Choose One)]")
    w("; All four write the same address 0x14. The last one applied wins.")
    for name, ln in DIFFICULTY:
        w(f"[{name}]")
        w(ln)
        w("")

    w("[GROUP:Inventory]")
    for title, lines, status, note in CODES[11:]:
        w(f"[{title}]")
        if note:
            for chunk in _wrap(note):
                w(f"; {chunk}")
        for ln in lines:
            w(ln)
        w("")

    w("[GROUP:Minigame Challenge]")
    for name, ln in MINIGAME:
        w(f"[{name}]")
        w(ln)
        w("")
    w("[GROUP:\\]")

    return "\n".join(out).rstrip("\n") + "\n"


def _wrap(text: str, width: int = 72) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for word in words:
        if len(cur) + len(word) + 1 > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return lines


def all_code_lines() -> list[str]:
    """Every code line this builder emits, normalised, in order."""
    lines: list[str] = []
    for _, code_lines, _, _ in CODES:
        lines += code_lines
    lines += [ln for _, ln in DIFFICULTY]
    lines += [ln for _, ln in MINIGAME]
    return [normalise(l) for l in lines]


def check_against_upstream(path: str) -> int:
    """Compare our code set with Apollo's upstream file, line by line."""
    if not os.path.exists(path):
        print(f"upstream not found: {path}")
        print("run: python tools/fetch_savepatch.py")
        return 1

    upstream = [normalise(l) for l in open(path, encoding="utf-8").read().splitlines()
                if CODE_RE.match(l.strip())]
    ours = all_code_lines()

    missing = [c for c in upstream if c not in ours]
    extra = [c for c in ours if c not in upstream]

    print(f"upstream code lines : {len(upstream)}")
    print(f"our      code lines : {len(ours)}")
    print()
    print("in UPSTREAM but not in ours:", missing or "none")
    print("in OURS but not in upstream:", extra or "none")
    print()

    if missing or extra:
        print("MISMATCH -- our patch is not equivalent to the published set.")
        return 1
    print("OK -- every code line matches the published set exactly.")
    print("(Order and titles are ours; the address/value pairs are identical.)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join("patches", f"{SERIAL}.our.savepatch"))
    ap.add_argument("--check", action="store_true",
                    help="verify code lines against the fetched upstream patch")
    ap.add_argument("--stdout", action="store_true", help="print, do not write")
    args = ap.parse_args()

    text = render()

    # self-checks: never emit a malformed line
    problems = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s.startswith((";", ":", "[", "#")):
            continue
        if not CODE_RE.match(s):
            problems.append(f"malformed code line: {ln!r}")
    if problems:
        print("REFUSING TO WRITE -- builder produced bad output:")
        for p in problems:
            print("  " + p)
        return 1

    if args.stdout:
        print(text, end="")
        return 0

    if args.check:
        return check_against_upstream(os.path.join("patches", f"{SERIAL}.savepatch"))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="ascii", newline="\n") as f:
        f.write(text)
    ncode = len(all_code_lines())
    print(f"wrote {args.out}")
    print(f"  {len(text.splitlines())} lines, {ncode} code lines encoded")
    print(f"  ASCII, LF endings, no BOM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
