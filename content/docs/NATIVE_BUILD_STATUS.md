# Native build status

**Block 1 is complete (2026-10-15):** from nothing but a user's own MKDS ROM, one command produces a native Windows program whose
game code was translated from the ROM's machine code into Rust and compiled. The shipped game contains no instruction interpreter.

Build it yourself: **[mkds-native-builder](https://github.com/CameronStorer/mkds-native-builder)** (no game data included; you
supply your own ROM).

## What one command does
1. **Checks** the ROM by fingerprint (USA version, game code AMCE, revision 0) and refuses anything else.
2. **Unpacks** every file in the ROM's file system (610 entries) into loose files with a fingerprint manifest
   ([asset layout](ASSET_LAYOUT.md)).
3. **Translates** all 11,297 ARM9 functions listed in an address-only function list, plus the ARM7 program (found automatically),
   from ARM/Thumb machine code into Rust ([code generator](GENERATOR_CONTRACT.md)). 8,246 functions get readable name comments.
4. **Compiles** the generated code with a runtime that provides the DS hardware on the PC ([runtime](RUNTIME_CONTRACT.md)).
5. **Packages** `play.exe`, the game, the unpacked files, the generated source and fingerprints of everything.

## Measured results (two fresh builds, 2026-10-15)
| Check | Result |
|---|---|
| Fresh build, ROM only, one command | about 6 minutes on a 6-core PC; unchanged rebuild about 30 s (build cache) |
| Functions translated | 11,297 / 11,297 ARM9 (0 rejected) + ARM7 program |
| Interpreter in the shipped game | not compiled in (verified in Cargo's feature tree) |
| Menus -> race, 400 million ARM9 instructions | 0 interpreted on the ARM9, 0 on the ARM7 |
| Full 3-lap race to the results screen | finished 1st; 1.67 billion ARM9 instructions, 0 interpreted; ARM7 0 interpreted |
| Also reached with 0 interpreted | Mushroom, Flower and Shell cups, Mission 1-1, Nintendo WFC menus, Battle mode |
| Two independent fresh builds | identical generated source, lockfile and asset fingerprints |
| Windowed play | real time, ~55-60 rendered frames per second, clean audio |
| Game files | read only from the unpacked folder; edited or missing files are refused |

Detailed history and every measurement: [build history](NATIVE_BUILD_BASELINE_AND_CONTRACT.md).

## How it got here (short)
- Function boundaries come from this project's mapping work ([identified functions](FUNCTION_MAP.md)); the lifter turns each function into
  Rust, with switch tables, ARM/Thumb interworking and overlays handled by segment.
- The ARM7 (sound/system processor) is discovered and lifted automatically; its translation was checked against a reference
  interpreter instruction by instruction (over 2.2 million runs, 0 mismatches) before it replaced the interpreter.
- Overlays (code the game loads at run time) are dispatched only after their bytes are verified in memory.
- The runtime renders on a worker thread, paces the game to real time and mixes audio with a resampler; the DS screens, sound chip,
  timers, DMA and interrupts are modelled in software.

## Honest limits
- The DS graphics and sound hardware are still recreated in software on the CPU (about 10% CPU use). Replacing them with a GPU
  renderer and native audio is **block 2**.
- Fidelity is checked against our own reference interpreter and spot checks against the original game, not exhaustively; not every
  course and mode has been driven yet.
- Known issues: occasional stutter, the race-position badge can show the wrong number, rare visual glitches.
- Only the USA revision-0 ROM is supported.

## What's next
1. **Block 2**: native platform layer (GPU renderer for the 3D command stream and 2D layers, native audio).
2. A separate **hand-port** build that uses the same unpacked files for players who want the modified version.
