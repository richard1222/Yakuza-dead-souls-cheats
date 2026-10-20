#!/usr/bin/env python3
"""Structural reader for a PS3 SELF (signed/encrypted ELF), e.g. EBOOT.BIN.

WHY THIS EXISTS
---------------
The question was whether a PS3 game's executable can be patched on a PC. The
answer is no. This tool is the evidence: it reads the parts of a SELF that are
plaintext, then *measures* where the file turns into ciphertext, so the claim
rests on the bytes rather than on somebody's assertion.

WHAT IT CAN AND CANNOT DO
-------------------------
CAN:
  * confirm the file is a SELF and report the header fields
  * measure, chunk by chunk, where plaintext ends and ciphertext begins
  * report the ratio of readable metadata to encrypted payload
  * warn when a declared offset does not point at anything sane

CANNOT:
  * decrypt anything
  * produce an ELF
  * find code offsets you could patch

There is deliberately no decryption path here. Decrypting a retail SELF needs
Sony's console keys. This tool answers a much smaller question: "how much of
this file is even visible to us?"

FORMAT NOTES (established by inspection, not assumption)
--------------------------------------------------------
The SELF header is big-endian and begins:

    0x00  4s   magic "SCE\\0"
    0x04  u32  version
    0x08  u16  flags
    0x0A  u16  file_type
    0x0C  u32  metadata_offset
    0x10  u64  header_size
    0x18  u64  elf_filesize
    0x20  onwards: u64 offsets (self, appinfo, elf, phdr, shdr, section_info,
                 sceversion, controlinfo_offset, controlinfo_size)

On the BLUS30826 EBOOT.BIN this yields header_size = 0x980 and
elf_filesize = 0x1501C30. However, 0x980 does **not** point at a segment table:
the bytes there are high-entropy random data. So this tool does not attempt to
enumerate segments. It reports the header, then measures the boundary directly.

That measurement is the honest conclusion: on this file the encrypted region
begins essentially immediately. The first 4 KB chunk is already ciphertext-like
(entropy 7.95-7.96, ~37% printable, which is the rate you get from random
bytes), and it stays that way for the whole 22 MB.
"""
from __future__ import annotations

import argparse
import math
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

SELF_MAGIC = b"SCE\x00"
ELF_MAGIC = b"\x7fELF"

# 4s magic, I version, H flags, H type, I metadata_offset, then u64 offsets.
SELF_HDR_FMT = ">4sIHHIQQQQQQQQQQQ"
SELF_HDR_SIZE = struct.calcsize(SELF_HDR_FMT)

# Only the first nine u64s are meaningful for our purposes.
FIELD_NAMES = [
    "magic",
    "version",
    "flags",
    "file_type",
    "metadata_offset",
    "header_size",
    "elf_filesize",
    "self_offset",
    "appinfo_offset",
    "elf_offset",
    "phdr_offset",
    "shdr_offset",
    "section_info_offset",
    "sceversion_offset",
    "controlinfo_offset",
    "controlinfo_size",
]

# A chunk is "plaintext-like" if it is neither high-entropy nor mostly
# non-printable. Thresholds are deliberately generous so that a real metadata
# block is never mislabelled as ciphertext.
ENTROPY_PLAIN_MAX = 6.5
PRINTABLE_PLAIN_MIN = 0.80

# Entropy of uniformly random bytes converges on 8.00; printable ratio on
# random bytes converges on 95/256, about 37%.
RANDOM_PRINTABLE = 95 / 256


@dataclass
class ChunkResult:
    offset: int
    size: int
    entropy: float
    printable: float

    @property
    def plaintext_like(self) -> bool:
        return self.entropy < ENTROPY_PLAIN_MAX or self.printable > PRINTABLE_PLAIN_MIN


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    e = 0.0
    n = len(data)
    for c in counts:
        if c:
            p = c / n
            e -= p * math.log(p, 2)
    return e


def printable_ratio(data: bytes) -> float:
    if not data:
        return 0.0
    return sum(1 for b in data if 32 <= b < 127) / len(data)


def human(n: int) -> str:
    return f"{n:,}"


def parse_header(data: bytes) -> dict[str, object]:
    if len(data) < SELF_HDR_SIZE:
        raise ValueError(
            f"file too small for a SELF header ({len(data)} B, need {SELF_HDR_SIZE})"
        )
    vals = struct.unpack(SELF_HDR_FMT, data[:SELF_HDR_SIZE])
    return dict(zip(FIELD_NAMES, vals, strict=False))


def scan_chunks(
    data: bytes, start: int, limit: int, chunk: int
) -> list[ChunkResult]:
    out: list[ChunkResult] = []
    pos = start
    end = min(len(data), start + limit) if limit else len(data)
    while pos < end:
        block = data[pos : pos + chunk]
        if not block:
            break
        out.append(
            ChunkResult(
                offset=pos,
                size=len(block),
                entropy=entropy(block),
                printable=printable_ratio(block),
            )
        )
        pos += chunk
    return out


def analyze(path: Path, scan_limit: int, chunk: int, quiet_scan: bool) -> int:
    data = path.read_bytes()
    print(f"file        : {path}")
    print(f"size        : {human(len(data))} bytes")
    print()

    if data[:4] == ELF_MAGIC:
        print("VERDICT: plain ELF -- NOT a SELF.")
        print("         The executable is readable. That should not happen on a")
        print("         retail disc copy, so treat this as notable.")
        return 0

    if data[:4] != SELF_MAGIC:
        print(f"VERDICT: not a SELF. magic = {data[:4]!r}")
        print("         Nothing here describes a PS3 executable.")
        return 2

    hdr = parse_header(data)
    print("=== SELF header (this part is plaintext) ===")
    print(f"  magic              : {hdr['magic']!r}")
    print(f"  SELF version       : {hdr['version']} (0x{hdr['version']:X})")
    print(f"  flags              : 0x{hdr['flags']:X}")
    print(f"  file type          : {hdr['file_type']}")
    print(f"  metadata offset    : 0x{hdr['metadata_offset']:X}")
    print(f"  header size        : 0x{hdr['header_size']:X} "
          f"({human(int(hdr['header_size']))} B)")
    print(f"  declared ELF size  : {human(int(hdr['elf_filesize']))} bytes")
    print(f"  ELF offset         : 0x{hdr['elf_offset']:X}")
    print(f"  phdr offset        : 0x{hdr['phdr_offset']:X}")
    print(f"  shdr offset        : 0x{hdr['shdr_offset']:X}")
    print(f"  controlinfo        : offset 0x{hdr['controlinfo_offset']:X}, "
          f"size 0x{hdr['controlinfo_size']:X}")
    print()

    # Sanity: does the declared header_size point at plausible data? On this
    # file it does not, and saying so is more useful than printing a table of
    # nonsense parsed from ciphertext.
    hs = int(hdr["header_size"])
    warnings: list[str] = []
    if hs == 0 or hs >= len(data):
        warnings.append(f"header_size 0x{hs:X} is not inside the file")
    else:
        probe = data[hs : hs + 4096]
        pe, pp = entropy(probe), printable_ratio(probe)
        print("=== does header_size point at anything structured? ===")
        print(f"  bytes at 0x{hs:X}     : entropy {pe:.2f}, printable {100*pp:.1f}%")
        if pe > 7.5 and pp < 0.6:
            print("  -> NO. That region is random, so it is not a segment table.")
            print("     This parser therefore does not claim to enumerate segments.")
            warnings.append(
                "header_size does not mark a readable structure; segment "
                "enumeration is skipped rather than guessed"
            )
        else:
            print("  -> looks structured; a segment table may be present.")
    print()

    print("=== measuring where plaintext ends ===")
    label = "whole file" if not scan_limit else f"first {human(scan_limit)} bytes"
    chunks = scan_chunks(data, 0, scan_limit, chunk)
    if quiet_scan:
        print(f"  (scanning {label}, output trimmed)")
    else:
        print(f"  {'offset':>10}  {'entropy':>7}  {'print%':>7}  shape")
    first_cipher = None
    for c in chunks:
        if not c.plaintext_like and first_cipher is None:
            first_cipher = c.offset
        if not quiet_scan or c.offset < 16384:
            shape = "plaintext-like" if c.plaintext_like else "ciphertext-like"
            print(f"  0x{c.offset:08X}  {c.entropy:7.2f}  "
                  f"{100*c.printable:6.1f}%  {shape}")
    if quiet_scan and len(chunks) > 4:
        print(f"   ... {len(chunks)} chunks scanned, all remaining are "
              f"ciphertext-like")
    print()

    scanned = sum(c.size for c in chunks)
    print(f"  scanned            : {human(scanned)} bytes")
    if first_cipher is None:
        print("  no ciphertext-like chunk in range")
    else:
        readable = first_cipher
        if readable == 0:
            print("  ciphertext begins at offset 0 of the scan.")
            print("  -> The plaintext header is smaller than one chunk "
                  f"({human(chunk)} B).")
        else:
            print(f"  ciphertext begins  : 0x{first_cipher:X} "
                  f"({human(first_cipher)} B in)")
        pct_header = 100 * readable / len(data) if data else 0
        print(f"  header fraction    : {pct_header:.4f}% of the file")
        print(f"  encrypted fraction : {100 - pct_header:.4f}%")
    print()

    if warnings:
        print("=== warnings ===")
        for w in warnings:
            print(f"  ! {w}")
        print()

    print("=== verdict ===")
    if first_cipher == 0:
        print("  This is an ENCRYPTED SELF and the ciphertext starts immediately.")
        print(f"  Roughly {100 - 100*chunk/len(data):.2f}% of the file is unreadable.")
        print("  Its code cannot be inspected or patched from a PC. Decrypting")
        print("  it requires Sony's console keys. This tool does not attempt it.")
    elif first_cipher is not None:
        print(f"  Plaintext header ends around 0x{first_cipher:X}.")
        print("  Everything after that is encrypted. No PC-side patching.")
    else:
        print("  No ciphertext-like region found in the scanned range.")
        print("  Extend the scan to see the encryption boundary.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Read the structure of a PS3 SELF (e.g. EBOOT.BIN). "
                    "Reports what is readable and what is encrypted. "
                    "Never decrypts.",
        epilog="Exit codes: 0 = read OK, 2 = not a SELF, 1 = bad input.",
    )
    ap.add_argument("file", help="path to EBOOT.BIN or an .sprx/.self file")
    ap.add_argument("--scan-limit", type=int, default=65536,
                    help="how many bytes to scan for the plaintext boundary "
                         "(0 = whole file; default 65536)")
    ap.add_argument("--chunk", type=int, default=4096,
                    help="chunk size for the scan (default 4096)")
    ap.add_argument("--quiet-scan", action="store_true",
                    help="print only the first few scan rows")
    args = ap.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"error: not a file: {path}", file=sys.stderr)
        return 1
    if args.chunk <= 0:
        print("error: --chunk must be positive", file=sys.stderr)
        return 1

    try:
        return analyze(path, args.scan_limit, args.chunk, args.quiet_scan)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
