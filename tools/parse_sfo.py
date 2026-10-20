"""Parse a PS3 PARAM.SFO and print its fields.

PARAM.SFO format:
  magic  b"\\x00PSF"  (4 bytes)
  version u32 LE
  key_table_off u32 LE   (from start of file)
  data_table_off u32 LE
  entry_count u32 LE
  then entry_count index entries of 16 bytes:
      key_off u16, data_fmt u16, data_len u32, data_max_len u32, data_off u32
  data_fmt: 0x0004 = UTF-8 special (unterminated), 0x0204 = UTF-8 string,
            0x0404 = uint32
"""
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")

FMT = {0x0004: "utf8-special", 0x0204: "utf8", 0x0404: "uint32"}


def parse(path):
    b = open(path, "rb").read()
    if b[:4] != b"\x00PSF":
        raise SystemExit(f"not a PARAM.SFO: magic={b[:4]!r}")
    version, key_off, data_off, count = struct.unpack_from("<IIII", b, 4)

    print(f"file        : {path}")
    print(f"size        : {len(b)} bytes")
    print(f"magic       : {b[:4]!r}")
    print(f"version     : 0x{version:08X}")
    print(f"key table   : 0x{key_off:X}")
    print(f"data table  : 0x{data_off:X}")
    print(f"entries     : {count}")
    print()
    print(f"{'key':<18} {'fmt':<13} {'len':>4}  value")
    print("-" * 70)

    out = {}
    for i in range(count):
        off = 20 + i * 16
        koff, fmt, dlen, dmax, doff = struct.unpack_from("<HHIII", b, off)
        # key: NUL-terminated ASCII at key_off + koff
        end = b.index(b"\x00", key_off + koff)
        key = b[key_off + koff:end].decode("ascii", "replace")
        raw = b[data_off + doff: data_off + doff + dlen]
        fname = FMT.get(fmt, f"0x{fmt:04X}")

        if fmt == 0x0404:
            val = str(struct.unpack("<I", raw.rjust(4, b"\x00"))[0])
        else:
            val = raw.rstrip(b"\x00").decode("utf-8", "replace")

        out[key] = val
        print(f"{key:<18} {fname:<13} {dlen:>4}  {val}")
    return out


if __name__ == "__main__":
    fields = parse(sys.argv[1])
    print()
    print("=== region-critical fields ===")
    for k in ("TITLE_ID", "TITLE", "ATTRIBUTE", "CATEGORY", "PARENTAL_LEVEL",
              "APP_VER", "VERSION", "PS3_SYSTEM_VER"):
        if k in fields:
            print(f"  {k:<16} = {fields[k]}")
