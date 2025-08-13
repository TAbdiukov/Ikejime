#  Ikejime
Patches for desktop libraries and apps. Public set.

Ikejime is inspired by [Japanese ikejime technique](https://en.wikipedia.org/wiki/Ikejime).

Discover pre-patched .exe and other binaries at: [/releases](https://github.com/TAbdiukov/Ikejime/releases)  

## Flags

Semantics (short & precise)
P — Pattern/template length check (preflight).
Before searching, ensure SRC and DST templates are the same length. (Your existing flag_use_same_length behavior.)

R — Runtime, per‑match length check.
For each match, expand the replacement (supports \1, \g<name>, \g<1> backrefs) and reject the patch if len(replacement) != len(match). Useful when SRC uses groups/regex and the actual match length may vary.

C — Commit-queue size preservation.
For each target file touched by the queue, preflight all patches in memory (in order), and reject the push if the final byte length differs from the original for that file. Nothing is written if this fails.


## Honorable mention

* [p-K10stat_anyCPUpatch.py](./p-K10stat_anyCPUpatch.py) → [K10STAT154-patched](https://github.com/TAbdiukov/Ikejime/releases/tag/K10STAT154-patched).

## See also
*Tweaking and patching,*  

* [TAbdiukov/PPSSPP-patches](https://github.com/TAbdiukov/PPSSPP-patches) – My romhacks, fixes, and workarounds for PPSSPP games and apps.
* **<ins>TAbdiukov/Ikejime</ins>** – Patches for desktop libraries and apps.
* [TAbdiukov/Ikejime-Private](https://github.com/TAbdiukov/Ikejime-Private) – <ins>Private</ins> patches.
* [TAbdiukov/WinRegistry](https://github.com/TAbdiukov/WinRegistry) – Windows Registry tweaks.
