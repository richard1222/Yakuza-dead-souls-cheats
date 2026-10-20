#!/usr/bin/env python3
"""save_inspector.py - Inspect a Yakuza: Dead Souls (BLUS30826) PS3 save folder.

Usage:
  python3 save_inspector.py <save_folder> [--patch <file.savepatch>]

Reports the files in the save folder and the PARAM.SFO fields, then shows the
bytes in USER01 at every offset the savepatch actually targets -- so a save can
be sanity-checked on PC after Apollo has written it.

The target list is read from the patch file, not hardcoded. That matters: an
earlier version of this script hardcoded three offsets (0x0000/0x0004/0x0008)
that do not match the real patch, and would print bytes from the file header
while labelling them "Max Money". Reading the patch means it cannot drift.

Offsets out of range are reported as OUT OF RANGE rather than a value, because
a value there would be meaningless.

REMINDER: PC inspection is a sanity check only -- it shows that bytes changed
where the patch says. It does NOT show that the game reads them as money, HP,
or level. That requires loading the save on the console. See TASK_FOR_MUSE.md.
"""
import os
import re
import struct
import sys

DEFAULT_PATCH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "patches", "BLUS30826.our.savepatch")

LINE_RE = re.compile(r"^([0124])([0-9A-Fa-f]{7})\s+([0-9A-Fa-f]{8})$")

SFO_FIELDS = ("TITLE_ID", "TITLE", "APP_VER", "CATEGORY")

# Values that look like an unpatched header rather than a patched save.
EXPECT = {
    "Max Money": ((0x008B48, 4), 0x3B9AC9FF),
}


def parse_sfo(path):
    """Minimal PARAM.SFO reader. Returns {} if the magic is not present."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"\x00PSF":
        return None
    try:
        key_off, data_off, count = struct.unpack("<III", data[8:20])
    except struct.error:
        return None
    entries = {}
    for i in range(count):
        base = 20 + i * 16
        if base + 16 > len(data):
            break
        koff, fmt, dlen, _dmax, doff = struct.unpack("<HHIII", data[base:base + 16])
        kend = data.find(b"\x00", key_off + koff)
        if kend < 0:
            continue
        key = data[key_off + koff:kend].decode("utf-8", "replace")
        raw = data[data_off + doff:data_off + doff + dlen]
        if fmt == 0x0204:
            val = raw.rstrip(b"\x00").decode("utf-8", "replace")
        elif fmt == 0x0404:
            val = struct.unpack("<I", raw[:4])[0] if len(raw) >= 4 else None
        else:
            val = raw.hex()
        entries[key] = val
    return entries


def parse_patch(path):
    """Return [(block_name, [(offset, size)], ...] for blocks with real codes."""
    blocks = []
    current = None
    name_re = re.compile(r"^\[(.+)\]$")
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            m = name_re.match(line)
            if m:
                title = m.group(1)
                # [GROUP:...] headers are structural, not codes.
                current = None if title.startswith("GROUP") else (title, [])
                if current is not None:
                    blocks.append(current)
                continue
            if current is None:
                continue
            cm = LINE_RE.match(line)
            if cm:
                kind, off, val = cm.group(1), int(cm.group(2), 16), cm.group(3)
                # kind 0 = 8-bit, 1 = 16-bit, 2 = 32-bit, 4 = multi-write header
                size = {"0": 1, "1": 2, "2": 4}.get(kind)
                if size is None:
                    continue  # multi-write: handled separately, not a plain write
                current[1].append((off, size))
    return [(n, w) for n, w in blocks if w]


def main():
    argv = sys.argv[1:]
    patch_path = None
    positional = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--patch":
            if i + 1 >= len(argv):
                print("--patch needs a file argument")
                return 1
            patch_path = argv[i + 1]
            i += 2
            continue
        if a.startswith("--"):
            print(f"Unknown option: {a}")
            return 1
        positional.append(a)
        i += 1

    if len(positional) != 1:
        print(__doc__)
        return 1

    folder = positional[0]
    if not os.path.isdir(folder):
        print(f"Not a folder: {folder}")
        return 1

    if patch_path is None:
        patch_path = DEFAULT_PATCH
        if not os.path.exists(patch_path):
            print(f"Default patch not found at {patch_path}")
            print("Pass one explicitly: --patch <file.savepatch>")
            return 1

    print(f"Save folder: {folder}")
    print("\nFiles:")
    for root, _dirs, files in os.walk(folder):
        for fn in sorted(files):
            p = os.path.join(root, fn)
            print(f"  {os.path.relpath(p, folder)}: {os.path.getsize(p)} bytes")

    sfo_path = os.path.join(folder, "PARAM.SFO")
    if os.path.exists(sfo_path):
        sfo = parse_sfo(sfo_path)
        if sfo:
            print("\nPARAM.SFO:")
            for k in SFO_FIELDS:
                if k in sfo:
                    print(f"  {k}: {sfo[k]}")
            tid = sfo.get("TITLE_ID")
            if tid and tid != "BLUS30826":
                print(f"  !! TITLE_ID is {tid}, expected BLUS30826 (USA).")
                print("     Europe (BLES01399) addresses differ and will not work.")
        else:
            print("\nPARAM.SFO present but not a valid SFO.")
    else:
        print("\nPARAM.SFO not found.")

    user_path = os.path.join(folder, "USER01")
    if not os.path.exists(user_path):
        print("\n!! USER01 not found -- the savepatch targets USER01. Nothing to check.")
        return 2

    with open(user_path, "rb") as f:
        user = f.read()
    print(f"\nUSER01: {len(user)} bytes")

    print(f"\nSavepatch targets (read from {os.path.basename(patch_path)}):")
    try:
        blocks = parse_patch(patch_path)
    except OSError as e:
        print(f"  could not read patch: {e}")
        return 1

    out_of_range = 0
    for name, writes in blocks:
        for off, size in writes:
            label = f"  {name}"
            if off + size > len(user):
                print(f"{label} @ {off:#08x} ({size}B): OUT OF RANGE "
                      f"(file is {len(user)} bytes)")
                out_of_range += 1
                continue
            chunk = user[off:off + size]
            val = int.from_bytes(chunk, "big")
            note = ""
            if name in EXPECT and EXPECT[name][0] == (off, size):
                want = EXPECT[name][1]
                note = "  <-- Max Money" + (" (PATCHED)" if val == want else " (not patched)")
            print(f"{label} @ {off:#08x} ({size}B): {chunk.hex()} = {val}{note}")

    if out_of_range:
        print(f"\n!! {out_of_range} target(s) out of range -- wrong save, or "
              "wrong region.")

    print("\nNOTE: this is a byte-level sanity check only. It does not show that")
    print("the game reads these bytes as money/HP/level. Only a console load does.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
