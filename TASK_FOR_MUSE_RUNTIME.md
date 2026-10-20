# Task brief: apply one runtime code and watch the screen

A self-contained job for whoever is at the console. Follow it in order.
If a step fails, **stop and report** — do not work around it.

**Goal:** apply the single `Infinite Health` code to the running game, then see
whether your health bar still drops. One observation settles it.

**Repo:** https://github.com/richard1222/Yakuza-dead-souls-cheats
**Target:** USA disc, serial `BLUS30826`, app `01.00`.

---

## Why this route, and not Artemis

**Do not use Artemis.** It was tried on this console and is not viable — the game
froze with Artemis enabled *and* disabled, so Artemis is not the cause, but it is
also not the tool that works here. It is not the route.

The route that **is** hardware-verified on this console is a plain HTTP memory
write to **webMAN MOD's PS3MAPI endpoints**. Nothing is installed, nothing is
hooked, no cheat engine runs. It is just a web request that changes four bytes
of the game's memory.

That matters for two reasons:

* **Nothing touches the disk.** Quit the game and it is stock again. No save is
  modified, no file is patched.
* **It is reversible by construction.** You can read the old value first.

---

## Read this first: what counts as proof

The repo's rule is strict, and it is the thing most likely to be got wrong.

| result | counts as verified? |
|---|---|
| applied on console, effect seen in game | **yes** |
| applied on console, game froze or crashed | **yes — that is a real finding** |
| "the address looks correct" | **no** |
| checked in an emulator | **no** |
| a tool printed "success" but nothing was seen in game | **no** |

The rule is: **a code counts only once the effect has been seen on the console.**
Everything else is a hypothesis. Do not record anything as verified that you did
not personally watch happen in the game.

---

## Part 0 — check the tool can even reach the console

Nothing is written in this step. It is a read.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\yakuza_mem.ps1 -IP <ps3-ip> -Mode status
```

This should print:

* webMAN MOD responding,
* the running game's **pid**,
* the current value at `0154BDA4` (the health address).

**If this fails, stop.** The rest of the brief cannot work. Report what it said.

Get the PS3's IP from **XMB → Settings → Network Settings → Connection Status
→ IP Address**.

## Part 1 — start the game and get in-game

1. Start Yakuza: Dead Souls — **USA disc**.
2. Load a save **you do not mind losing**. Not your main save.
3. Get somewhere you can take damage on purpose.
4. **Note your health before doing anything else.** Read it off the health bar.

## Part 2 — dry run (still writes nothing)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\yakuza_mem.ps1 -IP <ps3-ip> -Mode poke -Code "Infinite Health"
```

Without `-Force` this prints *what it would change* and writes nothing. Confirm
it reports the same value the status step read.

## Part 3 — apply it

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\yakuza_mem.ps1 -IP <ps3-ip> -Mode poke -Code "Infinite Health" -Force
```

It writes `35981264` to `0154BDA4`. That is the whole cheat.

## Part 4 — look at the screen (the only step that matters)

Do **not** trust the tool's success message. Get into a fight and take damage.

| what you see | what it means |
|---|---|
| health bar does not drop | ✅ **the code works** — the address is right for this build |
| health drops normally | ❌ wrong address or wrong build — headline finding |
| game freezes / audio stops | ❌ real finding — record exactly where |
| game crashes | ❌ real finding — record exactly where |

**Take a screenshot of the health bar** if you can. It is the clearest evidence.

> ### ⚠ Expected quirk
>
> The original author's own note, kept verbatim:
>
> > *"It also affects enemies, but the Shotgun still kills them."*
>
> So this is **not clean god mode**. It may make enemies very tough too. If
> enemies only die to the shotgun, that is the documented behaviour, **not a
> bug** — and it still counts as the code working.

## Part 5 — report back

Report in plain terms:

1. **Did the health bar stop dropping?** Yes / no / froze. This is the result.
2. What the `-Mode status` step printed (pid and the value at the address).
3. Any freeze or crash — and **exactly when** it happened (on apply? on next
   load? mid-fight?).
4. Whether the game still ran normally afterwards.

If it worked, the `Infinite Health` row in the README changes from *not yet* to
a real result. **If it failed, that is equally valuable** and the row records the
failure. A failed code is a finding, not a mistake on your part.

## Part 6 — optional: find an address that isn't in the list

Only if Parts 0–5 worked and you want to go further.

`tools\yakuza_find.ps1` finds a value's address by snapshotting memory twice and
diffing. It is **read-only** — there is no code path in it that writes to the
console, deliberately, so a wrong guess costs a read and never game state.

```powershell
# value is X on screen right now
powershell -NoProfile -ExecutionPolicy Bypass -File tools\yakuza_find.ps1 -IP <ip> -Mode snap -Out a.json

# change the value in game (spend money, take damage) ...

powershell -NoProfile -ExecutionPolicy Bypass -File tools\yakuza_find.ps1 -IP <ip> -Mode snap -Out b.json

# diff, telling it the before and after numbers you saw
powershell -NoProfile -ExecutionPolicy Bypass -File tools\yakuza_find.ps1 -Mode diff -A a.json -B b.json -From 1920 -To 557
```

It prints candidate addresses. Try them by hand with `yakuza_mem.ps1`.

## Do not

- install or launch Artemis
- write to your main save
- mark anything verified that you did not see on the console
- publish save files, `PARAM.PFD`, `PARAM.SFO`, or any PSN/console ID
- apply several codes at once — if something breaks you will not know which

## If something goes wrong

Quit the game. Nothing was written to disk, so a fresh launch is stock.
If the console itself seems stuck, hold the power button until it shuts down,
then start it again.
