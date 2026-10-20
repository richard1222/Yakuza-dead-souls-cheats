#!/usr/bin/env python3
"""Fetch Apollo's BLUS30826 savepatch, verify it, and stage it locally.

Why fetch instead of vendoring: Apollo's patches database is GPL-3.0
(Copyright (C) 2020-2026 Damian Parrino). Copying the file into this repo would
put GPL-3.0 obligations on it. Fetching at run time keeps this repo's own
content separate, while still giving you a one-command, tamper-checked download.

The patch is NOT modified in any way. If the hash does not match, this tool
refuses to write the file.

Usage:
    python tools/fetch_savepatch.py                 # fetch + verify + stage
    python tools/fetch_savepatch.py --print-hash    # show the pinned hash
    python tools/fetch_savepatch.py --out DIR       # choose output directory
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- pinned facts
SERIAL = "BLUS30826"

# SHA-256 of the exact artifact this repo's docs were written against.
# Both jsDelivr and GitHub raw served this same hash when pinned.
# If upstream ever changes the file, this will fail loudly and the docs must be
# re-checked before use -- which is the point.
PINNED_SHA256 = "76ccd5023f762815e8a8a1c6d7019ffe2e23ab06f42918e7ea74307cef1b479f"
EXPECTED_SIZE = 1527

SOURCES = [
    (
        "jsDelivr CDN (what Apollo's own site links)",
        f"https://cdn.jsdelivr.net/gh/bucanero/apollo-patches@main/PS3/{SERIAL}.savepatch",
    ),
    (
        "GitHub raw",
        f"https://raw.githubusercontent.com/bucanero/apollo-patches/main/PS3/{SERIAL}.savepatch",
    ),
]

DEFAULT_OUT = os.path.join("patches", f"{SERIAL}.savepatch")


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "yakuza-cheats-verify"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help=f"where to write the patch (default: {DEFAULT_OUT})")
    ap.add_argument("--print-hash", action="store_true",
                    help="print the pinned SHA-256 and exit")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing output file")
    args = ap.parse_args()

    if args.print_hash:
        print(f"serial       : {SERIAL}")
        print(f"expected size: {EXPECTED_SIZE} bytes")
        print(f"pinned sha256: {PINNED_SHA256}")
        return 0

    if os.path.exists(args.out) and not args.force:
        print(f"already present: {args.out}")
        data = open(args.out, "rb").read()
        got = hashlib.sha256(data).hexdigest()
        if got == PINNED_SHA256:
            print("hash OK -- nothing to do. Use --force to re-download.")
            return 0
        print(f"but its hash does NOT match the pinned value:")
        print(f"  on disk: {got}")
        print(f"  pinned : {PINNED_SHA256}")
        return 1

    data = None
    errors = []
    for label, url in SOURCES:
        try:
            print(f"fetching from {label} ...")
            data = fetch(url)
            print(f"  got {len(data)} bytes")
            break
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"  failed: {e}")
            errors.append(f"{label}: {e}")

    if data is None:
        print("\ncould not fetch from any source:")
        for e in errors:
            print(f"  {e}")
        return 1

    got = hashlib.sha256(data).hexdigest()

    print()
    print(f"  size        : {len(data)} (expected {EXPECTED_SIZE})")
    print(f"  sha256      : {got}")
    print(f"  pinned      : {PINNED_SHA256}")

    problems = []
    if len(data) != EXPECTED_SIZE:
        problems.append(f"size is {len(data)}, expected {EXPECTED_SIZE}")
    if got != PINNED_SHA256:
        problems.append("SHA-256 does not match the pinned value")
    # sanity: the file must actually be this game's patch
    head = data[:80].decode("ascii", "replace")
    if SERIAL not in data.decode("ascii", "replace"):
        problems.append(f"file does not mention {SERIAL}")

    if problems:
        print()
        print("REFUSING TO WRITE -- verification failed:")
        for p in problems:
            print(f"  - {p}")
        print()
        print("The upstream file has changed, or this is not the expected file.")
        print("Re-check the docs against the new artifact before using it.")
        print(f"first bytes: {head!r}")
        return 1

    print()
    print("verification OK")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "wb") as f:
        f.write(data)
    print(f"written to: {args.out}")
    print()
    print("This is Apollo's patch, unmodified. Apply it with Apollo Save Tool")
    print(f"against the {SERIAL} save, target file USER01.")
    print("See VERIFY_SAVEPATCH.md for the test order.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
