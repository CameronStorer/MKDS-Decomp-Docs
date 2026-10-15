# Progress (central status file)

- Block 1 Agent 3 T119 (2026-10-14): native `run_from_assets` now loads verified
  loose assets without opening the source ROM, preserving original FNT/FAT IDs
  and offsets. All 610 local-ROM FAT ranges and short two-CPU boot parity pass;
  9 host tests pass. Input logging now includes IRQ-wait and scripted changes.
  ARM7 lifted integration awaits Agent 2's tested table/hook; packaged race and
  temporal visual acceptance remain open. See `4_docs/RUNTIME_CONTRACT.md`.

- Runtime user-play follow-up T116 (2026-10-14): fixed duplicate sound-unit
  advancement, selection-screen lighting, texture transforms, affine/bitmap
  sprites, priority, window masks and blending. 119 core tests pass. Exact GX
  replay restores coloured Mario; fresh race capture shows a star item and all
  eight ranking portraits. Agent 1 owns T115 host pacing/audio buffering and the
  fresh packaged-build check. Windowed quality and ranking-animation acceptance
  remain open; see `4_docs/CODEX_RUNTIME_WORK_LOG.md`.

- Runtime lane T112 (2026-10-14): the supplied NDS now completes a three-lap
  first-place race and displays results through the full 11,298-function generated
  Rust table, with verified overlay residency and native display/input/audio.
  Fixed GX relative-vertex scaling; verified controls, pause/resume and normal
  window close. 111 core tests, 3 host tests and the explicit Windows event test
  pass. Builder launcher adoption/staged-bundle acceptance remains Agent 1's work.
  Evidence and limits: `4_docs/CODEX_RUNTIME_WORK_LOG.md`.

- Owner direction (2026-10-10): hand-port development is frozen; all new work
  targets user-ROM recompilation. Codex-audit released T052 and completed T067:
  dependency-free Rust address-only metadata exporter, four tests passing,
  11,175 function boundaries across five images; 43 replay-backed original
  layout/function/global facts appended to private `4_docs/MAPPING.csv`.
  Handoff: `4_docs/CODEX_AUDIT_RECOMP_MAPPING.md`. Full native ROM recompilation
  remains in progress; this exporter supplies metadata to the builder lane.

- Codex T059 ROM-loader milestone (2026-10-10): Rust now expands the user's ARM9 image into
  SDK-declared main/autoload sections, parses ARM9 overlays through the ROM FAT, and resolves
  NitroFS paths to borrowed file data. Section labels and image sizes match the independent
  `5_tools/nds_extract.py` output for the local ROM; all 8 builder library tests and 2 binary tests
  pass. Shared names are in `4_docs/RECOMP_GLOSSARY.md` and append-only `4_docs/MAPPING.csv`. The
  `rom_builder` UI still builds the frozen reference port, and codegen has not consumed overlays.
  Work log: `4_docs/CODEX_ROM_LOADER_WORK_LOG.md`.

- Pre-freeze reference-port milestones (2026-10-10): child emitter simulation matches 17 controlled original snapshots; sound sequencing and selected spatial cues were ported and validated in the reference implementation. This work remains test-oracle history under the current recompiler-only direction. Logs: `4_docs/CODEX_CHILD_PARTICLE_WORK_LOG.md`, `4_docs/CODEX_SOUND_WORK_LOG.md`.

One place to see where the port stands. Team memo: `4_docs/TEAM_MEMO.md`. Agents: start with `4_docs/AGENTS.md` and
`python 5_tools/coord.py start <name>`; the live task board is `4_docs/TASKS.md`, the running log
`4_docs/AGENT_LOG.md`. Details: `4_docs/NEXT_GOALS.md` (full goal list),
`4_docs/WORK_PLAN.md` (lanes), `4_docs/function_notes.md` / `4_docs/FUNCTION_TABLE.csv` (function meanings).

## Lane A: course objects (Claude)

- Piranha cleanup follow-up (codex-audit): original natural path-end capture
  confirms primary age14 -> lifetime20 while child age7 remains unchanged.
  Native projectiles now expire primaries before stopping births, preserving
  children and normal pool recycling. Six focused replay/regression tests pass;
  private release build and native frame900 inspection pass (race tick918).
  Evidence: `5_tools/bizhawk/codex_piranha_expiry/README.md`. Mouth/filter depth,
  original close-up billboard comparison and emitter camera pause remain open.

- Large Piranha audit (codex-audit): confirmed missing `0x1AA` behavior on
  Mario Circuit; its tick is `sub_20983C4`, separate from the existing small
  `0x1A6` plant. Added a scalar Rust translation and isolated capture/reducer.
  Replay now matches 2400 original plant calls across all seven states/RNG,
  and 686 projectile calls including bounce/end. Constructor headings/clock
  also verified against original fields. Native separate body/mouth animation,
  0x1AB path projectile/collision, SPA51 and launch/bounce sound ids are wired.
  Full isolated core suite:284 passed,0 failed,1 existing ignored. Native
  release passes; native close-up shows stem/red head/animated mouth and SPA
  activity, exits0. Original draw:235 calls each for all three parts (705 total);
  PakkunZHead is concurrent, not LOD. Mouth/filter GPU masking, billboard and
  emitter expiry remain open. Mario Circuit seed1 autopilot reached1500 ticks,
  zero falls, successful exit. See
  `CODEX_FIDELITY_AUDIT.md` and `5_tools/bizhawk/codex_piranha/README.md`.

- Crab presentation follow-up (codex-audit, 2026-10-10): restored the separate
  claw sprite; body/claw use original walk/idle clocks and independent actor
  materials. Natural clock/wait replay and 600 controlled original updates
  across all four states pass, including RNG; native close-up shows both parts.
  Full isolated core check:206 passed,0 failed,1 existing ignored; release build
  passes. Original draw callbacks were not captured; body wobble remains open.
  Harness: `5_tools/bizhawk/codex_crab_pattern/README.md`.
Ported from the game's code, replay-tested against BizHawk where possible (`3_hand_port/vm_model/src/mapobj/`,
wired up in `3_hand_port/game/src/objects.rs`):

| Object | Status |
| --- | --- |
| Thwomp, Chain Chomp, loose Chomp, Goomba, rocks, traffic, Bowser blocks, crabs, Pokeys | done, replay-exact |
| walking trees, Cheep Cheeps, pendulums, clock hands, Monty Moles, fire rings | done, replay-exact (or within 1 unit) |
| drawbridge (deck is a hinged ramp/wall floor) | done |
| Airship: Bullet Bill launchers + bullets, path sliders, hatches | done, in game (2026-10-09) |
| pinball bumpers | done (bounce 12 units) |
| moving-object shove (handler flag 1) | done |
| objects' own reaction table (`0x0216B9AC`) | done: real table replaces the old guess (2026-10-09) |
| Monty Mole hit states 6/7 (star knock / run into, roll) | done (2026-10-09) |
| Cheep Cheep star knock (shared knock-away routine `knock.rs`), hide, respawn | done (2026-10-09) |
| loose Chomp hit state 2 (pops up, tumbles), rock star burst, Piranha Plant knock-away | done (2026-10-09) |
| pinball iron balls (replay-exact, released by lap) and flippers (swing, kicks from balls, box contact + shove) | done, in game (2026-10-09) |
| star reactions: crab knocked flying, Pokey knocked apart + regrow, snowman head knocked off + rebuilt (now drawn as body + head), Bullet Bill knocked down, iron ball bounce | done (2026-10-09) |
| chained Chomp hit state 2 | done (2026-10-09) |
| pinball drums 0xD2 (replay-exact, with their manager's random speed order) | done (2026-10-09) |
| chandeliers, paintings, Desert sun: their .nsbca joint animations played on the objects | done (2026-10-09) |
| fallback decoration models checked against the game's loaders (fixed 0x13C bakubaku; spawners 0x13D/0x1A0 draw nothing) | done (2026-10-09) |
| Water (T002, claude-lead + claude-main): the course water models drawn (Cheep Cheep Beach, Palm Shore, Banshee Boardwalk, Yoshi Falls, Delfino); Cheep Cheep Beach / Palm Shore tide rises and falls; karts in that water slow with depth (replay-exact vs BizHawk) | done (2026-10-10) |
| Tick-Tock Clock pendulum collision (bob disc; blows karts away; clock autopilot 1-2 falls) | done (2026-10-09) |
| Rocky Wrench hatch collision (solid and knocking while the wrench is up) | done (2026-10-10) |
| Boo swarms (0x13D spawners, pooled 0x13B Boos; own RNG; fade/flip) on Luigi's Mansion and Banshee Boardwalk, bakubaku 0x13C on Banshee Boardwalk (replay-tested, in game) | done (2026-10-10) |
| black gears 0xCE and Bowser's Castle rotating bridge 0xD1 turn (about their own tilted y); only flat turntables carry karts | done (2026-10-10) |
| Moving terrain (user report: Bowser's Castle karts fell through the lava blocks and rotating pipe): ported the game's own path, `sub_1FFDEE4` -> `sub_20E1D10`: lava blocks are oriented boxes, turning platforms (gears, rotary room, rotating pipe) cylinders, floor/wall per face attribute (`vm_model::kart::movement::MovingSolid`). Autopilot: Bowser's Castle 1/0/0 falls over seeds 1-3 (was ~111), Tick-Tock Clock 0 | done (2026-10-10) |
| Banshee Boardwalk bats (spawner 0x1A0 throws 0x19F bats; replay-tested, in game) | done (2026-10-09) |
| turning platforms (gears, rotary room): speed-up / run / slow / reverse / rest | done (2026-10-09) |
| texture-pattern animations (.nsbtp) on objects: looped a frame a tick; Boo faces held on slot & 1 | done (2026-10-10; per-object frame drivers, e.g. the crab's claw clock, approximated by the loop) |
| Mansion 0xC9 path item boxes: ride their path (eased follower, restart flag, hover, 15-unit collision class); `3_hand_port/vm_model/src/mapobj/path_box.rs`, wired in `3_hand_port/game/src/items.rs` | done (2026-10-10; unit tests + real Mansion data, not replayed against BizHawk) |
| left: bakubaku shadow, per-object .nsbtp frame drivers | left |

## Lane B: characters, effects, Rainbow Road (Codex)
- Child-particle birth `sub_201C74C` now ported in `3_hand_port/vm_model/src/nitro_particle_child.rs` (2026-10-10): all 40 controlled original births match every modeled field and RNG; all four rotation modes exercised. ROM-independent replay and overflow/zero-parent-life/record checks pass. Child pool/cadence/update/render/native integration remains open; see `5_tools/bizhawk/codex_particle_child/README.md`.
- Driver joint animations and face-pattern decoders are integrated; detailed drivers render with original clips. Details: `4_docs/CODEX_*` handoffs.
- Original ROM particle textures/simulation now replace cube drift sparks: smoke, blue flares, red sparks and A+B pivot smoke. Draw math matches 721 captured calls; rear contacts 645; smoke attachment 100; pivot gate 3993. Native charge rendering and active-effects race restart checked.
- CPU heading matches 3500 original calls; direct steering matches 14000 Rainbow calls. Route targets now advance before steering, as in the C. The regular Rainbow spiral falls are corrected by the original fixed local ramp pitch and matrix order: all 14731 facing calls match the ROM, including 854 inverted ramps. Final Rainbow seeds 1 and 2 each completed at least 6000 ticks with zero falls, all eight racers on lap two. Bowser and Airship checks also completed with zero falls. Full race/RNG parity and the broader 32-course sweep remain separate work.
- CPU wall-stall recovery is now wired: timer 7000 calls, correction 863 state1 probes, area selection 218 controlled callbacks. Previous-node/AREA targets feed the route cursor; final callback uses existing native respawn. Forced-stall run passed all four stages at 259/379/559/739 with immediate placement. Fixed-tick Rainbow Road sweep exited0 at 6000 ticks/2995 render frames with 10 falls; falls remain open. Respawn placement/spread and SDK reset yaw now match306 controlled original calls and are wired; steering resets on placement. Source-backed follow-up freezes every falling racer checkpoint and caches the respawn id at fall start. Supplied JGPT CPU route reset now matches 306 original callback probes across 37 nodes, including pacing reset; native wired. Fall/carry timing, absent-route/item-controller/full reset parity, other kart effects/child particles and GPU parity remain.
- Bowser terrain isolation (2026-10-10):96 controlled original queries at 16 logged native fall positions match Rust hit/no-hit, flags and push exactly (51 hits,45 misses). Original accepts the same lava contacts. Exact native swept queries and moving-block/CPU trajectory parity remain open. New replay and existing Rainbow backface regression both pass. Replay: `3_hand_port/vm_model/tests/bowser_kcl.rs`.
- Actual Bowser terrain replay (2026-10-10):6 captured native swept queries (real center/previous/radius32768/facing) match original flags/push/hit exactly. Fresh shared release capture exited0 at 6000 ticks/frame 4431 with2 falls, away from the historical block region; concurrent edits prevent attributing improvement. Three targeted regressions pass. Source mapped original moving-terrain dispatcher/box/face/motion helpers; native object tops remain approximations. Next: paired moving-box contact probes.
- Moving-box terrain (Codex, 2026-10-10):new isolated `kart/moving_terrain.rs` matches30 controlled original Bowser box probes (tilted axes; face/edge/corner, floor/wall, hit/push/normal). Wired into the concurrently added `MovingSolid` box branch and `WithFloors`; retains original normals and moving-terrain flags0x40000000. SDK axes now match the real1-degree tilt. Cylinder geometry is now handled by claude-lane-a's separate replay-backed port. Full core suite passed before axes-only change; final box/adapter/axes replay passed. Final Windows release exited0 at6000 ticks/frame3776 with1 CPU6 fall outside the block region; no sliding-block falls in this check. Concurrent edits limit attribution.
- Moving-box center precision (2026-10-10): repeated all30 original probes with actual object positions and world centers recorded. Original SDK scale-add uses `position + up.scale(-half_height)`; subtracting the positive scale differs by one unit on tilted axes. Corrected native adapter; expanded world-coordinate replay passes. Final Windows release built; private native check exited0 at6000 ticks/frame1224 with1 CPU4 fall outside the block region and no sliding-block falls. Screenshot reviewed.
- BizHawk Lua fix (2026-10-10):invalid single-backslash escape in `autodrive_plan_triple.lua` corrected; all10 autodrive scripts parse with BizHawk's `lua54.dll`. Current `autodrive_plan.lua` was already valid. Broader scan found another invalid path escape in `mt_run.lua`; fixed it, and all79 local BizHawk Lua scripts now parse (compile-only).
- Earlier complete core check:171 passed,0 failed,1 existing CPU replay ignored; Windows release compiled and ran (fresh copy: `3_hand_port/game/target/release/mkds_game_codex_cpu_respawn.exe`; supplied route reset native check passed at tick 900/frame 420). Detailed evidence/limitations: `6_data/analysis/CODEX_PARTICLE_MAP.md`, `4_docs/NEXT_GOALS.md`.

- Bowser's Castle falls (2026-10-10, Lane A): the cause was missing object floors (moving lava
  blocks 0xCA, rotating pipe 0xD1; reported by the user), not `respawn.rs`; now 2 falls / 6000
  ticks with every kart reaching lap 2. The earlier note blaming the respawn edits was wrong.
  Sliding-block falls remain open. After checkpoint freeze/id cache and supplied-route
  reset:8 falls/6001 ticks/frame 2655 (CPU3:2, CPU4:5, CPU7:1, player:0), all8
  resets used the JGPT route pointer successfully. No verified reduction in total falls. Valid original course32 recording:
  6000 frames,39,844 CPU driver calls,0 fall callbacks; racer IDs and moving CPU
  positions checked. Starts/settings/RNG differ; paired contact/trajectory comparison needed.

## Lane C: items and sound
See `4_docs/NEXT_GOALS.md` item 4 onward.

## Lane C session log (Claude)
- 2026-10-10 Bullet Bill speed: ramp was the lean decay, not an ease; removed the hack in `3_hand_port/game/src/racers.rs`, replay test `3_hand_port/vm_model/tests/bullet_speed.rs` passes, game builds. Notes: `4_docs/lane_c/PROGRESS.md`.
- 2026-10-10 Blue shell first 20 steering ticks: already exact (`replays_first_steering` passes); corrected stale notes in `4_docs/lane_c/PROGRESS.md`. No code change.
- 2026-10-10 Triple/trailing items belong to claude-lane-c (board T010); my recording attempt collided with another BizHawk run, no data written. T001 (Bowser's Castle object floors): consumer of flag 0x1000 found (`sub_1FFDEE4` -> `sub_20E1D10` -> box `sub_20E0BAC` / cylinder `sub_20E0764`), documented in `4_docs/function_notes.md`; exact cylinder port done (`3_hand_port/vm_model/src/kart/moving_cylinder.rs`, 30-probe replay, 200 vm_model tests pass); box was ported by another agent. Still open: wire real object dims/attributes (+256/+260/+272/+276/+288) instead of the hard-coded constants in `3_hand_port/game/src/objects.rs moving_floors`; platform motion (`sub_20E0680`). Task board: `python 5_tools/coord.py list`.

- 2026-10-10 Regression sweep T017: `5_tools/native/sweep.ps1`; all 32 courses exit 0, 18 falls (Rainbow Road 13, five others 1, rest 0). Details in `4_docs/NEXT_GOALS.md`.

- 2026-10-10 Balloon Battle (T025): the real hold-to-pump balloon state machine (`3_hand_port/vm_model/src/battle.rs`, from `sub_20A3FA8`/`sub_20A08EC`) replaces the instant 'one balloon a second'; 1 balloon up + 5 spare at the start, 76 ticks to pump the next. Source-derived (no BizHawk replay); steals, popped-balloon pickups and the real win rule still approximate. Details in `4_docs/function_notes.md`.

## Checks

- 2026-10-10 uncertainty audit and ROM builder (codex-audit): source-confirmed missing
  water path and crab state-driven texture clocks; older Boo-targeting / blue-shell notes
  are stale. Blue homing replay and full locked core suite pass (one existing ignored CPU
  replay). `5_tools/rom_builder.py` provides a stdlib TUI, ROM validation/provenance and
  locked release bundle using the user's external ROM. Ten Python tests pass; offline
  reference build and generated launcher smoke capture pass from another working
  directory. No fresh original emulator capture in this audit. Findings:
  `4_docs/CODEX_FIDELITY_AUDIT.md`; usage: `4_docs/CODEX_ROM_BUILD_WORKFLOW.md`.
- Baseline 2026-10-10: `vm_model` lib 130 passed / 0 failed / 1 ignored, all integration tests pass, `game` release builds. Working notes: `WORK_LOG.md`.
- `cargo test` in `vm_model` (object tests: `cargo test --lib mapobj`), `cargo build` in `game`.
- Falls sweep (autopilot): Airship 0-1 falls per race (from Bullet Bill blows), Delfino 0, Pinball 0,
  Cheep Cheep Beach 0, Peach Gardens 0, Mario Circuit 1, DK Pass 1.

- Codex input-ownership investigation (2026-10-10): same frozen precise-box binary produced1 fall/frame1224 and0 falls/frame5556 at6000 ticks with seed1; RNG draw totals already differ at tick300. Original position snapshots are sparse (104), insufficient for a matched CPU trajectory. Found Update keyboard/autoshot and FixedUpdate countdown writers targeting PlayerKart even while Cpu drives it; exclude Cpu from those writers. Keyboard ownership regression and private playable release passed. Twin native validation completed; see result below. No claim that this resolves all determinism issues. Public docs deployment d327b24 succeeded.

- CPU call order (Codex, 2026-10-10): completed read-only original capture364 calls/52 frames, always racer IDs1..7 ascending. Native drive_cpus now sorts by Racer.index before shared RNG consumption. Player0 takeover order remains uncaptured. Input-ownership regression and private playable release passed. Twin native validation completed; see result below. Prior empty-route test fixture corrected.

- CPU input/order validation (Codex, 2026-10-10): private release regression passed. Two same-executable/seed1 Bowser runs exited0 at6000 ticks (render frames5948/5939), zero falls each. All69 selected debug records match: progress/standings, RNG counts, item and recovery events; tick6000 has7698 draws each. Screenshot reviewed. This validates repeatability for these two runs, not complete state-every-tick determinism or original-game trajectory parity. Build: 8_scratch/codex_bowser_build/release/mkds_game.exe. Completed original CPU-order capture364 calls and expanded original box replay30 probes remain the direct source/runtime evidence.

- Rainbow Road follow-up (Codex, 2026-10-10): same private input/order release exits0 at6000 ticks/frame5770 with19 falls (CPU7:7; player0,CPU1/2/5/6:2 each; CPU3/4:1 each), all flags0x84000800. One racer reached lap2; others remain lap1. Screenshot reviewed on spiral; spiral falls remain unresolved. Numeric positions: 8_scratch/codex_rainbow_order_falls.json. Prior10-fall run used a different shared build; no isolated causal comparison or broad regression verdict.

- 2026-10-10 Codex Rainbow routing: all89 real swept fall-contact queries exactly match original hit/push/flags; ROM-backed replay passes. C identifies boost-ramp CPU guards, now ported through CpuKart.ramp: crossing-plane reach only during ramp flight, exact node target without wander/offset/RNG consumption. Two new regressions plus existing recovery pass; CPU heading still matches3500 original calls. Native end-to-end rerun pending; spiral falls not yet resolved.

- 2026-10-10 Codex particle validation: original child-emission guard now handles resources without SPA flag0x10000 using the primary-only pool path. New lifetime/list/RNG/polygon parity test and original child-particle replay pass. First Rainbow ramp-guard run exited101 before6000 capture because of this panic; discarded as a completed sweep. Private rebuild also exposed Piranha component visibility; three pub(crate) qualifiers unblock cross-module system ordering without behavior changes. Final native rerun remains pending.

- 2026-10-10 Codex final ramp/particle verification: corrected private Windows release built; completed seed1 native6000-tick runs exit0. Bowser:0 falls, render2219. Rainbow:18 falls, render2232 (CPU6:7, CPU1:4, CPU4:3, CPU5:2, CPU2/7:1; player0 and CPU3:0); player0 and CPU3 reach lap2. Both screenshots reviewed. Compared with prior frozen19-fall Rainbow run, shared source changed concurrently; no isolated causal improvement claim. Spiral falls remain open. Numeric results/positions: 8_scratch/codex_ramp_guards_results.json. Source-backed ramp guards and optional-child fix retained; focused release regressions and3500 original heading replay pass. Next: capture cursor targets, body up/facing and motion at the first spiral divergence, rather than changing the already89-query-exact fall detector.

- 2026-10-10 Codex Rainbow root cause: ported fixed local ramp pitch and original ramp*drift matrix concatenation. All14731 original facing outputs match, including2004 ramp/854 inverted calls; old world-Y branch disagreed1129 times. CPU target-order fix also matches14000 original steering calls (65 old-target sign errors). Private release built; Rainbow seed1 completed6000ticks/frame1452 ZERO falls, all8 racers lap2. Traced upper-loop region has642 samples, all grounded,344 inverted (before pitch fix first falling CPU spent171 ticks airborne). Bowser completed6003ticks/frame1510 ZERO falls. Screenshots reviewed. Rainbow seed2/Airship validation pending; no full-game or paired-RNG parity claim.

- 2026-10-10 Codex final Rainbow verification: two seeds completed6000/6001 ticks with ZERO falls, every racer lap2; Bowser/Airship completed6003 ticks with ZERO falls. Screenshots reviewed. Exact replays:14000 steering,14731 facing (2004 ramps/854 inverted), plus existing3500 headings and89 terrain queries. Fixed original local pitch/matrix order and route-before-steering; regular spiral falls addressed on tested seeds. Full32-course/full-three-lap/RNG parity remain. Details: 4_docs/CODEX_RAINBOW_WORK_LOG.md; native summary 8_scratch/codex_local_pitch_results.json.
