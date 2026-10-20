#!/usr/bin/env python3
"""compare_regions.py - Compare two savepatch files (e.g. US vs EU).

Usage:
  python3 compare_regions.py <file_a.savepatch> <file_b.savepatch>

Lists codes by name in each file, and for codes present in both,
shows whether the target offsets match or differ. Different offsets
for the same cheat = different build = codes are NOT interchangeable.
"""
import re
import sys

def parse(path):
    codes = {}
    current = None
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if line.startswith('[') and line.endswith(']') and not line.startswith('[GROUP'):
                current = line[1:-1]
                codes[current] = []
            elif current:
                m = re.match(r'^([012])([0-9A-Fa-f]{7})\s+([0-9A-Fa-f]{8})$', line)
                if m:
                    codes[current].append((int(m.group(2), 16), m.group(3)))
    return codes

def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    a = parse(sys.argv[1])
    b = parse(sys.argv[2])
    print(f"A: {sys.argv[1]} — {len(a)} codes")
    print(f"B: {sys.argv[2]} — {len(b)} codes\n")
    
    common = set(a) & set(b)
    print(f"In both ({len(common)}):")
    for name in sorted(common):
        oa = sorted(o for o, _ in a[name])
        ob = sorted(o for o, _ in b[name])
        same = "SAME offsets" if oa == ob else "DIFFERENT offsets"
        print(f"  {name}: {same}")
    
    print(f"\nOnly in A ({len(set(a)-set(b))}): {sorted(set(a)-set(b))}")
    print(f"Only in B ({len(set(b)-set(a))}): {sorted(set(b)-set(a))}")

if __name__ == '__main__':
    main()
