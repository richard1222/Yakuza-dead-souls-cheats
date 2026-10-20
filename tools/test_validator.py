"""Prove validate_savepatch.py rejects broken files.

A validator that passes everything is worthless. This feeds it deliberately
corrupted patches and asserts each is REJECTED, plus the good file is ACCEPTED.
"""
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TOOL = os.path.join(HERE, "validate_savepatch.py")
GOOD = os.path.join(REPO, "patches", "BLUS30826.our.savepatch")
UPSTREAM = os.path.join(REPO, "patches", "BLUS30826.savepatch")

good_text = open(GOOD, encoding="ascii").read()


def run(path):
    r = subprocess.run([sys.executable, TOOL, path, "USER01"],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


CASES = [
    ("no :TARGET declaration", good_text.replace(":USER01", "; removed")),
    ("wrong target file",      good_text.replace(":USER01", ":WRONGFILE")),
    ("empty code block",       good_text.replace("20008B48 3B9AC9FF", "")),
    ("malformed code line",    good_text.replace("20008B48 3B9AC9FF", "20008B4 3B9AC9FF")),
    ("code before any title",  good_text.replace(":USER01", ":USER01\n20001111 22222222")),
    ("stray text in header",   good_text.replace(":USER01", "this is not valid\n:USER01")),
    ("short value field",      good_text.replace("20008B48 3B9AC9FF", "20008B48 3B9AC9F")),
]

fails = 0
print("=== must be ACCEPTED ===")
rc, _ = run(GOOD)
print(f"  our patch      : exit {rc}  {'OK' if rc == 0 else 'UNEXPECTED'}")
if rc != 0:
    fails += 1
rc, _ = run(UPSTREAM)
print(f"  Apollo upstream: exit {rc}  {'OK' if rc == 0 else 'UNEXPECTED'}")
if rc != 0:
    fails += 1

print()
print("=== must be REJECTED ===")
for name, broken in CASES:
    with tempfile.NamedTemporaryFile("w", suffix=".savepatch", delete=False,
                                    encoding="ascii", newline="\n") as f:
        f.write(broken)
        p = f.name
    try:
        rc, _ = run(p)
    finally:
        os.unlink(p)
    ok = rc != 0
    print(f"  {name:<24} exit {rc}  {'OK (rejected)' if ok else 'FAIL (accepted!)'}")
    if not ok:
        fails += 1

print()
print(f"failures: {fails}")
sys.exit(1 if fails else 0)
