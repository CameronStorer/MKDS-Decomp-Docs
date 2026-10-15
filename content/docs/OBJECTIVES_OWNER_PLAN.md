# Objectives: owner plan (relayed 2026-10-14)

This supersedes the *direction* of `NDS_TO_RUST_THREE_AGENT_INSTRUCTIONS.md` where they differ; the completion conditions
there (fresh build from the ROM, provenance, no reference-port fallback, finished race through the packaged launcher, honest
reporting) still apply to every block below.

## Vision
A user needs only their own MKDS ROM and one script. The script rips the game's assets, media and logic to files on their
machine and generates a **viewable, buildable Rust source tree** that runs **natively** (no CPU interpretation, no "it's just an
emulator"). We distribute only tools and our own runtime, never the game's code or assets: everything is generated locally.

Two products, built from the same ripped inputs, in **separate repos** (user chooses):
1. **Faithful recompile** (this repo, block 1-2): 1:1 behaviour of the original game.
2. **Hand-port mod build** (separate repo, block 3): the hand-port's improvements/changes, for people who want differences.

## Honest status of "native" today
Game logic (ARM9) is lifted to Rust (99.2% of executed instructions; 0 undecoded sites). Still emulation-like: the ARM7 CPU is
interpreted, the DS hardware is modelled in software (3D/2D renderers on the CPU, sound-chip mixer, DMA/timers/IRQs, VRAM banks),
a few ARM9 instructions still hit the interpreter (BIOS vector HLE, ITCM/main gaps), and the game reads files from the ROM image
through an emulated card. Docs and READMEs must keep saying this until it is false.

## Block 1: the recompile with no CPU interpreter (decided by the owner)
Definition of done:
1. **Rip**: one command extracts, from the ROM only, loose files into `<out>/assets/` (courses, models, textures, audio/media,
   NitroFS data, plus the code binaries/overlays the lifter needs). The built game serves its file system from that folder
   (virtual filesystem replacing the emulated card); the ROM hash and the asset manifest are recorded for provenance.
2. **Generate**: a Cargo source tree in `<out>/source/` containing the lifted **ARM9 and ARM7** code, the coverage reports, and
   the runtime glue. It is kept after the build and can be browsed and rebuilt with `cargo build` (locked lockfile included).
3. **No CPU interpreter in the shipped game**: runtime reports `interpreted_instructions == 0` for a full menu-to-results race;
   ARM7 is lifted; BIOS/SWI behaviour is native services. The interpreter survives only as a test oracle (not linked into the game).
4. The software hardware model **stays in block 1 on purpose** and is labelled as such. Replacing it is block 2.
5. Acceptance: fresh output directory, ROM only, one command; finished race with results through the packaged launcher;
   windowed run at real time with clean audio; repeat build reproduces; honest report of what is still modelled.

## Block 2: native platform layer (after block 1)
Replace the hardware model with native services: GPU renderer for the 3D command stream and 2D layers (resolution scaling,
texture replacement), native audio mixer for the sound engine, native input. This is what removes "it's an emulator".

## Block 3: hand-port mod repo (after block 2 or in parallel on the shared rip step)
New repo that consumes the same `assets/` output and the hand-port's gameplay changes. Same one-script user flow.

## Work packages for fresh agents (see `NEXT_STEPS_FOR_FRESH_AGENTS.md` for commands and rules)
- **WP-A Rip + virtual filesystem** (Agent 1 builder + Agent 3 host): extend `1_build_tool/src/extract.rs` (NitroFS reader exists),
  define the `assets/` layout and manifest, add a `rip` step to `mkds_builder`, make the runtime read from it, keep ROM hash checks.
- **WP-B Lift the ARM7** (Agent 2): the metadata only covers ARM9. Add ARM7 function discovery (recursive descent in `lift.rs`),
  generate ARM7 crates, run the sound/system CPU from lifted code, differential-test against the interpreter oracle.
- **WP-C Remaining ARM9 fallbacks** (Agent 2): BIOS vector (0xFFFF0034) and SWI handling as native services; ITCM/main gaps;
  goal `interpreted_instructions == 0`.
- **WP-D Generate-and-keep source tree + one-script flow** (Agent 1): `rip` -> `generate` -> `build`, `--keep-generated` becomes
  the default, manifest records assets + source hashes.
- **WP-E User documentation** (Agent 1): single user guide; honest limits; keys; troubleshooting.
- Visual/behaviour defects reported by the user (course-preview stutter, menu input double-moves, kart-select shadows if still
  present, race-start slowdown) stay open; fix when they block acceptance.

## Out of scope for now
Website, hosting, donations, mod hub, modified-ROM support (no modified ROM available to test), other game revisions.
