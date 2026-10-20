"""Analyse the BLUS30826 savepatch's address layout for internal consistency.

Question: [Level 98] writes 32-bit 0x62 to 0x01CA01, an odd offset, while
every other stat code in the file sits on a 4-byte-aligned offset. Tests:

  1. Are the other "stat block" addresses 4-byte aligned? (expected yes)
  2. Does a 32-bit write at 0x01CA01 overlap any known field?
  3. What is the gap structure of the stat block, and can a level field fit?
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

# (name, addr, size_bytes) from the decoded patch
STATS = [
    ("Max EXP",        0x01CAFC, 4),
    ("9999/9999 HP",   0x01CAE4, 4),
    ("Max Soul Points", 0x01CB06, 1),
    ("Level 98",       0x01CA01, 4),
]

print("=== alignment of stat-block addresses ===")
for name, a, sz in STATS:
    print(f"  {name:18s} 0x{a:06X}  size={sz}  aligned4={a % 4 == 0}  aligned2={a % 2 == 0}")

print()
print("=== sorted stat block, with gaps ===")
for name, a, sz in sorted([s for s in STATS if s[0] != "Level 98"], key=lambda x: x[1]):
    print(f"  0x{a:06X} .. 0x{a+sz-1:06X}  {name}")

print()
lv = 0x01CA01
print(f"=== does Level 98 @ 0x{lv:06X} (4 bytes -> 0x{lv+3:06X}) overlap a known field? ===")
for name, a, sz in sorted([s for s in STATS if s[0] != "Level 98"], key=lambda x: x[1]):
    lo, hi = a, a + sz - 1
    overlap = not (lv + 3 < lo or lv > hi)
    print(f"  vs {name:18s} 0x{lo:06X}..0x{hi:06X}  overlap={overlap}")

print()
print("=== what lies just below the EXP field? ===")
exp = 0x01CAFC
print(f"  Max EXP @ 0x{exp:06X}. Previous aligned dword: 0x{exp-4:06X}")
print(f"  Level 98 target 0x{lv:06X} is {exp - lv} bytes BEFORE Max EXP.")
print(f"  Reading Level 98 as 8-bit at 0x{lv:06X}: value 0x62 = 98  <- plausible level cap")
print(f"  Reading Level 98 as 16-bit at 0x{lv:06X}: value 0x0062 = 98  <- same")
print(f"  Reading Level 98 as 32-bit at 0x{lv:06X}: value 0x00000062 = 98  <- same")
print()
print("  NOTE: 32-bit LE write of 0x62 sets bytes at 0x1CA01..0x1CA04")
print("        = 62 00 00 00. If the level field is 1 or 2 bytes,")
print("        the trailing zero bytes land on neighbouring data.")
