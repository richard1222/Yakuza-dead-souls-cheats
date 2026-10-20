# Task brief: get a save file, test `[Max Money]`

A self-contained job for whoever is at the console. Follow it in order. If a
step fails, stop and report — do not work around it.

**Goal:** produce a real `BLUS30826` save file, apply the single `[Max Money]`
code, and see whether money reads **999,999,999**. That one number settles
whether the USA savepatch addresses are right.

**Repo:** https://github.com/richard1222/Yakuza-dead-souls-cheats
**Target:** USA disc, serial `BLUS30826`, app `01.00` (confirmed from the disc).
**Tool used to apply the patch:** Apollo Save Tool, **on the console**.

---

## Read this first: what counts as proof

The repo's rule is strict, and it is the thing most likely to be got wrong.

| result | counts as verified? |
|---|---|
| applied on console, effect seen in game | **yes** |
| applied on console, game froze or crashed | **yes — that is a real finding** |
| patch written into a downloaded save, never loaded on a console | **no** |
| checked in an emulator | **no** |
| "the address looks correct" | **no** |

A downloaded save only proves the patch writes the bytes it claims. It does not
prove the game reads them as money. Do not let a downloaded-save result get
recorded as a verified cheat — say which it is.

---

## Part 1 — make a save (on the console)

You need a save with **some money** and **at least one item**, so there is
something to see change.

1. Play Yakuza: Dead Souls on the USA disc.
2. Get past the opening until you have some money and an item or two.
3. Save into a **slot you do not mind losing**. Not your main save.
4. Note down what you saw, before touching the patch:
   - **money** (the exact figure, or close to it)
   - level
   - HP
   - one item and its count

Write those numbers down. You will compare against them later.

## Part 2 — copy the save to USB

Use the console's own save manager, not a file manager. Only this route
produces a save the console will accept back.

1. Plug in a USB stick, ideally **FAT32**.
2. XMB → **Game** → **Saved Data Utility (PS3)**.
3. Find the Yakuza: Dead Souls save.
4. Select it → **Copy** → choose the USB device.
5. Wait for it to finish, then **eject/safely remove** the stick before
   unplugging it.

The save will be in a folder named something like `BLUS30826-SAVEDATA` (the
exact suffix can vary) on the USB stick.

## Part 3 — inspect it (on the PC)

1. Plug the USB into the PC.
2. Find the save folder. **List every file in it** — name and size:

   ```
   Get-ChildItem -Recurse <save folder> | Select-Object FullName, Length
   ```

3. Confirm, and report:
   - the **folder name**
   - that **`USER01`** exists (this is the file the patch targets)
   - whether `PARAM.SFO` and `PARAM.PFD` are present
   - the file list and sizes

   **Do not open, copy, or publish the contents of `PARAM.PFD`, `PARAM.SFO`,
   or `USER01` itself.** A PS3 save carries the original PSN account's ID.
   The file *list* is fine; the file *contents* are not.

4. If the folder structure looks wrong (no `USER01`), stop and report it. That
   would itself be a finding: the patch would not apply.

## Part 4 — get the patch

On the PC, from the repo:

```
python tools/fetch_savepatch.py
```

This downloads Apollo's `BLUS30826.savepatch` and verifies it against a pinned
SHA-256. It writes `patches/BLUS30826.savepatch`. It refuses anything that does
not match, which is deliberate.

There is also our own patch, `patches/BLUS30826.our.savepatch`, which contains
the same 40 codes in our own layout. **Either can be used for this test.** The
point of this run is the `[Max Money]` code, which is identical in both:

```
[Max Money]
20008B48 3B9AC9FF
```

**Confirm the patch says `BLUS30826`, not `BLES01399`.** The Europe addresses
are different and will not work on the USA build.

## Part 5 — apply `[Max Money]` only (on the console)

**One code. Nothing else.** If something goes wrong, you need to know which
code caused it.

1. Copy the patch file to the USB stick.
2. Put the save back on the console if needed (Saved Data Utility).
3. Open **Apollo Save Tool** on the console.
4. Select the Yakuza: Dead Souls save.
5. Choose **Cheats** / the patch option, and load the `.savepatch`.
6. Tick **only `[Max Money]`**.
7. Apply, then let Apollo write the save.
8. **Before loading in game, back the save up again** — copy the patched save
   to USB a second time, so you can compare and roll back.

## Part 6 — load it and look

1. Start the game, load the save.
2. **What does money read?**

| what you see | what it means |
|---|---|
| **999,999,999** | ✅ the region is right; the whole savepatch set becomes credible |
| money unchanged | ❌ the patch is not landing on the USA save — headline finding |
| save corrupts / game refuses it | ❌ the write lands but the layout differs |
| game crashes on load | ❌ real finding, record exactly where it crashed |

## Part 7 — report back

Report, in plain terms:

1. **The money figure you saw.** This is the main result.
2. Whether the save loaded at all.
3. Any crash, freeze, or oddity, and when it happened.
4. The save file list from Part 3 (names and sizes only).
5. Whether anything else changed unexpectedly — neighbouring values, items,
   level.

If it worked, the `Max Money` row in the [README](README.md#what-is-verified)
changes from *not yet* to a real result. If it failed, that is equally
valuable, and the row records the failure.

## Do not

- apply more than one code this run
- use Europe (`BLES01399`) addresses
- publish the save file, `PARAM.PFD`, `PARAM.SFO`, or any account ID
- mark anything verified that was not seen on the console
- test on your main save

## If something goes wrong

Restore the save copy you took in Part 2 (Saved Data Utility → copy the USB
version back over the console's). Nothing here is destructive as long as that
copy exists — which is why it is step one.
