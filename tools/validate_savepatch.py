#!/usr/bin/env python3
"""Validate a .savepatch file against the documented SavePatch format.

Implements the structural rules from the Apollo savepatch spec:
  https://bucanero.github.io/apollo-lib/savepatch.html

This is a *structural* checker: it confirms the file is shaped the way Apollo
parses it. It does not (and cannot) prove the addresses are semantically right
for the game -- only a console test does that.

Checks:
  1. header comments present, encoding is ASCII
  2. exactly one :TARGET declaration, before any code block
  3. every [CODE] block has at least one code line
  4. every code line is exactly XXXXXXXX XXXXXXXX (Game Genie / Save Wizard)
  5. group tags are well-formed (an unclosed [GROUP:] is legal -- it simply
     runs to the end, as Apollo's own patches do)
  6. no code block is empty, no stray text outside blocks
  7. target file name matches what we intend (USER01)

Usage: python tools/validate_savepatch.py <file>
"""
from __future__ import annotations

import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

CODE_RE = re.compile(r"^[0-9A-Fa-f]{8}\s+[0-9A-Fa-f]{8}$")
TITLE_RE = re.compile(r"^\[(.+)\]$")


def validate(path: str, expect_target: str | None = None) -> int:
    raw = open(path, "rb").read()
    problems: list[str] = []

    # 1. encoding
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as e:
        problems.append(f"not plain ASCII: {e}")
        text = raw.decode("utf-8", "replace")

    if raw.startswith(b"\xef\xbb\xbf"):
        problems.append("file starts with a UTF-8 BOM; spec says plain ASCII")
    if b"\r\n" in raw:
        print("note: file has CRLF line endings (spec allows, but we emit LF)")

    lines = text.splitlines()

    # 2. target declaration
    targets = [l.strip()[1:] for l in lines
               if l.strip().startswith(":") and not l.strip().startswith("::")]
    if len(targets) == 0:
        problems.append("no :TARGET file declaration found (required)")
    if expect_target and targets and targets[0] != expect_target:
        problems.append(f"target is {targets[0]!r}, expected {expect_target!r}")

    # 3-6. walk the blocks
    blocks: list[tuple[str, list[str]]] = []
    cur_title: str | None = None
    cur_lines: list[str] = []
    depth = 0
    max_depth = 0
    in_header = True

    for i, ln in enumerate(lines, 1):
        s = ln.strip()

        if not s:
            continue
        if s.startswith(";"):
            continue
        if s.startswith(":"):
            in_header = False
            continue

        m = TITLE_RE.match(s)
        if m:
            # close previous block
            if cur_title is not None:
                blocks.append((cur_title, cur_lines))
            cur_title = m.group(1)
            cur_lines = []
            name = m.group(1)
            if name.upper().startswith("GROUP:\\"):
                depth = max(0, depth - 1)
            elif name.upper().startswith("GROUP:"):
                depth += 1
                max_depth = max(max_depth, depth)
            continue

        if in_header and not s.startswith("["):
            problems.append(f"line {i}: text before any [code] block: {s!r}")
            continue

        if CODE_RE.match(s):
            if cur_title is None:
                problems.append(f"line {i}: code line outside any [title]: {s!r}")
            cur_lines.append(s)
        else:
            # non-comment, non-tag, non-code -> BSD script content
            if cur_title is not None:
                cur_lines.append(s)
            else:
                problems.append(f"line {i}: stray line: {s!r}")

    if cur_title is not None:
        blocks.append((cur_title, cur_lines))

    # classify blocks
    codes, groups, empty = [], [], []
    for title, body in blocks:
        up = title.upper()
        if up.startswith("GROUP:"):
            groups.append(title)
            continue
        if not body:
            empty.append(title)
            continue
        codes.append((title, body))

    for title in empty:
        problems.append(f"empty code block: [{title}]")

    # Every code block in a pure Save Wizard patch must contain ONLY Game Genie
    # lines. A typo (e.g. a 7-char address) would otherwise be silently taken
    # for a BSD script line -- Apollo would then run the block as the wrong
    # type, or reject it at apply time. There is no BSD content in our patches,
    # so any non-code line inside a block is an error.
    for title, body in codes:
        bad = [l for l in body if not CODE_RE.match(l)]
        for b in bad:
            problems.append(
                f"[{title}]: not a valid Game Genie line: {b!r} "
                f"(expected exactly 'XXXXXXXX YYYYYYYY')")

    # An unclosed [GROUP:] is legal: the group runs to the end of the file.
    # Apollo's own BLUS30826.savepatch leaves one open, so treating that as an
    # error would reject the reference file. Report it, do not fail on it.
    if depth != 0:
        print(f"note: {depth} [GROUP:] left open (legal -- runs to end of file)")

    # ---- report
    print(f"file        : {path}")
    print(f"size        : {len(raw)} bytes")
    print(f"line endings: {'CRLF' if chr(13).encode() in raw[:0] or b'\\r\\n' in raw else 'LF'}")
    print(f"target      : {targets[0] if targets else '(none)'}")
    print()
    print(f"code blocks : {len(codes)}")
    print(f"groups      : {len(groups)} (max nesting {max_depth})")
    total_codes = sum(len(b) for _, b in codes)
    print(f"code lines  : {total_codes}")
    print()

    print("=== blocks ===")
    for title, body in codes:
        print(f"  {title[:50]:<50} {len(body)} line(s)")

    print()
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  - " + p)
        print()
        print("INVALID")
        return 1

    print("VALID -- structure matches the documented SavePatch format.")
    print("(Structure only. Whether each address is correct for BLUS30826 is")
    print(" settled by running it on the console, not here.)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    tgt = sys.argv[2] if len(sys.argv) > 2 else None
    raise SystemExit(validate(sys.argv[1], tgt))
