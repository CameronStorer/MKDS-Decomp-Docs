# Roadmap to a complete game

Clean-room Rust/Bevy re-implementation of MKDS. Every gameplay system is ported from the
decompiled code and verified **frame-exact** against BizHawk recordings before it is called done.
Assets are read from the user's own ROM at run time; nothing is embedded.

Status key: ✅ done and verified · 🔶 in progress · ⬜ not started

## Phase 0 — Player kart physics ✅
Speed, steering, drift, mini-turbo, slopes, walls, KCL collision, slipstream, kart bumps, damage
(spin, tumble, shrink), mushrooms, air physics. Replays: SNES MC1 (3 sessions), Figure-8 lap
(2,751 frames), Figure-8 items (5,639 frames).

## Phase 1 — Item objects (self-contained items, no recordings needed) 🔶
| Step | Done when | Status |
|---|---|---|
| 1.1 Map the item object pool, log it from BizHawk | item positions/velocities recorded per frame | ✅ `items_items.bin` (whole objects, every frame) |
| 1.2 Kart-vs-item test (`sub_20F97E0`) | hits in the items session come from the model | ✅ the model finds both red-shell hits and the banana (recorded item positions) |
| 1.3 Green shell: travel, slopes, wall bounces, lifetime, break; size growth, owner shield, airborne flag | recorded shell path replays exactly | ✅ 664 ticks exact from the throw |
| 1.4a Red shell homing (`sub_20F14A0`) | recorded homing replays exactly | ✅ 71 ticks exact, up to the hit |
| 1.4b Red shell state machine: item route following, target pick (all karts, then round-robin slot), homing | full red-shell life replays | ✅ 103 ticks exact, throw to hit (`red_shell.rs`, `route.rs`) |
| 1.4d Holding and throwing: throw request, held-item spring, green/red throw (`sub_20F2B94`), banana drop, flight, landing and size spring | spawned items match | ✅ pickup → hold → throw exact for both shells (kart 2, kart 6); banana 3 held + 122 ticks exact (`hand.rs`, `banana.rs`). Fake box, forward banana throw, chains ⬜ |
| 1.4c Blue shell, triples, trailing items | | ⬜ |
| 1.5 Item roulette (by place, game RNG), item-box respawn | roulette results match recordings | 🔶 odds tables and draw ported from `sub_20F8A04` (`item_slot.rs`); item boxes in the game; box size/respawn and spin time not yet measured |
| 1.6 Star, bob-omb, bullet bill, blooper, damage states 4/5/6/8 | each verified by a recording | 🔶 star speed (1.2 x top, any terrain, 451 ticks) from a recorded CPU star; the rest approximate |

## Phase 2 — Race flow
| Step | Done when |
|---|---|
| 2.0 Course map parser (`NKMD`: start points, checkpoints, item/CPU routes, objects, paths) | Figure-8 parses | ✅ `course_map.rs` |
| 2.1 Checkpoints and lap counting (NKM `CPOI`/`CPAT`), race position | lap/place match the game every frame | ✅ `race.rs`: 5,640 frames × 8 karts exact (9 lap crossings, 30 place changes) |
| 2.2 Countdown, start boost, finish, results | start-boost timing verified |
| 2.3 Falling off / wrong way / respawn (Lakitu) | respawn position verified | 🔶 fall surfaces + `JGPT` respawn point by checkpoint (from code); timing not measured |
| 2.4 Boost panels, ramps, map objects (pipes, Chomps, platforms) | per-course recordings exact |

## Phase 3 — CPU drivers
| Step | Done when |
|---|---|
| 3.1 Follow the CPU line (NKM `EPOI`/`EPAT`) with the same steering/kart physics | a CPU kart's recorded path replays | 🔶 `cpu.rs`: route cursor, reach test, target, yaw controller (`sub_1FFD224`, exact on recorded CPUs), start grid, drift hints and per-tick drift (hop direction only while in the hop, facing vector while drifting, CPU hops swing 720/tick, instant mini-turbo roll at 40 ticks); a recorded CPU drift replays with matching hop yaw, drift angle and turn rate. Missing: random target offsets, start-boost decision, other driver states |
| 3.2 Rubber-banding, item use | full 8-kart race replays from inputs alone | 🔶 Rubber-banding ported (`CpuPace`, `Standings`, `CpuParams` from `kartAIparam.bin`; ranks with two rivals): 4,921 of 4,934 recorded pace updates exact (the rest are end-of-frame standings timing). Item use ported (`CpuItems`: per-class waits, place-based aiming, rivals' shields; trailing-item handlers simplified) |

## Phase 4 — Content breadth
🔶 Stats for every character and kart built like the game (`roster.rs`; Mario's B Dasher equals the live stats). All characters/karts (stats from `kartphysicalparam.bin` + character table), all 32 courses
(collision + course objects), engine classes (50/100/150cc), mirror.

## Playable build (`3_hand_port/game/`) ✅
`cargo run --release` in `3_hand_port/game/` (or `play.bat`): a random course from the user's ROM with its
real models and textures (NSBMD/NSBTX loader `nitro.rs`), Mario on his kart, course objects,
the course's own music (SSEQ/SBNK/SWAR synth `sound.rs`; tempo and pitch verified against a
BizHawk audio dump; course → sequence table from the game at `0x0215316C`), countdown, laps,
race time, item boxes and items, Lakitu respawn; seven CPU opponents (the recorded Figure-8 GP line-up, real stats and models) on the start grid, places for all, finish standings.

## Phase 5 — Presentation
NSBMD/NSBTX model and texture loading, course and kart rendering, kart animation (lean, spin,
tumble, shrink), follow camera, HUD + touch-screen map, particles, SSEQ music and sound effects.

## Phase 6 — Game shell
Title, menus, character/kart/cup select, Grand Prix scoring, Time Trial (+ ghosts), VS, Battle,
Missions, save data, settings, packaging.

## How each step is verified
1. Read the routine (IDA exports, `5_tools/arm_disasm.py`).
2. Record a session with `5_tools/bizhawk/autodrive.lua` (scripted, unthrottled, deterministic).
3. Turn the log into a fixture; the test replays inputs only and requires exact equality.

## Status (2026-10-08)

Playable: Grand Prix, single races, Time Trial with ghosts, Balloon Battle (approximate rules).
All 32 race courses complete under autopilot. See `4_docs/NEXT_GOALS.md` for what comes next.
