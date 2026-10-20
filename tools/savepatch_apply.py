#!/usr/bin/env python3
"""savepatch_apply.py - Apply Apollo/Game Genie savepatch codes to USER01.

Usage:
  python3 savepatch_apply.py <savepatch> <USER01_in> [--only "Max Money"]
  python3 savepatch_apply.py <savepatch> <USER01_in> --write <USER01_out>

Parses [Code Name] blocks with Game Genie-style lines:
  2XXXXXXX YYYYYYYY  32-bit big-endian write at offset XXXXXXX
  1XXXXXXX 0000YYYY  16-bit write
  0XXXXXXX 000000YY  8-bit write

DRY RUN IS THE DEFAULT. Nothing is written unless --write is passed, and the
new file is written next to the input rather than over it -- the input is never
modified by this script.

READ THIS BEFORE USING --write ON A REAL SAVE:

  A PS3 save is encrypted, and PARAM.PFD is a signature over it. This script
  does no encryption and no signing. A USER01 patched by this script will be
  REJECTED by the console -- it is not a valid save.

  This script is for understanding a patch: seeing which bytes a code would
  touch, and confirming offsets line up, on a decrypted USER01. The only way
  to patch a real save is Apollo Save Tool ON THE CONSOLE, which re-encrypts
  and re-signs.

  Per the repo rule this is a sanity check, never verification. Verification
  requires loading the save on the console. See TASK_FOR_MUSE.md.
"""
import os
import re
import sys

def parse_savepatch(path):
    codes = []  # (name, [(offset, bytes)])
    current = None
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if line.startswith('[') and line.endswith(']') and not line.startswith('[GROUP'):
                current = (line[1:-1], [])
                codes.append(current)
            elif current is not None:
                m = re.match(r'^([012])([0-9A-Fa-f]{7})\s+([0-9A-Fa-f]{8})$', line)
                if m:
                    kind, off, val = m.group(1), int(m.group(2), 16), m.group(3)
                    vb = bytes.fromhex(val)
                    if kind == '2':
                        data = vb                # 4 bytes
                    elif kind == '1':
                        data = vb[2:]            # low 2 bytes
                    else:
                        data = vb[3:]            # low 1 byte
                    current[1].append((off, data))
    return [(n, w) for n, w in codes if w]

def main():
    argv = sys.argv[1:]
    write = False
    only = None
    positional = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--write':
            write = True
            i += 1
            continue
        if a == '--only':
            if i + 1 >= len(argv):
                print('--only needs a code name, e.g. --only "Max Money"')
                return 1
            only = argv[i + 1]
            i += 2
            continue
        if a.startswith('--'):
            print(f"Unknown option: {a}")
            return 1
        positional.append(a)
        i += 1

    if len(positional) < 2:
        print(__doc__)
        return 1

    patch_path, in_path = positional[0], positional[1]
    out_path = positional[2] if len(positional) > 2 else None

    if write:
        if out_path is None:
            print("--write needs an output path: --write <USER01_out>")
            return 1
        if os.path.abspath(out_path) == os.path.abspath(in_path):
            print("Refusing to overwrite the input file. Give a different output path.")
            return 1

    codes = parse_savepatch(patch_path)
    print(f"Parsed {len(codes)} codes from {patch_path}")
    if only:
        names = [n for n, _ in codes]
        if only not in names:
            print(f'No code named "{only}". Available:')
            for n in names:
                print(f"  {n}")
            return 1
        print(f'Only applying: "{only}"')

    with open(in_path, 'rb') as f:
        data = bytearray(f.read())
    print(f"USER01: {len(data)} bytes")
    print()

    changed = 0
    skipped = 0
    for name, writes in codes:
        if only and name != only:
            continue
        for off, new_bytes in writes:
            if off + len(new_bytes) > len(data):
                print(f"  !! {name}: offset {off:#x} out of range, skipped")
                skipped += 1
                continue
            old = bytes(data[off:off + len(new_bytes)])
            flag = "" if old != new_bytes else "  (already set)"
            print(f"  {name}: @{off:#08x} {old.hex()} -> {new_bytes.hex()}{flag}")
            data[off:off + len(new_bytes)] = new_bytes
            if old != new_bytes:
                changed += 1

    print()
    print(f"{changed} byte group(s) changed, {skipped} skipped (out of range).")

    if not write:
        print("\nDRY RUN -- nothing written. Pass --write <out> to produce a file.")
        print("Remember: a file patched here will be rejected by the console.")
        return 0

    if changed == 0:
        print("\nNothing to write -- no bytes differed.")
        return 0

    with open(out_path, 'wb') as f:
        f.write(data)
    print(f"\nWrote {out_path}")
    print("\n*** This output is NOT a usable PS3 save. ***")
    print("It is unencrypted and unsigned, so the console will reject it.")
    print("Use it to inspect the result, not to install it.")
    print("Patch the real save with Apollo on the console.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
