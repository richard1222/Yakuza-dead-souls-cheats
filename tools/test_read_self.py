"""Self-test for tools/read_self.py.

Tests run against synthetic files with known properties, so a failure here is
about the tool, not about the game. Every case states the expected outcome,
and the expected outcome was decided BEFORE running the code.

Cases:
  1. a random file with no magic       -> exit 2, "not a SELF"
  2. a plain ELF header                -> exit 0, reported as plain ELF
  3. a truncated "SCE\\0" file         -> exit 2, refused, no traceback
  4. a real SELF header + random rest  -> exit 0, ciphertext from offset 0
  5. a header + a truly plaintext tail -> boundary found at the tail
  6. a missing file                    -> exit 1
  7. a zero-length file                -> exit 2
"""
from __future__ import annotations

import io
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).with_name("read_self.py")
PY = sys.executable

HDR_FMT = ">4sIHHIQQQQQQQQQQQ"


def make_self_header() -> bytes:
    """A SELF header shaped like the real one (header_size 0x980)."""
    return struct.pack(
        HDR_FMT,
        b"SCE\x00", 2, 0x16, 1, 0x410, 0x980, 0x1501C30, 3, 0x70, 0x90,
        0xD0, 0x1501DB0, 0x290, 0x390, 0x3C0, 0x70,
    )


def run(path: Path, *extra: str) -> tuple[int, str]:
    proc = subprocess.run(
        [PY, str(TOOL), str(path), *extra],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)

        # 1. random bytes, no magic -> exit 2
        p = d / "random.bin"
        p.write_bytes(os.urandom(8192))
        rc, out = run(p)
        ok = rc == 2 and "not a SELF" in out
        print(f"  [1] random 8192 B, no magic          rc={rc} expect 2  "
              f"{'PASS' if ok else 'FAIL'}")
        failures += 0 if ok else 1

        # 2. plain ELF -> exit 0, says plain ELF
        p = d / "plain.elf"
        p.write_bytes(b"\x7fELF" + b"\x02\x02\x01" + b"\x00" * 8192)
        rc, out = run(p)
        ok = rc == 0 and "plain ELF" in out and "NOT a SELF" in out
        print(f"  [2] plain ELF header                 rc={rc} expect 0  "
              f"{'PASS' if ok else 'FAIL'}")
        failures += 0 if ok else 1

        # 3. truncated SELF -> exit 2, no traceback
        p = d / "truncated.bin"
        p.write_bytes(b"SCE\x00" + b"\x00" * 40)
        rc, out = run(p)
        ok = rc == 2 and "Traceback" not in out
        print(f"  [3] truncated SELF (44 B)            rc={rc} expect 2  "
              f"{'PASS' if ok else 'FAIL'}")
        failures += 0 if ok else 1

        # 4. real header + random payload -> exit 0, ciphertext at offset 0
        p = d / "self_random.bin"
        p.write_bytes(make_self_header() + os.urandom(1024 * 1024))
        rc, out = run(p, "--scan-limit", "65536")
        ok = (rc == 0 and "ENCRYPTED SELF" in out
              and "ciphertext begins at offset 0" in out)
        print(f"  [4] SELF header + random payload     rc={rc} expect 0  "
              f"{'PASS' if ok else 'FAIL'}")
        failures += 0 if ok else 1

        # 5. header + genuinely plaintext tail -> boundary must be found
        #    Plain ASCII has entropy ~4.x and printable ~100%.
        p = d / "self_plain_tail.bin"
        tail = (b"THIS IS READABLE METADATA " * 4000)
        p.write_bytes(make_self_header() + tail)
        rc, out = run(p, "--scan-limit", "0", "--chunk", "4096")
        ok = rc == 0 and "plaintext-like" in out
        print(f"  [5] SELF header + ASCII tail         rc={rc} expect 0, "
              f"plaintext found  {'PASS' if ok else 'FAIL'}")
        failures += 0 if ok else 1

        # 6. missing file -> exit 1
        rc, out = run(d / "nope.bin")
        ok = rc == 1 and "not a file" in out
        print(f"  [6] missing file                     rc={rc} expect 1  "
              f"{'PASS' if ok else 'FAIL'}")
        failures += 0 if ok else 1

        # 7. empty file -> exit 2 (too small for a header)
        p = d / "empty.bin"
        p.write_bytes(b"")
        rc, out = run(p)
        ok = rc == 2 and "Traceback" not in out
        print(f"  [7] zero-length file                 rc={rc} expect 2  "
              f"{'PASS' if ok else 'FAIL'}")
        failures += 0 if ok else 1

    print()
    if failures:
        print(f"  {failures} case(s) FAILED")
        return 1
    print("  all cases PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
