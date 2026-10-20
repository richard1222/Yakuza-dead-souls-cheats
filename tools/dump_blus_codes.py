"""Decode every code in the BLUS30826 savepatch into plain-English operations."""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decode_savepatch import decode_line, decode_multi_second

sys.stdout.reconfigure(encoding="utf-8")

path = os.path.join(os.environ["TEMP"], "opencode", "BLUS30826.savepatch")
lines = open(path, encoding="utf-8").read().splitlines()

cur = None
group = None
print(f"decoding {path}\n")
for raw in lines:
    s = raw.strip()
    if not s:
        continue
    if s.startswith(";"):
        continue
    if s.startswith(":"):
        print(f"TARGET FILE: {s[1:]}\n")
        continue
    if s.startswith("[GROUP:"):
        group = s[7:].rstrip("]")
        print(f"--- GROUP: {group} ---")
        continue
    if s.startswith("["):
        cur = s.strip("[]")
        print(f"[{cur}]")
        continue

    d = decode_line(s)
    if not d:
        print(f"    (unparsed) {s}")
        continue
    print(f"    {s}   -> {d[3]}")
    if d[0] == "4":
        # the following line is the multi-write parameter line
        idx = lines.index(raw)
        nxt = lines[idx + 1].strip() if idx + 1 < len(lines) else ""
        sec = decode_multi_second(nxt)
        if sec:
            count, addinc, valinc = sec
            print(f"    {nxt}   ->   repeats x{count}, addr += 0x{addinc:X}, val += 0x{valinc:X}")
            size_bytes = {"0": 1, "1": 2, "2": 4, "4": 1, "5": 2, "6": 4}[s[1].upper()]
            span = addinc * (count - 1) + size_bytes
            print(f"                  writes {count} slots of {size_bytes}B, spanning 0x{span:X} bytes")
