"""Decode Apollo Save Wizard codes into plain-English operations.

Implements only the code types actually used by the Yakuza: Dead Souls
savepatches (types 0, 1, 2, 4), per the Apollo savewizard format reference:
  https://bucanero.github.io/apollo-lib/savewizard.html

Verify with `selftest()` before trusting any output.
"""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")


def decode_line(line):
    """Decode one 8-byte Save Wizard code line -> (type_char, addr, val, text)."""
    m = re.match(r"^([0-9A-Fa-f]{8})\s+([0-9A-Fa-f]{8})$", line.strip())
    if not m:
        return None
    first, second = m.group(1), m.group(2)
    t = first[0].upper()
    sub = first[1].upper()          # address type: 0 normal, 8 pointer-offset
    addr = int(first[2:], 16)
    val = int(second, 16)
    ptr = " (pointer-relative)" if sub == "8" else ""

    if t == "0":
        return ("0", addr, val & 0xFF, f"write 8-bit  0x{val & 0xFF:02X} to 0x{addr:06X}{ptr}")
    if t == "1":
        return ("1", addr, val & 0xFFFF, f"write 16-bit 0x{val & 0xFFFF:04X} to 0x{addr:06X}{ptr}")
    if t == "2":
        return ("2", addr, val & 0xFFFFFFFF, f"write 32-bit 0x{val & 0xFFFFFFFF:08X} to 0x{addr:06X}{ptr}")
    if t == "4":
        size = {"0": "8-bit", "1": "16-bit", "2": "32-bit",
                "4": "8-bit inc", "5": "16-bit inc", "6": "32-bit inc"}.get(sub, "?")
        return ("4", addr, val, f"MULTI-WRITE {size}: start addr 0x{addr:06X} val 0x{val:08X} (needs 2nd line)")
    return (t, addr, val, f"type {t} (not decoded)")


def decode_multi_second(line):
    """Second line of a Type 4 multi-write: 4NNNWWWW VVVVVVVV."""
    m = re.match(r"^4([0-9A-Fa-f]{3})([0-9A-Fa-f]{4})\s+([0-9A-Fa-f]{8})$", line.strip())
    if not m:
        return None
    count = int(m.group(1), 16)
    addinc = int(m.group(2), 16)
    valinc = int(m.group(3), 16)
    return count, addinc, valinc


def selftest():
    """Pin the decoder against the spec's own worked examples."""
    ok = True

    # Spec: "20080000 12345678" = write 0x12345678 (32-bit) at 0x080000
    d = decode_line("20080000 12345678")
    assert d[0] == "2" and d[1] == 0x080000 and d[2] == 0x12345678, d
    print("  ok  32-bit write: 20080000 12345678 -> 0x12345678 @ 0x080000")

    # Spec: "10000014 00000101" = 16-bit write of 0x0101 at 0x14
    d = decode_line("10000014 00000101")
    assert d[0] == "1" and d[1] == 0x14 and d[2] == 0x0101, d
    print("  ok  16-bit write: 10000014 00000101 -> 0x0101 @ 0x14")

    # Spec: "0001CB06 000000FF" = 8-bit write of 0xFF at 0x1CB06
    d = decode_line("0001CB06 000000FF")
    assert d[0] == "0" and d[1] == 0x1CB06 and d[2] == 0xFF, d
    print("  ok  8-bit write:  0001CB06 000000FF -> 0xFF @ 0x1CB06")

    # Spec example for Type 4: "41004500 00000100" / "4004000C 00000002"
    #   = write 4 times, 16-bit, addr += 0x0C, val += 0x02
    d = decode_line("41004500 00000100")
    assert d[0] == "4", d
    s = decode_multi_second("4004000C 00000002")
    assert s == (4, 0x0C, 0x02), s
    print("  ok  multi-write:  41004500/4004000C -> 4 writes, addr+=0x0C, val+=0x02")

    # Subtype is the SECOND character: 0 = normal, 8 = pointer-relative.
    # Spec Type 2 lists "20080000 12345678" (normal) and "28300000 87654321"
    # (pointer offset +0x300000).
    d = decode_line("20080000 12345678")
    assert "pointer-relative" not in d[3], d
    print("  ok  subtype check: 20080000 is a normal 32-bit write")
    d = decode_line("28300000 87654321")
    assert "pointer-relative" in d[3], d
    print("  ok  subtype check: 28300000 is pointer-relative")

    return ok


if __name__ == "__main__":
    print("=== decoder selftest against spec examples ===")
    selftest()
    print("all selftests passed")
