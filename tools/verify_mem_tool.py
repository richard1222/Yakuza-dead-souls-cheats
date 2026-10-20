"""Check tools/yakuza_mem.ps1 against the codelist.

Why this exists: the tool ships a hardcoded copy of the code table. If that
copy drifts from codelists\\Yakuza Dead Souls BLUS30826 01.00.ncl, the tool
would write values that were never verified. This asserts they match.

Run from the repo root:   py tools/verify_mem_tool.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NCL = ROOT / "codelists" / "Yakuza Dead Souls BLUS30826 01.00.ncl"
PS1 = ROOT / "tools" / "yakuza_mem.ps1"

# "0 ADDR VALUE" — the codelist code-line format.
CODE_RE = re.compile(r"^0 ([0-9A-Fa-f]{8}) ([0-9A-Fa-f]{1,8})\s*$")
# addr = "ADDR"; val = "VALUE"  — the PowerShell table format.
PS1_RE = re.compile(
    r'addr\s*=\s*"([0-9A-Fa-f]{8})";\s*val\s*=\s*"([0-9A-Fa-f]{1,8})"'
)


def main() -> int:
    if not NCL.is_file():
        print(f"error: codelist not found: {NCL}")
        return 1
    if not PS1.is_file():
        print(f"error: tool not found: {PS1}")
        return 1

    ncl_text = NCL.read_text(encoding="utf-8")
    ncl_codes = sorted(
        (m.group(1).upper(), m.group(2).upper())
        for m in (CODE_RE.match(line.strip()) for line in ncl_text.splitlines())
        if m
    )

    ps1_text = PS1.read_text(encoding="utf-8")
    ps1_codes = sorted(
        (m.group(1).upper(), m.group(2).upper())
        for m in PS1_RE.finditer(ps1_text)
    )

    print(f"  codelist code lines : {len(ncl_codes)}")
    print(f"  ps1 table entries   : {len(ps1_codes)}")
    print()

    ncl_set, ps1_set = set(ncl_codes), set(ps1_codes)
    missing = sorted(ncl_set - ps1_set)
    extra = sorted(ps1_set - ncl_set)

    ok = True
    if len(ncl_codes) == 0:
        print("  FAIL: found 0 code lines in the codelist — the parser is wrong,")
        print("        which means this check proves nothing. Fix it before trusting.")
        ok = False
    if missing:
        print("  FAIL: in codelist but NOT in the tool (tool would miss these):")
        for a, v in missing:
            print(f"    {a} {v}")
        ok = False
    if extra:
        print("  FAIL: in the tool but NOT in the codelist (never verified!):")
        for a, v in extra:
            print(f"    {a} {v}")
        ok = False

    if ok:
        print(f"  PASS: {len(ncl_codes)}/{len(ncl_codes)} identical — tool cannot drift")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
