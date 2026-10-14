# Native build: baseline and interface contract (Agent 1 / codex-build-lead)

Date: 2026-10-14. Supports `docs/NDS_TO_RUST_THREE_AGENT_INSTRUCTIONS.md`.

## Baseline (measured today, before the builder change)

ROM: `gamefile.nds`, AMCE revision 0, reference ROM, SHA-256
`0ea8a91a0ae3e9db26337c25a6a8568f6737fa36c1e0761988c0fa0ecbf210ed`.
Metadata: `docs/FUNCTION_BOUNDARIES.csv`, 11,298 entries.

| Path | Command | Result |
|---|---|---|
| Old `--build` | `mkds_builder gamefile.nds --build` | Builds `game/Cargo.toml`, the frozen hand-written port. 2m29s. Not ROM-driven. |
| Old `--recompile` | `mkds_builder gamefile.nds --recompile` | 400 lifted, 10,898 skipped by `MKDS_LIFT_CAP` (default 400), 0 rejected. 55s. Executable only prints a count. |
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
- Lockfile: the generated workspace is seeded with `recomp/Cargo.lock`, resolved with `cargo metadata`, then built `--locked`.
- Isolated target and workspace directories under a temp dir beside the output; moved into place only on success.

## Known gaps (still open on the builder side)
- Generated workspace source is copied into the bundle (68 MB); consider shipping only the report and hashes.
- `lift_report.csv` staging waits for Agent 2's report output.

## Builder acceptance results (2026-10-14)
- `mkds_builder gamefile.nds --build --out "<dir with space>/native out" --offline`: exit 0, 12m57s from a fresh output
  (11,298 generated functions, `--locked`, isolated target dir). First attempt failed at the lockfile step with a
  clear error, nonzero exit and nothing staged; fixed with `cargo update --workspace`.
- Bundle: `game.exe` (36 MB), `play.exe`, `generated/`, `manifest.json` (format 2, `uses_reference_port: false`).
- `play.exe` run from `C:\Windows` (path with a space): runs the generated code on the ROM (boot probe, exit 0).
- Changed ROM hash -> "ROM changed since build", exit 1. Missing ROM -> clear error, exit 1.
- NOT done: playable game (runtime is only the boot probe), lift_report staging, repeat-build lockfile reuse test,
  unsupported-revision/Cargo-failure message review, offline-off run.

## Builder acceptance, run 2 (mkds_gen + mkds_native), 2026-10-14
- `mkds_builder gamefile.nds --build --out "<dir with space>/native out2" --offline`: exit 0 from a fresh output.
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
