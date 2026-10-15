# Next goals (resume here)

- Crab frame-driver fix (codex-audit, 2026-10-10): restored crab_hand and wired
  body/claw clocks with independent materials. Fresh original 600-call replay
  checks all four states, wait/clocks/RNG; natural replay strengthened; native
  close-up and release pass. Full isolated core:206 passed,1 existing ignored.
  Source-backed draw mapping still needs original visible-draw capture; body
  wobble remains unported. Piranha definitions reconciled: complex bite tick
  belongs to large 0x1AA, not small 0x1A6. Scalar replay now passes2400 original
  calls/all7 states/RNG, projectile686 calls/bounce/end, constructor headings
  and clock; native plugin and SPA51 bridge wired. Full core284 passed/1 ignored.
  Native release close-up passed, red head sprite restored; original draw
  callbacks235 each (705 total) confirm concurrent stem/head/mouth. Mario
  autopilot reached1500 ticks with0 falls. Next:T052 mouth/filter depth masking,
  original close-up billboard probes, crab body wobble and emitter culling. Primary
  expiry now matches an original natural path end; children remain alive. Positioned
  launch369/bounce431 sound and particle-child rendering belong to T012/T009.

- Codex continuation (2026-10-10): shared child emission/pool/update matches all 17 controlled original emitter snapshots, including RNG/list order/newborn ticking; children now pass through the native wheel-effect update/cancel/draw path. Existing wheel resources have no child records, so new visuals await an emitter that uses them. The sound sequencer handles portamento, signed sweeps, tied-note retuning, live bend/pan and modulation; engine/item sounds are spatialized and remote wall/charge/mini-turbo cues now use camera-relative falloff/pan. Full core: 258 passed, 1 ignored. The latest `cargo build --manifest-path 3_hand_port/game/Cargo.toml` passes. Hardware sound parity remains unmeasured. Logs: `4_docs/CODEX_CHILD_PARTICLE_WORK_LOG.md`, `4_docs/CODEX_SOUND_WORK_LOG.md`.

- Moving terrain (Codex, 2026-10-10): ordinary Bowser box contact now ported from `sub_20E0BAC`/`sub_20E16DC`/`sub_20E1A80`;30 original probes match hit/push/normal/floor-wall and the installed ground adapter flags. SDK map-object Euler axes also match the real1-degree block tilt; block initialization uses them. Cylinders remain the existing approximation. Full core suite passed; final axes replay passes; Windows release check exited0 at6000 ticks/frame3776 with1 CPU6 fall outside the block region. Next: cylinder contacts, multi-contact accumulation/lowest/platform-motion output, and remaining natural falls. Evidence: `5_tools/bizhawk/codex_bowser_box/README.md`, `6_data/analysis/CODEX_PARTICLE_MAP.md`.

- Lane B child particles (2026-10-10): birth arithmetic matches 40 controlled original births; pool/cadence/updates match 17 full emitter snapshots. Native Effects now updates, cancels and draws child-list slots through its existing renderer. No current wheel emitter has child records, so native visual parity needs a child-bearing integration case. See `5_tools/bizhawk/codex_particle_child_sim/README.md` and `4_docs/CODEX_CHILD_PARTICLE_WORK_LOG.md`.
- Lane C validation handoff (2026-10-10): full core run failed `kart::blue_shell::tests::switches_to_homing_when_recorded` (expected `Some(3804)`, got `None`); no Lane C source edited by this child-birth task. Follow-up run skipping that named test passed all remaining library/integration tests. See child-particle work log for captured-run details; shared files changed during validation.

- Shared multi-bot status: root `PROGRESS.md` (update your own lane). CPU recovery now wired: timer 7000 calls, steering863 probes, AREA selection 218 callbacks; forced-stall native stages 259/379/559/739 and immediate placement pass. Fixed-tick seed1 Rainbow Road run:10 falls at 6000 ticks; placement/spread and SDK reset yaw now match306 controlled original calls and are wired. Every falling racer now freezes checkpoint progress and caches its respawn id at fall start (source-backed). Supplied JGPT route reset matches 306 original callbacks and is wired. Falls, fall/carry timing, fallback/item-controller reset parity remain open; Bowser native remains8 falls/6001 ticks after supplied-route reset. Valid original diagnostic:0 falls/6000 frames and 39,844 CPU calls; unsynchronized starts/settings. 96 controlled Bowser terrain probes match original hit/no-hit, flags and push; original accepts lava there too. Six actual native swept queries also match original exactly; fresh shared release has2 falls/6000 ticks away from the historical block region, with concurrent edits. Next: paired original moving-box contact probes (`sub_20E1D10` -> `sub_20E0BAC`), then CPU pose/target trajectories.

- Lane B CPU heading now uses original quantized SDK atan2 and rounded integer degrees, replacing floats. Original Figure-8/Rainbow Road calls replay exactly; seed1 native Rainbow Road sweep changed five falls to six, so spiral falls remain open. See `6_data/analysis/CODEX_PARTICLE_MAP.md` and `6_data/analysis/cpu_heading_fall_comparison.csv`.

- Lane B: ROM-textured drift smoke/flares/sparks now replace cubes; draw matrices/quad args match 721 original calls, rear contacts 645 calls, smoke attachment 100 wheel records, pivot smoke gate 3,993 calls. Native charge rendering and active-effects race restart verified; remaining second-matrix/GPU differences are tracked in `6_data/analysis/CODEX_PARTICLE_MAP.md`.

How to run: `game\play.bat` or `game\target\release\mkds_game.exe [course]`. Cargo lives in
`~/.cargo/bin` (not on Git Bash's PATH: `export PATH="$HOME/.cargo/bin:$PATH"`).
Falls harness: `5_tools/native/recovery_probe.ps1 -NoProbe -Course <course> -Ticks 6000` (seed1, MKDS_DEBUG + MKDS_AUTOPILOT). Use logged capture tick for comparison.

## Done recently
- Lane B primary particle pool added: 1,396 natural list operations match; whole
  birth/update/death/reuse composition matches 1,050 controlled original emitter
  ticks, including free-slot order/alpha, particle fields, RNG and polygon state.
  Drawing/native integration now landed; see the Lane B summary above.
- Lane B continuous-wheel gate now matches 645 natural updates and a second
  645-update capture with four controlled airborne calls. Drift starts/switches
  after eleven drifting ticks; ground resumes births, air pauses them. Corrected
  flag meanings: kart+68 mask0x08=drifting, mask0x10=grounded. Pool and native
  texture rendering now landed; remaining fidelity limits are documented above.
- Lane B emitter scheduling matches 1,050 original decisions (279 birth calls,
  four removals). Natural blue/red burst timing and all 56 wheel attachments
  match 20 callbacks. Continuous-wheel switching, ground gate and native textured
  rendering now landed.
- Flipper replay repaired: all 1,476 complete calls pass; three known stale
  return-hook exits are explicitly checked. Tracer now suppresses inactive exits.
- Lane C status, specs and open work: `4_docs/lane_c/PROGRESS.md` (read it before touching items or sound).
- Lane B primary particle update now matches 996 original-game ticks across all
  eight drift resources, including every modeled field, RNG and polygon allocator.
  Emitter/wheel timing and native rendering now landed; child spawning remains
  unsupported. See `6_data/analysis/CODEX_PARTICLE_MAP.md`.
- Lane B point-particle birth now matches 280 original births across all eight
  drift/wheel resources, including initialized fields and RNG states. Full
  particle update, wheel timers and native textured effects integration are now
  implemented; see `6_data/analysis/CODEX_PARTICLE_MAP.md`.

- Lane C Blooper ported from `4_docs/lane_c/blooper_boo_bullet.md`: victims are the karts AHEAD of the user
  (4/4/3/3/2/2/1 by place), chosen at actor age 63, inked at 143, ink 451 ticks fading over the last 50;
  CPU karts slow to 0.7 (`SpeedLimit::ink`); star/bullet end ink and are immune. Not ported: battle-mode
  random victims, the CPU steering wobble, exact ink blots. Roulette refuses a second Blooper (`InPlay`).
- Lane C sounds (specs in `4_docs/lane_c/sound.md`): countdown, item box/roulette/get cues; the roulette stops with the selected item. Engine voices use live pitch/volume/pan, item effects and remote wall/charge/mini-turbo cues use camera-relative falloff/pan. Remaining: verify remote event coverage and original hardware mixing, investigate the small background-music glitches, and continue the original-sequence replay work (`4_docs/CODEX_SOUND_WORK_LOG.md`).
- Lane C Boo ported from the spec: ghost state 451 ticks (item objects, lightning, star touch and Blooper
  skip the ghost; star/bullet end it), steal victim by the weighted rank-distance walk (100,75,50,30,20,10,5,0)
  taking the victim's whole slot. Steal is instant (original: Boo flies out/back, steal at frame 30 of 40);
  ghost kart-kart contact / targeting by red shells not yet ignored.
- Lane C specs ready in `4_docs/lane_c/` (blue shell + bob-omb: states, constants, damage state 6 is not in
  damage.rs yet; sound follow-up is original hardware mixing/remote cue replay).
- Lane C Bullet Bill ported from the spec: fixed speed 43008 on any terrain (`SpeedLimit::fixed`, also set
  as forward speed), CPU driver always takes fork branch 0, ends after >480 ticks or >180 when first or
  at/above the target place (rank minus 1,1,1,1,2,2,3,3 by racers) then 20 ticks of ramp-down; star and
  mushroom refused while riding; invulnerable (mask 0x10000040). Not ported: stuck-120 end, damage state 5
  for karts it touches (uses the star's blow), KillerItem model/scale, steering constants of `sub_2090638`.
- Lane C blue shell: states 3 to 7 (home, spiral, rise, dive, blast) replay a BizHawk recording exactly
  (`3_hand_port/vm_model/src/kart/blue_shell.rs`); in the game it targets the unfinished leader and runs the item route
  (approximate state 1); karts in the blast get `Blow` then `Spin(2)` until damage state 6 exists.
- Lane C bob-omb: flight with bounces, landing, rest, fuse and blast replay a BizHawk recording exactly
  (`3_hand_port/vm_model/src/kart/bomb.rs`); in the game it is thrown (or dropped behind when aiming back) and any
  kart sets it off.
- Lane C damage state 6 ("launch") replays a recorded kart; blue shell and bob-omb blasts use it.
- Lane C engine sound: kart engine voices (three nearest the camera) with live pitch/volume/pan
  (`3_hand_port/vm_model/src/engine_sound.rs`, `3_hand_port/game/src/engine_audio.rs`); item sound effects positioned by the camera.
- Lane C blue shell: the route-spline phase (153 ticks of the recording) now replays exactly too; only the
  first 20 steering ticks and the 1 -> 3 switch rule are approximate.
- Lane C music: final-lap fanfare (sequence 62, then the course music 1.17x faster) and the star theme (sequence 73).
- Lane C remaining: blue shell first 20 ticks, bob-omb throw speed with the kart's motion, engine leftovers
  (countdown rev, Doppler, air drop), final-lap fanfare; see `4_docs/lane_c/PROGRESS.md`.
- Lane B particle motion: all six SPL behavior records ported; controlled
  original resource capture matches 9,794 acceleration/random/rotation calls
  and their RNG states. Attraction/plane/convergence are source-derived with
  boundary regressions. Particle birth, full update, wheel timers and native
  SPA effects integration remain next; see `6_data/analysis/CODEX_PARTICLE_MAP.md`.

- Lane C item fidelity (star): hits (shell tumble, banana/hazard spin) and lightning are now refused
  under a star or Bullet Bill, as the game's shared mask 0x10000040 (`kart_plugin::use_items`,
  `strike_lightning`); star timer/on/off decoded in `4_docs/function_notes.md` (451 ticks = timer > 450).
  Still approximated: star-on cancelling Boo, refusal of a star under Bullet Bill, star sparkle/jingle.
- Corrected Goomba "debris" mapping: the original helper creates a mushroom pickup.
  Normal-race launch, flight, growth, landing and spring match all 538 original
  item updates; native qualifying kart hits now create the original mushroom
  asset, and collection invokes the existing 90-tick boost/shove handler.
  Map setting 1 low half disables drops when nonzero; repeated disabled contacts
  cannot create duplicate pickups. Moving platforms, item/object dispatch and
  original audio remain pending. Full core suite: 110 passed, one ignored;
  standard release build and mushroom visual smoke check pass. See
  `6_data/analysis/CODEX_NPC_MAP.md`.

- Goomba normal-contact wobble and squash states 2..5 now match all 600 original
  update calls and three original callbacks (two normal, one qualifying hit).
  Native Star/shrunk contacts trigger stretch/compression/wait/spring-back and
  collision suppression; sprite X/Y scale follows original draw formula.
  One-shot fade/deactivation is source-derived, not independently captured.
  Mario Circuit flat/recovered visual captures pass; airborne state 1,
  item-hit dispatch and audio remain pending. See `6_data/analysis/CODEX_NPC_MAP.md`.

- Original traffic tire model now renders both axle assemblies on buses/cars/trucks;
  rotation comes from the vehicle tick (+1536 angle units), with original type-specific
  scale/spacing. Bus clock and render fields agree with the 900-row original trace.
  Normal terrain probing, heading, tilt, easing and all nine body-matrix words now
  match all 899 bus transitions using native KCL/velocity inputs. Rendering and
  collision axes consume that state. Hit flight/rebound/recovery now additionally
  match 300 original bus updates after one controlled mode-1 overlap; Star/shrunk
  contacts invoke the own-object reaction in the native game. Traffic now uses the
  original asymmetric oriented contact test: all 293 original bus/car/truck calls
  match scaled extents, axis and push. First flight disables contact until rebound,
  including subsequent karts in the same update. Item-hit dispatch and crash/landing
  sounds remain pending.
  Fixed missing SDK T-origin compensation in non-rotated texture matrices, which
  made the quarter-wheel texture appear as two half-wheels.
  Full core suite: 108 passed, one ignored; standard Windows release build and
  Shroom Ridge / Mushroom Bridge visual captures pass. See
  `6_data/analysis/CODEX_NPC_MAP.md` for evidence and remaining vehicle presentation work.
- CPU drift fixed (hop-only direction, facing vector while drifting, CPU hop turn x2): no falls.
- Rubber-banding (`cpu::CpuPace`, `Standings`, `CpuParams` from kartAIparam.bin): 4921/4934 exact.
- CPU skill tables per class, instant mini-turbo roll, start boost / burnout decision.
- CPU target offsets (lateral random walk, `sub_207E944`).
- Star speed (1.2 x top, any terrain, 451 ticks); laps from NKM `STAG` (Baby Park 5).
- CPU item use (`cpu::CpuItems`: per-class wait tables, place-based aiming, 20-degree boost
  check, rival shields); trailing-item handlers simplified to a wait.
- Jump pads (type 12): lift and speed target by variant, +1.0/tick in flight, ends on landing;
  CPU pace not applied in flight.
- Time Trial mode with ghosts (`3_hand_port/game/src/ghost.rs`, `ghosts/<course>.ghost`); player aims
  throws with up/down (W/S).

- Cannons (KCL type 15 -> `kart::cannon`, NKM `KTPC`): Waluigi Pinball start, Airship, DK Pass.
- Boost ramps (type 19): 8.2 degree pitch while grounded. Delfino drawbridge decks as solid
  floors (`movement::WithFloors`, `objects::solid_tops`; always lowered).
- Kart SEs (`3_hand_port/game/src/sfx.rs`).
- Balloon Battle mode (`3_hand_port/game/src/battle.rs`; 6 battle stages, MEPO/MEPA roaming CPUs, rules
  from the manual: 1 up + 4 spare, max 3 up, 3-minute limit).

- Battle CPUs: yaw scale 4096 (`cpu::BATTLE_TURN_SCALE`); battle item tables 7/8 by balloons.
- Damage state 4 "blown" (`KartDamage::blow`, `ItemAction::Blow`): star touch, bob-omb blast,
  vehicles. Character voices (SSAR 2: spin, hit, burnout, start boost, fall).
- Path movers (`objects::Mover`): Goombas, Mushroom Bridge bus/truck/car, rolling rocks,
  Bowser's sliding blocks (speeds from their init code). Static still: Chain Chomps, walking
  trees, crabs, iron balls, Thwomps, Piranha plants, pendulums, fire bars.

- Minimap from the course's `Map2D` (NCGR/NCLR/NSCR decoder `nitro::screen_image`), kart dots;
  world-to-map transform fitted (the game's own not found; battle stages: none yet).

- Visual fixes (user reports 2026-10-08): duplicate wheels (kart bodies carry low-detail
  `kart_tire` wheels; detailed karts hide them), texture matrices applied, pivot rotations
  transposed (fixed skinned/rotated models), detailed drivers `KartModelSub/P_*` for the player
  (now animated through NSBCA `P_*_drive` etc.), spinning/steering tire pivots, drift sparks
  (approximate; real ones in `MainEffect/RaceEffect.spa`), wall sounds by material
  (`sub_210BAFC` table), crash SE 232 only for blown karts.

- Object collision is the game's (`vm_model::obj_collision`): collision classes per object id
  read back from the running game on every course (`5_tools/bizhawk/harvest.lua`: boots, starts
  a GP and swaps the course id at 0x023CDCD8/0x023CDEC0 while it loads, dumps the master
  object array), hit handlers from the game's tables (bump / spin 1-2 / tumble / blow).
  Decorations without a class (most trees, 0x12D palms) are only drawn, as in the game;
  0x12E palms (Cheep Cheep Beach) are r6 x h80 cylinders.
- Race camera ported (`vm_model::camera`, `sub_2076528`): matches BizHawk exactly over a
  recorded turn (`cam_probe.csv`); FOV 60.4 deg vertical, near 0.25, far 1600, eye-vs-KCL test.
  `MKDS_43=1` opens a 4:3 window (1024x768) for side-by-side shots (`5_tools/bizhawk/shot_probe.lua`).
- Pokeys: 3 body sprites + head stacked (`sub_20A79C4`); flat models drawn as billboards.
- `4_docs/FUNCTION_MAP.md` (generated by `5_tools/function_map.py` from source comments +
  `4_docs/function_notes.md`): what each identified game function does.
- `4_docs/FUNCTION_TABLE.csv/.md` (`5_tools/function_table.py`): all 11175 exported functions, status
  known / inferred (area from loaded files + call graph) / sdk / unknown. Goal (user): a 1:1
  meaning for every function. Add meanings to `4_docs/function_notes.md` (or source comments)
  and regenerate.
- Pivot matrices decoded with the NNS sign layout (no more mirrored models): detailed drivers
  face forward without the 180-degree turn, back faces render right.
- Object lifts (item box 12, pipe 13, wooden box / Piranha Plant 10 x scale) for model and body.

## Codex visual-fidelity progress (2026-10-08)
- Detailed driver joint poses now reach SBC skinning through `nitro::Model::parse_all_with_poses`.
  `nitro_driver` implements steering-controlled drive and original clip clock/blend increment;
  `3_hand_port/game/src/driver_animation.rs` selects drive/spin/ordinary win/lose and normal/closed faces.
  Engine screenshot comparison confirms Mario's arms moved inward into the driving pose.
  All 48 detailed-driver clips pass integer-frame skinning/topology checks.
- SPA resource decoder: both race particle archives parse; main archive has 156 emitters,
  47 decoded textures. Original blue flare 126, red flares 22/23 and smoke/red families
  mapped from C. Full particle simulation and replacement of approximate cubes remain pending.
- Original particle scale/color/opacity/texture evaluators now ported in `nitro_particle`:
  885 unique BizHawk calls match exactly, including RNG state; blue/red attachment
  timers and all six SPA behavior callbacks mapped. Native particle creation/motion
  and wheel-controller integration remain pending; see `6_data/analysis/CODEX_PARTICLE_MAP.md`.
- Goomba walking presentation now uses `kuribo.nsbtp` and the original step counter:
  20-frame texture selection plus mirrored second step (`sub_20DB050`), independent
  materials per actor. Close-up engine captures show changing gait frames.
  Squash/recovery states remain pending. Traffic tire clock matches 899 original bus
  transitions; separate tire geometry and body presentation remain pending.
  See `6_data/analysis/CODEX_NPC_MAP.md`.
- Fall detection now uses accepted movement-contact flags, matching `sub_1FFA4B4`, and
  suppresses type 10 during wall contact as the original does. ROM regression exercises
  186 Rainbow Road backfaces falsely accepted by the former second unswept probe.
  Seed-1 native comparison over 6,000 render frames still produces four identical type-11
  falls before/after; remaining autopilot falls need diagnosis. See `6_data/analysis/CODEX_PARTICLE_MAP.md`.

- Object behaviours from the game's code, each replayed exactly against BizHawk traces
  (`5_tools/bizhawk/obj_trace.lua` + `obj_trace_cfg.lua`; fixtures in `3_hand_port/vm_model/tests/data`):
  path follower and segment builder (`vm_model::mapobj::path`), Thwomp (glide / slam,
  flattens karts: `KartShrink::flatten`), path Chain Chomp 0x1A5, chained Chain Chomp 0x196
  (wander exact; its lunge aims through an uninitialised word in the game, approximated),
  Goomba walk. Object RNG `mapobj::ObjRng`, kart turn round-robin (`objects::ObjectWorld`).
- Function table now: known 438 (checked), described 7675 (agent sweeps in 4_docs/function_notes/,
  unverified), sdk 511, out of scope 2472, open 79. Object models from game code
  (`vm_model::obj_models`, 5_tools/make_object_models.py); rocks, traffic, Bowser blocks ported
  (replay-exact); Mover approximation removed.
- (older) Function table: 5_tools/infer_functions.py guesses (getters, wrappers, hardware, SEs, effects,
  state machines) + address-neighbour areas. 11175 functions: known 372, inferred 5750, sdk
  512, out of scope 2472 (overlay 0 = online play, overlay 3 = Wi-Fi setup utility; the user
  said to ignore them), unknown 2069. Overlay 1 (race: missions, bosses) C is in 6_data/export/plan1.

## Open user reports
- Driver presentation: victory idle alternation, complete special-mode results and one-shot
  return logic; capture spin/win/lose, face changes and crossfades against the emulator.
- Rainbow Road spiral falls; original drift particle simulation from `RaceEffect.spa`.
- Object reactions: traffic hit/bounce and asymmetric contact geometry ported; item-hit dispatch next.
  Goomba wobble/squash/recovery states now match 600 original updates and three
  callbacks; normal/Star/shrunk contacts drive native squash, disabled contact,
  stretch and spring-back. Other own-object callbacks (crab knock, Chomp) remain
  unported, moving-object shove (handler flag 1), handler 9/10 exact damage (taken as blown).

## Long-term: "bring your own ROM" release (user, 2026-10-08; lower priority than finishing the game)
Like the SM64 PC port: ship only our code; the player supplies their own MKDS `.nds`. The game
already reads everything from the user's ROM at runtime (`NdsRom::open`, `MKDS_ROM`). To finish:
- Move the tables now hard-coded from ARM9 (object classes/handlers in `obj_collision.rs`, item
  tables, camera constants, ...) to reads from the user's ARM9 at startup (addresses + ROM
  checksum check), so no game data lives in our source.
- A first-run tool / screen: pick the `.nds`, verify the SHA-1 (USA `AMCE`), cache extracted
  assets, clear error for wrong dumps/regions.

## Same-seed comparisons with the emulator (user idea)
Read the game's RNG state from a savestate (find the race RNG global with a RAM diff) and start
our race with it, so CPU/item behaviour can be compared frame by frame against BizHawk.

## Course sweep (autopilot, 6000 ticks; falls) - see 8_scratch/sweep.sh
OK: Figure-8, Yoshi Falls, Cheep Cheep, Luigi's Mansion, Desert(1), Delfino(0 after bridge),
Pinball(0 after cannon), Shroom Ridge, DK Pass, Mario Circuit, Airship, Wario Stadium, Peach
Gardens, SNES MC1, N64 Moo Moo, GBA Peach. Rainbow Road ~3-11 (cluster at 500,550,400).
Tick-Tock Clock and Bowser's Castle fixed with turning disc platforms (`objects::platforms`,
gears 0xCB, rotating floor 0xD0; their speed-up / run / slow / reverse / rest states:
`vm_model::mapobj::turner`). All 32 race courses
run with 0-1 falls per autopilot race (Rainbow Road a few).

### Sweep 2026-10-10 (claude-lane-a, T017; `5_tools/native/sweep.ps1`, own exe, seed 1, 6000 ticks, autopilot)
All 32 courses exit 0, no panics. 18 falls in all: Rainbow Road 13 (baseline above said ~3-11; Lane B's T006 owns it), 1 each on Tick-Tock Clock, Mario Circuit, Bowser's Castle, `old_noko_sfc` and `old_choco_64`; every other course 0. Results: `8_scratch/sweepA.csv`, `sweepB.csv`. Re-run after big kart/collision changes: `pwsh 5_tools/native/sweep.ps1 -Executable <own exe> -Name mysweep` (about 55 min sequential; run two halves with `-Courses` in parallel).

## Next big goal (in order)
1. (optional) exact trailing-item handlers (`0x0215524C` table) and player throw direction
   (hold up/down when releasing).
2. (done: see the Lane A table in `PROGRESS.md`; the numbering is kept because other files cite items 4 onward)
3. Map objects: remaining behaviours: rocks 0x192/0x1B1, traffic 0x195/0x19A/0x19C,
   (rocks, traffic, Bowser blocks, crab walk, Pokey walk, walking trees, Cheep Cheep hops,
   pendulum, clock hands + their box collision: done; replay-exact or within 1 unit)
   Done since: Monty Moles, drawbridge (agent; deck = hinged ramp/wall floor), fire rings
   (hit test of outer fireballs, spin), pinball bumpers (bounce 12 units), moving-object
   shove (handler flag 1), Airship objects (bullet launchers fire Bullet Bills that blow karts,
   path sliders, hatches; in game, autopilot 0-1 falls from bullet blows). Pinball iron balls + flippers
   (agent port, in game: kicks, box contact, shove 12/14). Left: drums 0xD2, balls 0x1B3,
   fallback decoration models (agent stopped).
   Bats: spawner 0x1A0 throws 0x19F bats (agent port `mapobj::bats`, in game).
   Drums 0xD2, chandeliers/paintings/sun (.nsbca on objects) done.
   Boos (0x13D spawners) and bakubaku 0x13C done (agent port `mapobj::boo`).
   Left: Mansion 0xC9 path item
   boxes (Lane C), objects' star reactions: all done (own table, chained Chomp, Monty, Cheep,
   Piranha, path Chomp, rocks, crab, Pokey, snowman, Bullet Bill, iron ball), Piranha bite anim, snowman 0x19D. Method:
   obj_trace.lua -> writer pc -> state
   table (def +0x10 manager record +8 / state machine at +0x80) -> port -> replay test.
4. Item fidelity: star invincibility/knock, blue shell, bob-omb, blooper, Boo, bullet bill,
   triple/trailing items (record each in BizHawk, write fixture, port).
5. Sound: kart SEs, engine voices, item positioning and selected remote wall/charge/mini-turbo cues are wired. Remaining: original timer/mixer parity, damage voices and other remote event sources; see `4_docs/CODEX_SOUND_WORK_LOG.md`.
6. Battle fidelity: the game's battle CPU AI (tables set by `sub_2090354`, driver mode for
   cfg+8 == 2) so CPUs hunt; balloon models on karts; balloon stealing; verify the balloon
   rules in BizHawk. Shine Runners. Missions last.

- Water (found from the engine-sound work, see 4_docs/lane_c/sound.md 'Resolved'): `sub_206FE08` slows/sinks karts below the course water surface (`sub_20D3D48`, object `*0x217B4C4`) and drives the underwater engine pitch; none of it is ported. Needs the water object (map-object lane) and the kart step.

- 2026-10-10 Codex moving-box precision follow-up:30 original-world probes match core/adapter after signed negative scale-add center correction. Final private Windows run exited0 at6000 ticks/frame1224 with1 fall outside the blocks, no sliding-block falls; screenshot reviewed. All79 BizHawk Lua scripts parse after fixing mt_run.lua and autodrive_plan_triple.lua path escapes. Remaining terrain motion/lowest/aggregation belongs to T022.

- 2026-10-10 Codex CPU input/order: prevent keyboard, screenshot and manual countdown writers from overwriting Cpu-controlled PlayerKart; sort CPU updates by Racer.index (364 original calls/52 frames verify1..7 order). Regression/private release pass; twin6000-tick seed1 Bowser runs zero falls, all69 selected debug records identical. Original player0 takeover order/full RNG/trajectory parity still unverified.

- Rainbow Road follow-up (Codex, 2026-10-10): same private input/order release exits0 at6000 ticks/frame5770 with19 falls (CPU7:7; player0,CPU1/2/5/6:2 each; CPU3/4:1 each), all flags0x84000800. One racer reached lap2; others remain lap1. Screenshot reviewed on spiral; spiral falls remain unresolved. Numeric positions: 8_scratch/codex_rainbow_order_falls.json. Prior10-fall run used a different shared build; no isolated causal comparison or broad regression verdict.

- 2026-10-10 Codex Rainbow routing: all89 real swept fall-contact queries exactly match original hit/push/flags; ROM-backed replay passes. C identifies boost-ramp CPU guards, now ported through CpuKart.ramp: crossing-plane reach only during ramp flight, exact node target without wander/offset/RNG consumption. Two new regressions plus existing recovery pass; CPU heading still matches3500 original calls. Native end-to-end rerun pending; spiral falls not yet resolved.

- 2026-10-10 Codex particle validation: original child-emission guard now handles resources without SPA flag0x10000 using the primary-only pool path. New lifetime/list/RNG/polygon parity test and original child-particle replay pass. First Rainbow ramp-guard run exited101 before6000 capture because of this panic; discarded as a completed sweep. Private rebuild also exposed Piranha component visibility; three pub(crate) qualifiers unblock cross-module system ordering without behavior changes. Final native rerun remains pending.

- 2026-10-10 Codex final ramp/particle verification: corrected private Windows release built; completed seed1 native6000-tick runs exit0. Bowser:0 falls, render2219. Rainbow:18 falls, render2232 (CPU6:7, CPU1:4, CPU4:3, CPU5:2, CPU2/7:1; player0 and CPU3:0); player0 and CPU3 reach lap2. Both screenshots reviewed. Compared with prior frozen19-fall Rainbow run, shared source changed concurrently; no isolated causal improvement claim. Spiral falls remain open. Numeric results/positions: 8_scratch/codex_ramp_guards_results.json. Source-backed ramp guards and optional-child fix retained; focused release regressions and3500 original heading replay pass. Next: capture cursor targets, body up/facing and motion at the first spiral divergence, rather than changing the already89-query-exact fall detector.

- 2026-10-10 Codex Rainbow root cause: ported fixed local ramp pitch and original ramp*drift matrix concatenation. All14731 original facing outputs match, including2004 ramp/854 inverted calls; old world-Y branch disagreed1129 times. CPU target-order fix also matches14000 original steering calls (65 old-target sign errors). Private release built; Rainbow seed1 completed6000ticks/frame1452 ZERO falls, all8 racers lap2. Traced upper-loop region has642 samples, all grounded,344 inverted (before pitch fix first falling CPU spent171 ticks airborne). Bowser completed6003ticks/frame1510 ZERO falls. Screenshots reviewed. Rainbow seed2/Airship validation pending; no full-game or paired-RNG parity claim.

- 2026-10-10 Codex final Rainbow verification: two seeds completed6000/6001 ticks with ZERO falls, every racer lap2; Bowser/Airship completed6003 ticks with ZERO falls. Screenshots reviewed. Exact replays:14000 steering,14731 facing (2004 ramps/854 inverted), plus existing3500 headings and89 terrain queries. Fixed original local pitch/matrix order and route-before-steering; regular spiral falls addressed on tested seeds. Full32-course/full-three-lap/RNG parity remain. Details: 4_docs/CODEX_RAINBOW_WORK_LOG.md; native summary 8_scratch/codex_local_pitch_results.json.
