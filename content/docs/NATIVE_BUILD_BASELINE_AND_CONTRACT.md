# Native build: baseline and interface contract (Agent 1 / codex-build-lead)

Date: 2026-10-14. Supports `4_docs/NDS_TO_RUST_THREE_AGENT_INSTRUCTIONS.md`.

## Baseline (measured today, before the builder change)

ROM: `6_data/rom/gamefile.nds`, AMCE revision 0, reference ROM, SHA-256
`0ea8a91a0ae3e9db26337c25a6a8568f6737fa36c1e0761988c0fa0ecbf210ed`.
Metadata: `4_docs/FUNCTION_BOUNDARIES.csv`, 11,298 entries.

| Path | Command | Result |
|---|---|---|
| Old `--build` | `mkds_builder 6_data/rom/gamefile.nds --build` | Builds `3_hand_port/game/Cargo.toml`, the frozen hand-written port. 2m29s. Not ROM-driven. |
| Old `--recompile` | `mkds_builder 6_data/rom/gamefile.nds --recompile` | 400 lifted, 10,898 skipped by `MKDS_LIFT_CAP` (default 400), 0 rejected. 55s. Executable only prints a count. |
| Workspace generator | `cargo run --release --example lift_workspace -- <out> 16 <rom> <csv>` | 11,298 functions, 0 skipped, 16 part crates, 68 MB of Rust. 1m31s. |
| Compile of that workspace | `cargo build --release -j 2` | Succeeds, 17m49s. No lockfile was provided (Cargo created one). |
| Run of that workspace | `game <rom> 20` | Boots to ~20M instructions, 231 frames, 2,554 IRQs, then budget stop. **0 polygons, 0 GX writes.** It is a boot probe, not a game. |

First missing behavior: there is no native runner (window, input, audio, game loop); `recomp::boot::probe` is the only entry.

Other findings:
- `recomp` has a dev-dependency on a pre-generated `lifted/mkds_lifted` crate (stale-output risk for examples).
- `lift_workspace` writes no per-function lift/reject report and silently counts rejects as "skipped".

## Interface contract (proposed; Agent 2 and Agent 3 to confirm)

### Generator (Agent 2 provides, builder consumes)
Current stand-in: `cargo run --release --locked --example lift_workspace -- <out_dir> <parts> <rom> <metadata_csv>`.
Required for completion: the same explicit inputs, no environment fallback, plus
- `<out_dir>/lift_report.csv` (status, segment, entry, reason for **every** metadata entry),
- nonzero exit if any entry is unaccounted for,
- a generated `game` package whose binary is named `game`.

### Native runtime executable (Agent 3 provides)
- Launched as `game <args from manifest launch_args>`; today `["{rom}"]` (positional ROM path).
- Builder substitutes `{rom}` with the hash-verified ROM path and runs with the bundle as working directory.
- Exit code 0 on normal quit, nonzero with a message on stderr for launch errors (bad ROM, unsupported service).
- Diagnostics on stop: segment, guest PC, service/register.
If Agent 3 wants different arguments, change `launch_args` in `build.rs::recompile`; the launcher already honors it.

### Builder manifest (`manifest.json`, format_version 2)
`artifact_kind: generated_native_game`, `uses_reference_port: false`, ROM identity, executable + sha256,
metadata sha256, Cargo.lock sha256, generated-source sha256 and function count, build profile, `launch_args`.

## Builder behavior implemented

- `--build` / `--run` / TUI "Build native game from ROM [and play]" run: generate -> lockfile -> compile -> stage.
- The reference port is reachable only via `--reference-port` (and the TUI items marked legacy).
- Lockfile: the generated workspace is seeded with `2_native_game/Cargo.lock`, resolved with `cargo metadata`, then built `--locked`.
- Isolated target and workspace directories under a temp dir beside the output; moved into place only on success.

## Known gaps (still open on the builder side)
- Generated workspace source is copied into the bundle (68 MB); consider shipping only the report and hashes.
- `lift_report.csv` staging waits for Agent 2's report output.

## Builder acceptance results (2026-10-14)
- `mkds_builder 6_data/rom/gamefile.nds --build --out "<dir with space>/native out" --offline`: exit 0, 12m57s from a fresh output
  (11,298 generated functions, `--locked`, isolated target dir). First attempt failed at the lockfile step with a
  clear error, nonzero exit and nothing staged; fixed with `cargo update --workspace`.
- Bundle: `game.exe` (36 MB), `play.exe`, `generated/`, `manifest.json` (format 2, `uses_reference_port: false`).
- `play.exe` run from `C:\Windows` (path with a space): runs the generated code on the ROM (boot probe, exit 0).
- Changed ROM hash -> "ROM changed since build", exit 1. Missing ROM -> clear error, exit 1.
- NOT done: playable game (runtime is only the boot probe), lift_report staging, repeat-build lockfile reuse test,
  unsupported-revision/Cargo-failure message review, offline-off run.

## Builder acceptance, run 2 (mkds_gen + mkds_native), 2026-10-14
- `mkds_builder 6_data/rom/gamefile.nds --build --out "<dir with space>/native out2" --offline`: exit 0 from a fresh output.
  Compile phase 16m06s at `-j 2` (shared machine). Bundle: `game.exe` 36 MB, `play.exe`, `manifest.json` (format 3),
  `generation.json`, `coverage.csv`; no generated source unless `--keep-generated`.
- Manifest: `generation_status: complete_with_interpreter_fallback`, 11,298/11,298 entries lifted,
  0 rejected/absent, 2 undecoded sites left to the interpreter.
- `play.exe --headless --instructions 50000000 --mute` from `C:\Windows`: exit 0, 6.8 s;
  49,600,769 lifted + 399,231 interpreted ARM9 instructions, 929 frames, 0 GX writes (boot only; no menu input script used).
- Earlier run failed in Agent 2's in-progress `mkds_gen.rs` (undefined `sig_ranges`): builder reported Cargo error, staged nothing.
- Still open: interactive window check of the staged `play.exe`, menu/race run with `--input-script`, repeat build with
  warm lock, online build, overlay residency (Agent 3/2), results screen, audio verification.

## Builder acceptance, run 3 (run_with_signatures), 2026-10-14
- Builder-written `game` crate now calls `mkds_native::run_with_signatures(..., lifted::SEGMENT_SIGS, ...)`.
- Second fresh `--build` into a new output (warm caches): exit 0; `cargo_lock_sha256` identical to run 2 (lock reuse OK);
  generated source differs because Agent 2 changed the generator meanwhile (11,297 functions, status `complete`).
- `play.exe --headless --instructions 400000000 --mute --input-script confirm_menu.csv` from `C:\Windows`: exit 0, 35.9 s.
  390.8M lifted + 9.2M interpreted ARM9 instructions, 77,817 lifted overlay instructions (3 overlay signatures),
  3,189 frames, 32.6M GX writes. Capture shows a race: Lap 1/3, Mario's kart on the start line, 8th place; bottom screen
  has rankings/timer/minimap. Run 2 (old `run()` API) gave the same scene with 0 overlay instructions.
- NOT shown: steering, finishing a race, results screen, windowed launch, keyboard input, audible sound
  (audio counters are non-zero), repeat-run determinism check, online build.

## Run 4: host pacing/audio fix + regenerated lift (2026-10-14, codex-build-lead, T115)
- Fresh `--build` with the current generator/boundaries: exit 0; 11,297/11,297 lifted, 0 rejected, 0 fallback sites,
  status `complete`. Headless scripted run from `C:\Windows` (spaced path): exit 0; 397.0M lifted + 3.0M interpreted ARM9
  instructions (was 9.2M interpreted before the generator fixes), 77,818 overlay instructions, race captured (Lap 1/3, 8th).
- Host (2_native_game/native/src/{lib,audio}.rs): render worker thread (snapshot of VRAM/palette/OAM/IO/polygons, newest frame shown),
  emulation held to real time with a re-anchored schedule (no catch-up sprint), linear-interpolating resampler + primed
  jitter buffer, `--stats` pacing line with render parity check against `Session::screens()`.
- Dev-build measurement, windowed, audio on, menu script to race (before -> after): speed 33%/52% (menu/race) -> ~100%;
  audio queue empties ~30,000/s -> 0-3/s; no audio overflow drops; ~61 presented fps, ~38 distinct frames/s;
  20 render-parity checks OK. Remaining: ~12 s around race start at 79-91% speed (emulation-bound), under investigation.
- User play report: "1 million times better"; open: model shadow glitches (kart select, races), course-preview stutter,
  lag at race start (handed to T116 / Agent 2).

## Run 6: block-1 builder flow from the reorganised layout (2026-10-15, agent-build / codex-build-lead)
Command: `1_build_tool\target_lane1\release\mkds_builder.exe 6_data\rom\gamefile.nds --build --with-acceptance --out "<spaced dir>\native out6" --offline`
- Stages: rip (610 files, 25.4 MB) -> generator built 1m03s -> generate (11,297/11,297, status `complete`, 0 rejected) ->
  compile **5m01s at -j 6** (was 11-16 min at -j 2, fresh cache both times) -> stage. Exit 0.
- Bundle: `play.exe`, `game.exe`, `acceptance.exe`, `assets/` (610 files), `source/` (70.2 MB: 24 part crates, lifted, game,
  Cargo.lock, README), `generation.json`, `coverage.csv`, `manifest.json` (format 4, assets + source + acceptance blocks).
- Launcher from `C:\Windows`: normal launch exit 0; edited asset -> "Asset changed: files/data/Course/cross_course.carc", exit 1;
  deleted asset -> "Asset missing", exit 1; restored -> exit 0. Revision-1 ROM -> "Unsupported ROM ... revision 1", exit 1, no output.
- `source/` rebuilt standalone (`cargo build --release --locked --offline`, 6m13s): not byte-identical (embedded build paths) but
  **identical behaviour**: 60M-instruction headless run gives the same lifted/interpreted counts, frames and final PCs.
- **Finished race on generated code** (`acceptance.exe` = race_check on this build's `lifted::LIFTED` + `SEGMENT_SIGS`, route from
  `5_tools/native/export_runtime_route.py` on the user ROM, Figure-8 Circuit): GOAL at frame 11,409, place 1; results screen shows
  total 2:32.222 (laps 0:53.513 / 0:50.046 / 0:48.663) and standings Player 1st 10 pts ... Wario 8th 0 pts. 1,843M ARM9 instructions:
  1,826M lifted, 17.2M interpreted (0.93%), 77,818 overlay. Captures: session scratchpad `accept6/`.
- Defect seen: top-screen place badge reads like "2st" at finish/results while standings and +10 pts say 1st (glyph/OAM rendering).
- Still not block-1 complete: game reads the ROM (needs Agent 3 VFS), ARM7 interpreted (Agent 2), 17.2M ARM9 interpreted (Agent 2).

## ROM-free runtime + build cache (2026-10-15, agent-build)
- Builder now generates `game --assets <dir> [--arm7-lifted]`: the rip's `assets_sha256` is baked into the game; it calls Agent 3's
  `mkds_native::run_from_assets` (virtual card rebuilt from `assets/`, original file ids/offsets; ROM never opened). `--arm7-lifted`
  uses `run_from_assets_dual` with `lifted::LIFTED7` when the generator produced it; opt-in until Agent 2's differential test passes.
  Bundles: `launch_args: ["--assets", "{assets}"]`, `runtime_reads_rom: false`; launcher requires the ROM only for `{rom}`/legacy bundles.
- Verified (build-6 generated code + new entry point, current runtime): ROM-free 400M-instruction scripted run = identical counts
  to the ROM-based run (396,989,667 lifted / 3,010,333 interpreted ARM9, 3,199 frames), race captured; ARM7 interpreted 154.1M.
  Missing args, `--arm7-lifted` without LIFTED7, edited asset: clear errors, exit 1.
- Build cache (`--cache-dir`, default `%LOCALAPPDATA%\mkds_builder`): cold 7m27s; warm 5m41s with recomp changed in between
  (deps reused, parts recompiled because they depend on recomp). Clean no-change warm build not yet measured (tree changing).
- Build 11 with the current generator failed to compile (part_27 E0425 `ax`, constant-address load with writeback; data decoded as
  code). Reported to Agent 2 (T117); builder staged nothing.

## Lifted ARM7 by default + cache fix + finished race with no ARM7 interpreter (2026-10-15, agent-build)
- Generated game runs the ARM7 from `lifted::LIFTED7` by default (`run_from_assets_dual`); `--arm7-interpreted` = diagnostics fallback
  (prints a warning). Manifest field `arm7`. Evidence before switching: Agent 2 differential 0 mismatches / 2.2M; 400M scripted run
  lifted vs interpreted ARM7: same scene, 3198 vs 3201 frames, audio counters within 0.05%, 30 s vs 38 s wall.
- **Build cache fixed**: `2_native_game/build.rs` watched a non-existent `no-rom-supplied.nds`, so Cargo reran it on every build and
  recompiled recomp + all part crates. Now only watched with `MKDS_ROM`. Measured: build 14 (after the fix) 5m24s / 32 crates;
  **build 15, nothing changed: 28.8 s total, 0 crates compiled** (rip + generate + sync + no-op Cargo + stage).
- `race_check::run_with_tables(.., LIFTED7)`; acceptance builds pass the ARM7 table. **Build 16 acceptance (Figure-8): finished 1st at
  frame 11,580, results 1st/10 pts, total 2:35.044; ARM9 1,860.1M instructions of which 113 interpreted; ARM7 927.3M lifted cycles,
  0 interpreted; 148 s wall.** Captures: session scratchpad `accept16/`.
- Playable copy: `builds/latest/` (git-ignored) = build 15 (ROM-free, lifted ARM7); 50M boot run: 0 interpreted on both CPUs.

## Render starvation fix (2026-10-15, agent-build; owner play report "severe frame drops / stuttery preview")
- Owner: audio great with lifted ARM7; arrow on home screen often jumps too far; in-game keyboard spams Tab/Caps (low priority);
  course preview very stuttery; severe frame drops; rare visual anomalies; 13% CPU.
- Measured (`--stats`, windowed, menu->race): game at ~100% / 60 guest fps but only **8-34 frames/s rendered**. Cause: frame submission
  to the render worker was gated by the 14 ms presentation timer, which the pacing wait keeps resetting. Fixed in
  `2_native_game/native/src/lib.rs` (submit whenever a new frame exists and the worker is idle). After: **53-61 rendered/s**
  (38-49 during the emulation-bound race-start dip), 0 parity mismatches. CPU 1.34 cores (11% of 12 logical): the renderer now draws
  every frame; the CPU cost is the software hardware model (block 2), not interpretation (0 ARM7, ~0 ARM9 interpreted).
- `builds/latest` = build 17.

## Menu arrow "over-jump" measured (2026-10-15, agent-build)
- Owner input log (`8_scratch/inputlog_arrow_2026-10-15.csv`): taps reach the guest with median 5-7 frames (80-110 ms), 60 fps
  consistent (no host stretching). 16 samples had Left+Right held together (fast steering) -> host now resolves opposite D-pad
  directions to the last press (`dpad_resolve`, 2 unit tests; build 18).
- Scripted single Down press on the 50/100/150cc menu (build 18, ROM-free): hold 4-8 frames -> 1 step; 10-15 frames -> 2 steps;
  20-25 -> 3 (wraps); 30+ keeps repeating every ~8-10 frames. The game's own menu auto-repeat starts at ~10 frames (~167 ms); the
  owner's 10-15-frame presses explain the over-jumps. Faithful behaviour; no host change. Optional opt-in "short-tap assist" possible.

## One render path (Agent 3, finished/validated by agent-build) + zero interpreter (2026-10-15)
- Agent 3: `RenderSnapshot` (owned GPU inputs) + `RenderSnapshot::screens_profiled` in `machine.rs`; `Session::screens()` renders through
  it (single implementation); host worker renders snapshots, no emulated bus or duplicate code in `native/lib.rs`. His regression test
  covers correctness; agent-build ran the paired windowed validation.
- Paired windowed run, same menu->race script, quiet machine (`--stats` pacing lines only; ARM7 stats lines excluded):
  build 18 (old path): 56 s, 41 s at full speed (57.8 rendered/s), 15 s race-start dip (avg 88%, min 70%), 22 audio underruns.
  build 20 (new path + agent-lift core changes): 54 s, **all at full speed**, 55.3 rendered/s, 1 underrun, snapshot 14.8 ms/s
  (1.5% of the emulation thread), 0 parity mismatches. The dip's removal cannot be attributed to the render refactor alone.
- Build 20, 400M-instruction menu->race script: **ARM9 interpreted 0, ARM7 interpreted 0** (first time on both CPUs).
  `builds/latest` = build 20. (Earlier contended runs while other agents compiled were discarded as invalid.)
- Build 21 full-race acceptance (Figure-8, lifted ARM7): finished 1st at frame 11,359; ARM9 1,666.9M instructions, **0 interpreted**; ARM7 968.6M lifted cycles, **0 interpreted**; 95 s wall. Remaining block-1 item: interpreter out of the shipped binary (agent-lift item 2), then fresh no-cache acceptance x2.

## BLOCK 1 FINAL ACCEPTANCE: PASSED (2026-10-15 13:26-13:42, agent-build)
Two fresh builds (`--no-cache`), published tool `7_output/build_script/mkds_builder.exe`, run from `C:\Windows`, output paths with spaces:
- Each: build exit 0 (~6 min); 11,297/11,297 lifted, 0 rejected; ARM7 lifted; **interpreter not compiled in** (`interpreter_compiled_in:
  false`, `cargo tree -e features -i recomp` shows no `interpreter`); 8,246 functions with readable name comments; game reads only `assets/`.
- `play.exe` 400M-instruction menu->race: ARM9 400,000,000 lifted / **0 interpreted**; ARM7 **0 interpreted**; 3,384 frames.
- Tampered asset refused (exit 1, names the file); `--arm7-interpreted` refused (no interpreter in the shipped game).
- Full race (Figure-8, adaptive driver on the generated code): GOAL frame 11,359, 1st, results; ARM9 1,666,940,928 instructions, 0 interpreted;
  ARM7 968.6M lifted cycles, 0 interpreted; ~85 s wall.
- Pass A == pass B: generated source, Cargo.lock, generator id, metadata, coverage and assets hashes identical.
Log: session scratchpad `final_acceptance.log`. Agent 2 additionally covered Mushroom/Flower/Shell cups, Mission 1-1, WFC menus, Battle at 0/0.
Not covered by block 1: original-hardware fidelity beyond these runs, every course/mode, other ROM revisions/modified ROMs, other PCs,
the software hardware model (block 2).
