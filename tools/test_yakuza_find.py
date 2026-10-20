"""Prove the diff logic in tools/yakuza_find.ps1 actually works.

Why this exists: yakuza_find.ps1 hunts for a value's address by diffing two
memory snapshots. If that diff logic is wrong, it will hand back wrong
addresses -- and a wrong address written afterwards is exactly the failure mode
this whole project has been trying to avoid.

So we build snapshots with a KNOWN answer and check the tool finds it.

The PS3 is big-endian, so a word 0x00000780 = 1920 is the bytes 00 00 07 80.
The swap test below exists because decoding little-endian would silently find
NOTHING, and that bug already cost time once on this console.

Cases:
  1. exactly one word 1920 -> 557          (must find it, at the right address)
  2. no change between snapshots           (must find nothing)
  3. two words make the same transition    (must find both)
  4. float 1.0 and 0x55555555 fill present (must be filtered out)
  5. big-endian check: byte order matters  (proves the swap would be caught)
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).with_name("yakuza_find.ps1")
POWERSHELL = "powershell"

BASE = 0x30000000


def make_snapshot(path: Path, words: list[int]) -> None:
    payload = {
        "base": f"0x{BASE:08X}",
        "end": f"0x{BASE + len(words) * 4:08X}",
        "pid": "0x0",
        "title": "BLUS30826",
        "words": words,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def diff(a: Path, b: Path, *extra: str) -> tuple[int, str]:
    cmd = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", str(TOOL), "-Mode", "diff", "-A", str(a), "-B", str(b), *extra]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def addr_of(index: int) -> str:
    return f"0x{BASE + index * 4:08X}"


def main() -> int:
    fails = 0
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)

        # ---- 1. one word changes 1920 -> 557 --------------------------------
        a, b = d / "a1.json", d / "b1.json"
        wa = [0] * 64
        wb = [0] * 64
        wa[10], wb[10] = 1920, 557          # the real transition
        wa[11] = wb[11] = 159               # stable neighbour
        make_snapshot(a, wa)
        make_snapshot(b, wb)
        rc, out = diff(a, b, "-From", "1920", "-To", "557")
        want = addr_of(10)
        ok = want in out and out.count("0x3000") >= 1 and "1 candidate" in out
        print(f"  [1] single 1920->557 change     rc={rc}  expect {want}  "
              f"{'PASS' if ok else 'FAIL'}")
        fails += 0 if ok else 1
        if not ok:
            print("      output:", out.strip()[:300])

        # ---- 2. identical snapshots -> nothing ------------------------------
        a2, b2 = d / "a2.json", d / "b2.json"
        same = [7] * 64
        make_snapshot(a2, same)
        make_snapshot(b2, same)
        rc, out = diff(a2, b2)
        ok = "No candidates" in out
        print(f"  [2] no change at all            rc={rc}  expect none      "
              f"{'PASS' if ok else 'FAIL'}")
        fails += 0 if ok else 1

        # ---- 3. two words, same transition ----------------------------------
        a3, b3 = d / "a3.json", d / "b3.json"
        wa = [1] * 64
        wb = [1] * 64
        wa[5], wb[5] = 1920, 557
        wa[40], wb[40] = 1920, 557
        make_snapshot(a3, wa)
        make_snapshot(b3, wb)
        rc, out = diff(a3, b3, "-From", "1920", "-To", "557")
        ok = addr_of(5) in out and addr_of(40) in out and "2 candidate" in out
        print(f"  [3] two matching transitions    rc={rc}  expect both    "
              f"{'PASS' if ok else 'FAIL'}")
        fails += 0 if ok else 1
        if not ok:
            print("      output:", out.strip()[:300])

        # ---- 4. junk fills must be filtered ---------------------------------
        a4, b4 = d / "a4.json", d / "b4.json"
        wa = [0] * 8
        wb = [0] * 8
        wa[0], wb[0] = 100, 0x3F800000      # becomes float 1.0
        wa[1], wb[1] = 100, 0x55555555      # becomes free fill
        wa[2], wb[2] = 100, 0xAAAAAAAA      # becomes free fill
        make_snapshot(a4, wa)
        make_snapshot(b4, wb)
        rc, out = diff(a4, b4)
        ok = "No candidates" in out
        print(f"  [4] junk fills filtered        rc={rc}  expect none      "
              f"{'PASS' if ok else 'FAIL'}")
        fails += 0 if ok else 1
        if not ok:
            print("      output:", out.strip()[:300])

        # ---- 5. big-endian proof --------------------------------------------
        # 1920 = 0x00000780. Big-endian bytes: 00 00 07 80.
        # Little-endian would be 80 07 00 00 = 0x80070000 as read big-endian.
        a5, b5 = d / "a5.json", d / "b5.json"
        wa = [0] * 8
        wb = [0] * 8
        wa[3], wb[3] = 1920, 557
        make_snapshot(a5, wa)
        make_snapshot(b5, wb)
        # correct (big-endian) values must match
        rc, out = diff(a5, b5, "-From", "1920", "-To", "557")
        ok_be = "1 candidate" in out
        # byte-swapped values must NOT match
        rc2, out2 = diff(a5, b5, "-From", str(0x80070000), "-To", str(0x2D020000))
        ok_sw = "No candidates" in out2
        ok = ok_be and ok_sw
        print(f"  [5] big-endian, not swapped     rc={rc}  expect be-only  "
              f"{'PASS' if ok else 'FAIL'}")
        fails += 0 if ok else 1
        if not ok:
            print("      be output:", out.strip()[:200])
            print("      sw output:", out2.strip()[:200])

    print()
    if fails:
        print(f"  {fails} case(s) FAILED")
        return 1
    print("  all cases PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
