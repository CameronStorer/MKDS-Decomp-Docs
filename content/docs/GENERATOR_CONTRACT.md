# `mkds_gen`: production generator contract (lane 2 / agent-lift)

Built from `2_native_game/src/bin/mkds_gen.rs`; requires the `gen` feature:

```
cargo build --release --locked --features gen --bin mkds_gen --manifest-path 2_native_game/Cargo.toml --target-dir <dir>
mkds_gen --rom <game.nds> --metadata <FUNCTION_BOUNDARIES.csv> --out <dir>
         [--recomp <recomp crate dir>] [--lockfile <Cargo.lock>] [--part-bytes N]
         [--no-game] [--allow-incomplete] [--names <FUNCTION_TABLE.csv>]
```

## Inputs (all explicit; no implicit repository ROM or metadata)
- `--rom`: validated with `mkds_builder::rom::inspect_rom` (AMCE revision 0 only).
- `--metadata`: address-only `segment,entry,size,mode`. The private legacy inventory is refused.
- `--names` (optional, readable `source/`): a CSV with the columns `name`, `segment`, `ea` and optional `meaning`
  (e.g. `4_docs/FUNCTION_TABLE.csv`, the project's own analysis). Each known ARM9 function gets one `// name: meaning`
  line above it; rows that are only `sub_<address>` with no meaning are skipped. Ids, code, the table and behaviour are
  unchanged (current ROM: 8,246 functions named; all generated code identical with the comments removed).
  `generation.json` reports `named_functions`.
- Segments are `arm9_main`, the autoload sections (`arm9_autoload1_itcm`, ...) and `ov9_NNN` overlays,
  from `mkds_builder::extract`. Entry bit 0 = Thumb. Overlay functions are qualified by segment.
- No lift cap. The capped `2_native_game/build.rs` (`mkds_lift`) is development-only and now lifts only an
  explicit `MKDS_ROM`; it no longer falls back to `6_data/rom/gamefile.nds`.

## Output workspace (`--out`)
- `part_NN/` crates holding lifted functions, balanced by emitted source size (`--part-bytes`, default 3 MB).
- `lifted/`: `lifted::LIFTED: &[recomp::mem::Lifted]`, plus provenance constants
  `ROM_SHA256`, `METADATA_SHA256`, `GENERATOR_ID`, `FUNCTION_COUNT`. A runner (Agent 3's) must compare
  the user's ROM hash to `lifted::ROM_SHA256` before use, so a changed input cannot reuse old code.
- `3_hand_port/game/` (omit with `--no-game`): boot-probe executable that does that check. Agent 3's native runner
  replaces it; add it as a workspace member and depend on `lifted`.
- `Cargo.toml` workspace; `Cargo.lock` is copied from `--lockfile` when given (Agent 1 decides which
  lockfile; `2_native_game/Cargo.lock` works). Part crates depend on the `recomp` crate by absolute path
  (`--recomp`, default: the checkout containing the generator).
- `coverage.csv`: exactly one row per metadata entry
  (`status,segment,entry,mode,size,instructions,blocks,undecoded_sites,reason`).
- `generation.json`: machine-readable result, written last (its presence marks a finished output).
  Fields include `status`, `rom`, `metadata`, `generator_id`, `counts`, `per_segment`,
  `lifted_functions`, `rejected_or_absent_entries`, `undecoded_sites_left_to_interpreter`,
  `fallback_sites` (segment, function, pc, word, category), `rejected`.

Statuses per entry: `lifted`, `lifted_with_fallback` (some instruction sites undecodable, left to the
interpreter), `rejected` (boundary outside image or discovery failure), `segment_absent`.

## Exit status
- 0: every entry lifted (fallback sites, if any, are reported in `status:
  complete_with_interpreter_fallback`).
- 2: output written but some entries rejected/absent: a blocker unless `--allow-incomplete`.
- 1: bad arguments or input, or an unusable output directory: nothing was written.

## Output directory safety
A non-empty `--out` that lacks `generation.json` is refused. Regenerating over a previous output removes
its `part_*`/`lifted`/`game` directories first, so stale parts never linger.

## Current evidence (this checkout, `6_data/rom/gamefile.nds` + `4_docs/FUNCTION_BOUNDARIES.csv`)
11,297 / 11,297 entries lifted, 0 rejected, 0 undecodable sites (`status: complete`). The generated
workspace compiles `--locked --offline` (about 5 min). Differential check: all table functions (four
batches via `MKDS_LIFT_CAP`/`MKDS_LIFT_OFFSET`, ~90k random runs each) match the interpreter. Generation alone does not establish that the game runs.

## Overlay residency (lane 2 -> runtime hand-off)
Overlays share guest addresses, so lifted overlay code may be dispatched only while that exact overlay
is in guest RAM. Generated `lifted::SEGMENT_SIGS: &[recomp::residency::SegmentSig]` lists, per `ov9_NNN`
segment, the FNV-1a hash of every lifted function's byte range (literal pools included). Runtime API
(`2_native_game/src/dispatch.rs`, `2_native_game/src/residency.rs`; all take `&Dispatcher`):

- `dispatcher.invalidate_overlays()`: stop dispatching every overlay at once (main image/autoloads stay
  lifted). Call when guest writes touch the overlay window, so a swapped-out overlay's code never runs.
- `dispatcher.refresh_residency(lifted::SEGMENT_SIGS, &|addr, buf| bus.peek_into(addr, buf))`: reads
  guest memory, dispatches exactly the overlays whose code matches, returns their names. Call at frame
  boundaries (and after `invalidate_overlays`). A partially overwritten overlay verifies as not resident.
- The host's "interpret all overlays" filter (`2_native_game/native/src/lib.rs`) can then be dropped; this
  lane did not edit that file.
Verified: unit tests (`residency`, `dispatch`) and a real-ROM test (`tests/gen_cli.rs`): each overlay
image verifies exactly itself. Not yet verified: the host actually running lifted overlay code.

## Metadata corrections (4_docs/FUNCTION_BOUNDARIES.csv, 5_tools/export_boundaries.py)
- `ov9_000` 0x021814F0 / 0x021896C0 are Thumb (bytes confirm); fixed via `MODE_OVERRIDES`.
- ITCM 0x01FFFCBA / 0x01FFFD0A were phantom Thumb entries (offsets inside ARM instructions; nothing
  branches to them). Dropped and replaced by the ARM run 0x01FFFCA4 (392 bytes) via `DROP_ENTRIES`/`ADD_ENTRIES`.

## Independent verification and fallback attribution (lane 2, 2026-10-14)
Private harness `8_scratch/agent_lift_profile` (not shipped) replays a full Figure-8 race on the real
generated table and checks, without using the signatures: for every lifted overlay step, the function's
bytes in guest RAM equal the ROM overlay image (11,260 steps: 0 stale, 0 dispatched while unverified); and
every 10 frames, which overlay image actually matches RAM. Only `ov9_001` is resident during the race
(`ov9_002`, which has no lifted code, only for the first ~10 boot frames). A <=10-frame window where the
session lists no overlay although one is resident is the safe direction.

Interpreted ARM9 charges, full race, before -> after two generator fixes:
- 65-67M -> 16-17M (3.5% -> 0.9% of 1.84B). Adaptive driver: finished 1st at frame 11409, results 1st/10 pts
  (earlier table: frame 11449); wall time 175 s vs 199 s.
- Fix 1, `2_native_game/src/lift.rs`: `add pc, pc, rX, lsl #n` switch tables. The table of `b` instructions after
  it is now discovered (each entry is a block), so case bodies are lifted; they were ~30% of the fallback.
- Fix 2, metadata: `sub_1FFDEE4` (course KCL swept-sphere query) is 5380 bytes (0x01FFDEE4-0x01FFF3E8), not
  1700; its hot triangle loop was uncovered ITCM (~60% of the fallback).
Remaining ~16M: ARM9 BIOS exception vector 0xFFFF0034 (~1.2M; deliberate BIOS service replacement, not
game code), listed ITCM/main functions entered at non-block-start pcs (~10M), and unlisted ITCM/main gaps
(~5M, e.g. 0x01FFF400-0x01FFFBB8, 0x0200C900-0x0200C980). These are reported, not claimed solved.
Note: fixed-input replays are timing-sensitive (any change to what is lifted shifts budgets); use the
adaptive driver (`race_check`) for behavioural comparison.

## Generator-discovered code: ARM7 program and IRQ stubs (block 1 WP-B/WP-C, agent-lift, 2026-10-14)
Code with no metadata entry is found by `lift::discover_program` (whole-program recursive descent): seeds, then
every direct call target, tail call (branch out of the function) and code pointer the code materialises
(pc-relative literal words, `adr`) to a fixpoint. A pointer candidate is kept only if it is aligned for its mode,
lies in a code section and lifts with no undecodable site, so data words that look like addresses are dropped.
A function ends at a branch to another known entry. `lift::discover` additionally makes the return point of
`mov lr, pc` / `add lr, pc, #k` (indirect calls through `bx rX` / `ldr pc, ...`) a block start.

- **ARM7**: `build_support::arm7_sections` reads the ARM7 binary from the ROM header and finds the crt0 autoload
  descriptor `(list_start, list_end, data_start)` by its arithmetic (12-byte `(dest, size, bss)` entries summing to
  `list_start - data_start`); no descriptor = refused. Sections: `arm7_main` (static part) and
  `arm7_auto_XXXXXXXX` (by destination; AMCE0: 0x027E0000, 0x037F8000 WRAM, 0x06000000 ARM7 VRAM), lifted at their
  run-time addresses. Seeds: ARM7 entry and our `rt::ARM7_IRQ_STUB` at 0x18 (segment `bios7`).
- **ARM9 IRQ stub**: `rt::ARM9_IRQ_STUB` at 0xFFFF0018 is lifted as segment `bios9` into `LIFTED` (its return half,
  0xFFFF0034, was the largest single interpreted pc).
- New `lifted` items: `LIFTED7: &[recomp::mem::Lifted]`, `ARM7_FUNCTION_COUNT`, `ARM7_ENTRY`,
  `ARM7_SEGMENTS: &[&str]` (dispatch all; none is an overlay), `ARM7_SIGS: &[SegmentSig]` (bytes of every lifted
  ARM7 function, literal pools excluded: verify once after boot with `residency::verify`). `FUNCTION_COUNT` counts
  `LIFTED` (ARM9) only.
- `coverage.csv`: metadata rows as before, then one `discovered` row per generator-found function (size = code span).
  `generation.json`: new `discovered` object (rule, ARM7 entry/sections, per-segment functions/instructions/undecoded).
- **Unlisted ARM9 code (WP-C)**, after the metadata lift, repeated to a fixpoint:
  1. Cross-function entries: a call, tail call, code pointer, fall-through or computed-jump target that lands inside
     another listed function at a pc that is not one of its block starts becomes an extra block start there
     (`lift::discover_seeded`), but only at an instruction the function already decodes or, if its discovery never
     reached it, only if code from there lifts cleanly within the function's bounds. Metadata boundaries split some
     routines (the SDK unrolled divide/copy is entered by `add pc, pc, rX, lsl #2` from the *previous* listed function).
  2. Gaps (main image + autoload sections outside every listed function): `discover_program_with` from every reference
     into a gap, every data word pointing into a gap and the start of each gap after a listed function and its literal
     pool. Every gap candidate must lift with no undecodable site (literals often point at read-only data in gaps,
     fall-throughs after no-return calls are literal pools, and a few listed "functions" in the crt0 header area are data).
  Overlays get (1) but not (2) yet.
- Discovery rules added to `lift.rs` (all ARM and ARM7 alike): return point of `mov lr, pc` / `add lr, pc, #k`; resume
  point of a context save (`stm {.., pc}` / `str pc` -> address + 12; NitroSDK `adr` + 8 resumed by `subs pc, lr, #4`,
  so `adr` values - 4 are pointer candidates); `add pc, pc, rX, lsl #n` with no branch table = jump into the following
  unrolled run (every instruction up to the first unconditional pc write is a block start; `lift::jump_run`); the Thumb
  switch `add rX, rI, rI; add rX, pc; ldrh rX, [rX, #k]; lsl #16; asr #16; add rX, pc; bx rX` (signed halfword table,
  `cmp rI, #n` bound, else up to the first case after the table; `lift::thumb_switch_targets`).
- Evidence (AMCE0, 2026-10-15): 11,297/11,297 listed entries lifted, ~100 of them with added entry points; ~155 gap
  functions; 1,109 ARM7 functions; 0 undecodable sites (`status: complete`). `tests/gen_cli.rs` checks rows,
  `LIFTED7`, sections; `tests/discovery.rs` covers each rule on hand-assembled code. Private harnesses
  (`8_scratch/agent_lift_tools`, not shipped): `diff7`/`diff9` (every `LIFTED7` / `LIFTED` function vs the
  interpreter, entry + random block starts) and `cov` (replayed menu -> race: interpreted ARM9 entry pcs; every pc
  the ARM7 executes must be a lifted instruction and every non-sequential entry a block start). Results below.

### ARM7 host integration contract (for Agent 3; `LIFTED7` hand-off)
- **Dispatcher**: `let d7 = Dispatcher::with_loaded(lifted::LIFTED7, lifted::ARM7_SEGMENTS);` (no overlays, no residency
  refresh). Optionally check once after the crt0 autoload has run: every `lifted::ARM7_SIGS` entry verifies with
  `residency::verify(sig, &|a, b| peek ARM7 view)`.
- **Run loop (replaces fetch/exec in `Arm7::run_cpu`)**, same shape as ARM9 `Session::step`:
  `cpu.budget = burst; match d7.get(pc) { Some(f) => { let n = f(&mut cpu, &mut view, pc); pc = if n == BUDGET_EXHAUSTED { cpu.r[15] } else { n }; } None => <diagnostics-only interpreter, else report the pc as an error> }; spent = burst - cpu.budget`.
- **Resumable state**: all of it is `Cpu` + `pc`. Lifted functions return at block boundaries only; `Bus::call` stays flat
  (`View::call` returns `target`, lr already set), so nothing lives on the host stack and an IRQ or halt can be taken
  after any return.
- **Budget units = ARM7 cycles**, the same model as `arm7.rs` `cost()` (now also `rt::arm7_cycles`; please make
  `cost()` call it so the two cannot drift). The generator charges each block, at its start, the sum of
  `arm7_cycles(inst, passed = true, jumped = last instruction && writes pc/calls)`. Differences from the per-instruction
  interpreter: a skipped conditional instruction is charged as executed (interp: 1), and a block may overshoot the
  burst by up to one block (`spend` lets a block start with less budget left, like the ARM9). Timers advance by
  `spent` as now.
- **IRQs**: set `burst = left.min(64)` as now; check `rt::irq_ready` between calls and `take_irq(.., 0)` -> pc 0x18,
  which is lifted (`bios7`), so the IRQ entry and return run lifted.
- **Halt / IntrWait / HALTCNT**: lifted code continues to the next block after `m.swi(..)` or an IO write. When the
  CPU must stop (`s.halted = true`, `intr_wait`), also set `c.budget = 0` in the same handler. The next block then
  returns `BUDGET_EXHAUSTED` with `cpu.r[15]` = resume pc, so execution stops exactly where the interpreter stops.
- **Interpreter gate**: `d7.get(pc) == None` is the only interpreter entry. In the shipped game, treat it as an error
  (report pc, ARM9 pc) unless a diagnostics flag allows interpreting. Count those instructions separately in `--stats`
  (`arm7_interpreted_instructions`), so block 1 acceptance can require 0.
- Status: see the verification lines below (differential + runtime coverage) before relying on it.
- Results (2026-10-15, current generator, AMCE0, replayed recorded menu -> race inputs, 12,000 frames, headless
  `Session` with the generated `LIFTED`; the replay drifts and does not finish the race, so results/menus after a
  finish are not covered):
  - ARM9: 1,783,111,621 instructions, **119 interpreted** (before this work: 11,708,843 on the same replay). All 119 are
    lifted `ov9_000`/`ov9_001` code that runs before the session re-verifies overlay residency (it verifies at frame
    boundaries). Host fix (Agent 3, `session.rs`): when `dispatcher.get(pc)` misses inside an overlay window, call
    `refresh_residency` and retry before interpreting.
  - ARM7 (still interpreted by the host, checked against `LIFTED7`): 526,423,993 instructions, 100% on lifted
    instructions, 0 non-sequential entries that are not block starts.
  - `diff7`: 1,109 functions x 2000 = 2.22M runs, **0 mismatches** (166k budget-exhausted, excluded). Timing: static
    block charges total +5.8% vs the interpreter's dynamic cycles (skipped conditionals are charged as executed).
  - `diff9`: 11,453 functions x 200 = 2.29M runs, **0 mismatches** (126k budget-exhausted).
  - Wall time of the replay: 525 s -> 307 s (fewer interpreter fallbacks).
  Not verified here: the host actually running `LIFTED7` (Agent 3), a finished race through the packaged launcher
  (Agent 1), and code paths the replay did not reach (results, other modes): measure with `--stats` there.

## Runtime dispatch (Worker 2, 2026-10-15): no interpreter needed, slices chain lifted blocks
- **Overlay residency on a miss.** `Dispatcher::configure_residency(SEGMENT_SIGS)` (called by `Session::configure_residency`)
  records each overlay's address window. `Dispatcher::resolve(pc, read)`: on a miss inside a window, residency is verified
  again (at most once per `invalidate_overlays`, i.e. per overlay code write) and the lookup retried, so an overlay the game
  has just loaded runs lifted at once. The periodic per-frame check now re-hashes only when overlay code was written since the
  last check. 12,000-frame replay: ARM9 interpreted 119 -> **0** (identical instruction count and end state).
- **Cargo feature `interpreter`** (recomp; default on for tests/diagnostics). With `default-features = false` there is no
  `recomp::interp`: a pc without a lifted block is an error naming the pc and `Dispatcher::describe(pc)` (containing lifted
  function, or segment, and overlay state) from `Session::step`, the ARM7 (`execution_error`) or `Dispatcher::call`
  (`take_error`). Shipped games should build recomp with `default-features = false` (generated `game` crate and `mkds_native`,
  since Cargo unifies features in a workspace). `Dispatcher::interpreted()` counts instructions interpreted inside
  `Dispatcher::call` (not used by `Session`, whose calls are flat).
- **Block chaining.** `Session::step` keeps calling the next lifted block until its slice budget (<= 32 ARM9 instructions) is
  spent, a pc has no lifted block, or overlay code was written; before, every call/return/computed jump ended the slice
  (12.6 instructions per slice on average), each slice paying an IRQ check, a hardware tick and an ARM7 burst. IRQs are still
  taken between slices. `Session::chain = false` restores the old behaviour.
- **Cheaper ticks.** `Machine::tick` reads the clock only when `machine.profile_time` is set (fills `prof_ns`); the GX
  command buffer is reused; the undrained-audio trim is amortized; no allocation per slice.
- **Measured** (`8_scratch/agent_lift_tools` `speed`, headless, replay of recorded inputs, host-like audio draining; i7-9750H):
  race-start window (frames 1980-2340) 85-96% -> 145-154% of real time; frames 0-3300 34.4 s -> 20.7 s. `race_check` on
  Figure-8 with chaining: GOAL at frame 11,359, place 1, results screen correct, ARM9 and ARM7 interpreted 0, 12,259 frames
  in 91 s. Profiling without admin rights: `speed` with `PROF=from,to` (in-process sampler, `src/sampler.rs`).
- **Overlay gap discovery** (2026-10-15): the gap discovery above also runs inside each overlay's own image (references from
  that overlay's listed code, its data words, gap starts after listed functions; all weak, clean lift required). Discovered
  functions belong to the overlay's segment, so they dispatch only while it is verified resident (they are not added to
  `SEGMENT_SIGS`). Current ROM: 174 functions (ov9_000 / ov9_001 / ov9_003), 0 undecodable sites.
- **Split Thumb switches**: when metadata splits a halfword switch so that its table base (`add rX, pc`) and guard are in the
  previous function, `thumb_switch_targets` reads them from the image (`tests/discovery.rs`
  `thumb_switch_split_by_metadata_still_finds_its_cases`; seen in ov9_000 at 0x0218173C, Nintendo WFC menu).
- **Coverage beyond one course** (private driver `8_scratch/agent_lift_tools` `cup`; generated ws8 + current runtime): Mushroom
  Cup (4 races finished), Flower Cup (Desert Hills, Delfino Square finished; Waluigi Pinball entered), Shell Cup (Mario Circuit,
  Moo Moo Farm finished; Peach Circuit entered), Mission 1-1, Nintendo WFC connect flow: ARM9 and ARM7 interpreted 0.
  WFC flow was 1,770 interpreted before the two fixes above. diff9 2,325,400 runs / diff7 2,218,000 runs: 0 mismatches.
  Battle mode crashed the ARM7 at stage load with both CPUs fully interpreted too (board task T120); fixed below.
- **T120 fix: `LDM/STM {..}^` base register** (`rt::block_user`, used by lifted code and the interpreter). The user-bank
  transfer read its base (and wrote back) through the *user* bank, so the ARM7 IRQ handler's `stmdb sp, {sp, lr}^` /
  `ldmia sp, {sp, lr}^` (0x03803740 / 0x03803844) saved and restored the interrupted sp/lr at the system sp instead of
  the IRQ sp. Races survived by luck; Balloon Battle starts a timer-3 IRQ (microphone sampling over SPI) that wrote
  below the main thread's sp, so sp/lr came back as garbage and the ARM7 ran from 0. The base is now the current mode's
  register; only the transferred registers are user-bank. Regression test: `rt::tests::user_bank_transfer_uses_the_current_mode_base`.
  Generated code is unchanged (it calls `R::block_user`), so no regeneration is needed. Evidence (ws8 table): Balloon
  Battle (`MENU=842:0,1056:128,1068:128,1080:0`) runs 6,000 frames (crash was at 2,347), battle timer counting,
  ARM9/ARM7 interpreted 0; Figure-8 acceptance unchanged (GOAL frame 11,359, place 1, 0/0 interpreted).
  The ARM7 now also stops at the first jump out of mapped memory (state kept for the report).
