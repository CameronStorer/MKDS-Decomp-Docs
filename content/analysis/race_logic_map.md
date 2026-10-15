# Race logic map (MKDS, AMCE): input-anchored findings

Addresses are real RAM addresses from the clean IDA load (`tools/nds_extract.py` +
`tools/ida_load_nds.py` + `tools/ida_fix_thumb_switches.py`). Location keys use the notation of
`tools/sm_scan.py` / `tools/key_xref.py`: `[[G]+off]` = field `off` of the object pointed to by the
global pointer stored at `G`.

**Confidence:** *Confirmed* means read directly from decompiled code. *Hypothesis* means inferred from
structure and not yet verified.

## 1. Input pipeline (confirmed)

```
KEYINPUT 0x04000130 | ARM7 mirror 0x027FFFA8 (X/Y, lid bit 15)
  -> sub_2043A34   inlined PAD_Read: ((ext|key) ^ 0x2FFF) & 0x2FFF; 0 if lid closed
  -> [[0x02175604]+0x2]:u16   raw buttons (input object; +0x4 flags, +0x8/+0xC mode/recording)
  -> sub_2046D7C   touch-panel sampling into input object (+0x28 samples, +0x30 flags)
  -> sub_2043648   per-frame fan-out to 10 controller slots
  -> sub_2039530   per-slot edge/repeat/soft-reset update
```

`sub_2043648` source types (slot `+0x3C`): 0 none, 1 generated (`sub_204A664`),
2 local buttons with optional **left/right swap** (input-object flag `+4 & 4`; likely mirror mode),
3/7 injected value, 4 network (`[[0x0217A9E0]+0x15C8]`), 5 network/alt, 6 raw local.
Final keys are masked by slot `+0x42` (enabled buttons).

### Controller slot (10 × 92 bytes at `0x02175608`)

| off | field |
|---|---|
| +0x00 | pressed (`held & ~prev`) |
| +0x02 | **held**: what kart code reads |
| +0x04 | released |
| +0x06 | auto-repeat output; repeat FSM at +0x08 (0 idle / 1 initial delay / 2 repeating), timer +0x0A, mask +0x0C, delays +0x0E / +0x10 |
| +0x12..+0x1E | L+R+Start+Select (`0x30C`) hold detector (soft reset) |
| +0x3C | source type (above) |
| +0x42 | enabled-button mask (kart code writes 0xFF7 / 0xE04) |
| +0x48.. | touch block (`sub_2046CA8`) |

Slots 0–7: racers (indexed by kart `+0x78`). Slot 8: UI (menus read pressed `+0x2E0` and touch `+0x328..+0x338`).

## 2. Kart object (partially confirmed)

Kart code in `arm9_main` roughly `0x02060000`–`0x02095000`. The kart is a **flag/counter state
machine**, not a `switch`.

| off | meaning | evidence |
|---|---|---|
| +0x44 (68) | state flags: 1 hop, 2 ?, 8 drifting, 0x10 grounded?, 0x8000 drift cancelled | `sub_206C5E4` |
| +0x48 (72) | input/steer flags: 0x8 left, 0x10 right, 0x2 ? | same |
| +0x4C (76) | flags (0x8000 → sound/effect calls) | same |
| +0x74 (116) | id used for effect/sound handle (`sub_208C5B8`) | same |
| +0x78 (120) | **player / controller index** | `ctrl[+0x78].held` in 6+ functions |
| +0x7C (124) | flags (0x1 local human?, 0x400 input disabled) | same |
| +0x23C (572) | mini-turbo timer | `sub_206C5E4` |
| +0x2A4 (676) | speed (20.12 fixed point) | compared to stats top speed |
| +0x2C4 (708) | drift direction −1/0/+1 | same |
| +0x2CC (716) | → kart stats table (+0x0E mini-turbo duration, +0x10 top speed) | same |
| +0x2FC (764) | drift charge level 1..4 (4 = mini-turbo ready) | same |
| +0x380 (896) | frames since start (hop allowed when ≥ 5) | same |

Buttons (held, `+0x2`): A/B `& 3` accelerate/brake (`sub_20641F0`), R `& 0x100` hop/drift (`sub_206C5E4`), Up `& 0x40` (`sub_20EF4A0`, `sub_20F0154`; those index by `+0x200`).

### Kart array and full layout

- `getKart(i)` = `sub_207A974`: `*(u32*)0x0217ACF8 + 0x5A8 * i`. **Kart object size 0x5A8**; independently,
  the highest field `tools/struct_map.py` recovered is +0x5A4 (u32), which ends exactly at the object size.
- Full recovered layout: `analysis/kart_struct.md` / `.json` (272 functions accepted by evidence, 176 strict;
  286 confirmed + 70 likely direct fields, nested structs at +0x9C, +0x12C, +0x168, +0x2CC (stats), +0x508, +0x514, +0x590).
  IR Rust layout: `vm_model/src/ir/kart_layout.rs` (`KartRaw`, offsets compile-time asserted).
- Runtime (BizHawk 2.11, melonDS core): addresses verified live. The code word at 0x0207A988 reads 0x0217ACF8 as
  in the static image, and an execute hook on `sub_2043A34` fires once per frame. Kart array is null outside races.
  Tools: `tools/bizhawk/` (`kart_logger.lua`, `func_coverage.lua`, `analyze_kart_log.py`).

### Runtime-confirmed fields (BizHawk, GP 50cc SNES Mario Circuit 1 (Shell Cup race 1; earlier mislabelled SNES Mario Circuit 1 Circuit), Mario / B Dasher, kart 0)

Recorded unattended by `tools/bizhawk/autodrive.lua` from `race_start.State`: `kart_log.csv` (2,696 frames:
accelerate, steer, brake/reverse, hops, drifts; partly stuck on a wall) and `kart_log_drift.csv` (328 frames:
hop, left drift, closed-loop counter-steer until charged, mini-turbo). Reports: `analysis/kart_runtime.md`,
`analysis/kart_runtime_drift.md`. Corrections to the table above are marked **(corrected)**.

| off | meaning | runtime evidence |
|---|---|---|
| +0x78 | player / controller index | 0 for the human kart |
| +0x44 | state flags | 0x10 clear while airborne in a hop; 0x2/0x4/0x800 set at hop start; 0x8 set while drifting; 0x100 while reversing; 0x80 after hitting the wall / off-road; 0x400 and 0x1000 while not accelerating |
| +0x48 | input intent flags | 0x2 accelerate (A), 0x4 brake (B), 0x8 steer left, 0x10 steer right; **0x80000 during mini-turbo boost** (plus 0x20) |
| +0x464 | accelerate held (0/1) | value = A (correlation +1.00) |
| +0xEC | **(corrected)** w of the yaw quaternion +0xE0 (`sub_1FFD190`), not a steering amount | = cos(yaw/2): 6 at yaw 32760; follows turns because yaw does |
| +0x2A8 | **forward speed, signed** | 0→21,396 on A (B Dasher at 50cc), ~10,170 cap off-road, negative while reversing with B |
| +0x2A4 | speed magnitude **(corrected)**: not the same as +0x2A8; this is what the drift checks compare to top speed (`sub_206C5E4`) | e.g. 4,183 vs +0x2A8 = 79 when pushing against a wall |
| +0x2C4 | drift direction −1 / 0 / +1 | set on hop with a direction; cleared when the drift ends (release R, or off-road) |
| +0x2FC | drift charge: 0 none, 1 drifting, 2 charging, 4 mini-turbo ready | 1 on landing, 2 after the first counter-steer pair, 4 after the second |
| +0x300 / +0x302 | u16 counted **Left / Right presses** **(corrected)**; +0x304/+0x308 point at whichever is "toward"/"away" for the drift | `sub_20681F0`: new presses only, 10-tick cooldown (+0x30C); an away press counts if away == toward, a toward press counts if away > toward and raises the charge |
| +0x23C | mini-turbo timer | 34 on release, −1 per frame; speed 21,390 → 27,822 for exactly those frames |
| +0x380 | hop airborne frames **(corrected)** | 1, 2, … 13 during a hop, 0 on landing (not "frames since start") |
| +0x4D0 | frame counter | +1 every frame |

Ported: `vm_model/src/kart.rs` (`KartInput`, `KartMotion`, `KartDrift`, `MiniTurbo`, `KartStats`, `step`) and
`vm_model/src/kart_plugin.rs` (`KartPlugin`, FixedUpdate). The test `replays_recorded_mini_turbo` replays the
recorded input and matches every logged transition frame. Stats table (live, Mario / B Dasher / 50cc): +0x0E = 35
mini-turbo ticks, +0x10 = 21396 top speed, +0x14 = 225 / +0x18 = 94 acceleration steps, +0x1C = 2867.

### Speed pipeline (confirmed: code + write-watch + exact replay)

Per-kart tick `sub_1FFCC50`: `sub_1FFBE70` target limit -> `sub_1FFBE04` limit -> `sub_1FFBD9C` ratio ->
`sub_1FFC6C0` (`sub_206C5E4` drift, `sub_1FFBA68` acceleration) -> `sub_1FF9D18` (mini-turbo countdown) ->
`sub_1FFB130` movement (`sub_1FFB9E0` friction, `sub_1FFAF18` cap, `sub_1FFAE14` |velocity|).
Which code writes which field was measured with `autodrive.lua`'s `watch_writes` (BizHawk `onmemorywrite` + ARM9
r15) and `tools/bizhawk/watch_report.py`.

| off | meaning |
|---|---|
| +0xCC | target limit = top × terrain (+0xDC) × slope (+0xD4 × +0xD8); boosting × 5325/4096 (1.30005); non-mini-turbo boosts use raw top |
| +0xD0 | effective limit: rises to the target at once, eases down × 3895/4096 (0.951) per tick |
| +0xDC | terrain multiplier; eases to 1947 (0.475) on SNES Mario Circuit 1's off-road |
| +0x2A0 | `FX_Div(|velocity|, limit)` clamped to 1.0 (hardware divider, rounded) |
| +0x2A8 | engine speed: + stats curve (225 below ratio 0.5, linear to 94 at stats +0x1C = 2867/4096, 94 above); drifting: flat stats +0x20 = 249; brake −410; boost +4096; only while grounded |
| +0x2A4 | |velocity|; flat road: `sqrt(fwd² + 4182²)`, rounded (21396 -> 21801) |
| +0x238 | boost timer (`sub_206D020` start = max, `sub_206CEB4` countdown); +0x48 bit 0x20 while active, 0x20000000 = ignores terrain |
| +0x44 bit 0x400 | coasting (no pedal, grounded): speed × stats +0x2C (4030/4096) |

Cap: |speed| > limit -> limit; |speed| ≤ 410 with no pedal -> 0. `vm_model/src/kart/speed.rs`; the test
`replays_recorded_speed_session` replays `vm_model/tests/data/kart_speed_session.csv` (317 ticks: from rest, hop,
drift, mini-turbo, decay, grass, coast, reverse) free-running and matches every frame exactly.

### Steering, movement and orientation (confirmed: code + write-watch + exact replay)

Per tick: `sub_1FFC5A0` pedal intents (A+B -> neither, 0x80) -> `sub_206C494` A+B pivot -> `sub_1FFC27C`/`sub_1FFC158`
steering -> `sub_206C5E4` drift -> `sub_1FFBA68` acceleration -> `sub_1FFC090` turn -> `sub_1FFB130` movement;
then collision `sub_1FFCB58` (contact `sub_1FFA4B4`, rest `sub_2070398`, surface `sub_1FF9E5C`, orientation `sub_1FF9F60`).

| off | meaning |
|---|---|
| +0x80 | position (vec3, fx12); +0x8C position at tick start |
| +0x236 | yaw (u16 angle, 65536 = turn; increasing = left) |
| +0x3EC / +0x3F0 | target turn rate (reset each tick) / applied turn rate: eases ×1638/4096 (rounded), added to yaw |
| +0x2D4 | lean ±4096: +1638/tick while steering, ×3690/4096 decay; at speed > 12288 costs `speed·492/4096·|lean|/4096` of that tick's displacement |
| +0x388 / +0x38A | drift angle / slide bonus (landing: `26·|vel|/4096`; decays ×3891 to 50); hop yaw becomes drift angle on landing (atan2 of saved vs current forward, `0x28BE60DB9391` rad->angle) |
| +0x3DC / +0x240 / +0xDC | surface kind (-1 airborne) / grip (stats +0x38 + 4·kind) / speed multiplier (stats +0x68 + 4·kind, eased ×1229 when dropping) |
| +0x244 | ground normal; +0x278 heading = basis right × normal (ground) or basis forward (air) |
| +0x50 | facing = heading rotated by drift angle about the normal; +0xD4 slope = |facing along ground| |
| +0x68 | travel direction: += (facing − travel)·grip/4096 on the ground; frozen in the air |
| +0xA4 | velocity = travel·speed + (0, +0x260, 0) (+ impulses); +0x2A4 = |velocity| (cap 53248) |
| +0x260 | vertical speed: gravity +0xC8 = −697/tick; hop +8610; contact while falling -> −3485 |
| +0x2B8 / +0x2BC | visual hop bounce speed / height (body only; tilts the basis during the hop) |
| +0xE0 / +0xF0 / +0x120 | yaw quaternion / ground-tilt quaternion / basis rows (right, up, forward) from normalize(ground·yaw·hop tilt) |
| +0x44 bit 0x1000 | resting: forward speed 0 on contact -> velocity 0, horizontal position held |

SDK math reproduced bit-exactly in `vm_model/src/kart/fxmath.rs` (VEC_Normalize/Mag with the hardware sqrt/divider,
FX_Atan2, MTX_RotAxis33, quaternion ops); the sin/cos and atan tables equal `round(sin·4096)` / `round(atan(i/128)·4096)`.
The tests `replays_recorded_speed_session` and `replays_recorded_steering_session` (`tests/data/kart_steer_session.csv`:
plain steering, braking, A+B pivots, grass) match every recorded field on every frame (789 frames), driven only by
buttons and the reported surface kind. Not yet ported: ground alignment on slopes, wall reactions (bounce/speed loss), map objects.

### Course collision (KCL) (confirmed: ARM code + exact push-outs)

Courses are `data/Course/<name>.carc` (LZ10 + NARC) -> `course_collision.kcl`; the recordings are on
`old_mario_sfc` (SNES Mario Circuit 1; Figure-8 Circuit is `cross_course`). Read at run time from the
user's ROM by `vm_model/src/assets.rs`. Runtime header at `0x0217B5F4` = file header with offsets fixed up.

Sphere query `sub_1FFDEE4` (ITCM; IDA splits it and decodes parts as Thumb, so it was ported from a
Capstone listing: `tools/arm_disasm.py`): octree leaf -> per prism face/edge/corner contact (`sub_1FFF434`
corner line point, hardware sqrt), previous-centre rejections, push-outs `(pen·n)>>2` accumulated per class
(floor types `0x1E34EF`, wall types `0x214300`, type 16 special wall) as per-axis max+min, combined `>>10`;
16-entry hit list (flags, attribute). Surface = strongest floor hit's collision type through
`[0,5,2,3,0,4,6,8,0,0,0,0,8,0,0,9,0,10,8,11,0,0]` (function table `0x02154D8C`; types 7/12/18/19 also
trigger boosts/jumps, not ported).

Kart sphere: radius stats +0x00 (45056), centre = position + body up (+0x15C = basis up of the previous
tick, tilted during hops) · (radius + 1024). Ported in `vm_model/src/kart/kcl.rs`; `sphere_test_matches_recorded_pushouts`
reproduces the game's push-out (`pos[t] − pos[t−1] − vel[t]`) on all 2533 frames of `kart_log.csv`
(floor, ~1700 wall frames, edges, corners, hop tilt); both session replays stay exact with `KclGround`.

## 3. Race configuration object `[0x021759A0]` (confirmed structure, hypothesised meaning)

- Active settings at `+0x000..+0x1E7`; **pending copy at `+0x1E8`**, written by menus.
- `sub_2044940` commits pending → active (488-byte copy), then `sub_2045084(i)` for i = 0..7 (per-racer setup).
  Callers: `sub_2039F9C`, `sub_2045590` (← `sub_2039CBC`, `sub_203B0F8`, `sub_20AD344`).
- Read by the kart module (never written there): `+0x8` (6 states; read by 330 functions game-wide; **hypothesis: game mode**),
  `+0x0` (36 states; **hypothesis: course/stage id**), `+0xC` (7 states), `+0x3D0` u8 (6 states), `+0x14` (3 states).
  `+0x8 == 4` routes the mini-turbo path into ov000 (`sub_21816FC`).

## 4. Other machines (from `analysis/state_machines.md`)

- `[[0x0217A9E0]+0xC]` (47 states, 56 fns) / `+0x4` (12 states): object that also holds remote players' input
  (`+0x15C8`); **likely the multiplayer/network session**, not game flow.
- `[[0x0217B41C]+0xC]` (31 states, 30 fns, arm9 + ov001): surfaced by the switch fix; next candidate for top-level game/menu flow.
- `0x0217D1EC` (8 states): mode variable driven from ov001.

## 5. Tooling notes

- 221 functions originally hid their switch bodies behind an unrecovered Thumb jump-table idiom
  (`ADDS/ADD PC/LDRH/LSLS/ASRS/ADD PC/BX`); `tools/ida_fix_thumb_switches.py` recovers 265 sites
  (4 jump-table `BX` left in total). Backups of the pre-fix databases: `tools/idb/backup_before_switchfix/`.
- Literal-pool calls (`off_X(...)`) are resolved to `sub_` targets in `analysis/xref.json`.
- Some tiny ARM "functions" in `0x02028xxx`/`0x0202Exxx`/`0x020ACxxx`... are mis-split stubs that point back
  into themselves; ignore them as getters.

### Slopes, walls and other karts (confirmed: code + exact replays)

- **Ground alignment** (`sub_1FF9F60`): ground tilt quaternion +0xF0 lerps toward +0x100 at rate +0x3A8.
  On the ground (airborne ≤ 5) the target is `between(UP, floor normal)` (`sub_1FFD0E8`, rounded cross,
  FX_Sqrt), kept on one hemisphere (+0x48 bit 31); rate (`sub_1FFA11C`): dot(old, new normal) < 0.9 ->
  492·speed ratio, else +20/tick up to 492 (0 while resting). In the air: rate 246, target = air-pitch
  attitude (`sub_2070484`). Orientation = normalize(tilt · yaw · hop tilt); sphere offset = body up.
- **Hop flag** +0x44 0x800 clears when the visual bounce ends (mask 0x804 in `sub_1FF9C40`), not on touchdown.
- **Walls** (`sub_1FFA4B4` -> `sub_206F574` -> `sub_206F04C`, types 8/9/21 = `0x200300`): head-on factor
  clamp(facing_signed·n + 1, 41/4096..1) -> speed-cap factor +0x38C (×0.8; 0.3 when backing into it), bounce
  `n·(n·v)` into +0x2D8 -> +0x2E4 -> +0x2F0 (two-tick delay, ×0.93/0.98 decay), yaw kick +0x386 (×0.9 decay),
  boosts cancelled, drift charge/angle reset; slide impulse +0x1FC from the sphere test's slide vector
  (`sub_206F694`); ledge knock +0x374 (`sub_1FFA478`). Braking in reverse caps reverse speed at 12288.
- **Frame structure** (`sub_207AAEC`): pass 1 runs every kart's prologue (`sub_1FFCAC0`: clears +0x2B0 pair
  bits, 0x44 mask 0x57FFFFDF, shifts the bounce chain); `sub_207A32C`; pass 2 runs each kart's update (+0x218:
  control, movement, broadphase query, contact, slipstream) in kart order; pass 3 (+0x21C) runs ground contact.
  Kart 0 goes first, so it meets the others as of the end of the previous frame.
- **Broadphase** (`sub_1FFDB70` / `sub_1FFD900`, mask 0xE800): see `kart/traffic.rs`. The query result
  (count 0x0217B588, flags 0x0217B59C, owners 0x0217B5A4) is scratch, reused by every kart.
- **Kart-to-kart contact** (`sub_206DFD0`): skipped if self +0x7C & 0x402000 or +0x48 & 0x40. For each result
  with flag 0x8000 not already paired (+0x2B0 bits) nor excluded (+0x7C & 0x402020, +0x48 & 0x40): contact
  centres +0x1D8 = pos + up(+0x12C)·(r + kart stats +4 = −11264), set right after moving (`sub_1FFC064`). If they
  overlap (|d| < r1+r2): sep = unit(d)·rsum − d (`sub_20EB3F0`); each kart moves by ±sep/2 (projected off its
  ground normal if grounded, off its wall normal if touching a wall and pushing into the ground); a kart with
  +0x44 & 0xC0 trades speed: other's +0x2A8 += facing·(n·(n·(v_this − v_other))). Star (+0x4C 0x10000000) /
  mega (0x40) have their own reactions; otherwise `sub_206D7C8` both ways. Bump sound/spark/spin (+0x3D4
  cooldown, +0x3D2, +0x594/+0x598, `sub_2071318`, `sub_206C354`) are presentation. Both get +0x44 |= 0x20,
  which `sub_1FFCB58` turns into 0x80000 at the next ground contact: `sub_1FFAF18` then skips the stop snap.
- **Push** (`sub_206D7C8(pusher, target, n, first, dir)`): w = kart stats +0x0C + character stats +4 (Mario/B Dasher
  2662 + 2048). Factor: CPU (+0x7C & 0x600) 819 if ratio > 0, else the ratio; human 2·ratio (min 819) up
  to ratio 0.5, else 4096. +0x4C 0x80 (shrunk): both weights /8; pusher +0x48 0x100000: ×2; target's: /4.
  s = ((w_p · min(FX_Div(w_p, w_t), 20480)) >> 12) · factor >> 12. Push n·s minus its part along the target's
  facing (negated when +0x44 & 0x100), normalized, ×s, y ≤ 0, minus its part along the ground normal, goes into
  bounce +0x2D8 (x, z) and vertical speed +0x260. The second call (first = 0) swaps a direction within 0.1 of
  the first for zero.
- **Slipstream** (`sub_206D578`): round-robin slot `*(*0x02061FA0 + 12)`; see `kart/slipstream.rs`.
- Lightning shrinks the radius (+0x1D0 ×0.7) and sets +0x4C 0x80; not ported.

Replays (only buttons fed in): SNES Mario Circuit 1 wall session 2695/2695 frames exact; Figure-8 Circuit
(`tools/bizhawk/figure8_start.State`, autopilot along the course's EPOI line, CPU karts from the recording via
`traffic_figure8.csv`) exact for 1770 frames, through the climb, hops on slopes, slipstreams and the bumps of
frames 4009-4012, until lightning at 4701. Sphere test exact on 2751 Figure-8 frames.

### Items and damage (confirmed: code + exact replays of the Figure-8 sessions)

- **Item dispatch** `sub_206D18C` (per kart, after moving, before kart contact) switches on the touching item
  object's type (`sub_20FA4C8`: broadphase flag 0x4000, exact test `sub_20F97E0`): 0/1/7 shells -> tumble
  (`sub_206B4D0`), 2 banana -> spin 1 turn (`sub_206BCB0(k,1,0)`), 3 mushroom -> `sub_206D020(k,0,90)` + +0x48
  0x100000 with +0x538 = 90 (bump shove: pusher weight x2, target's /4), 4 star (`sub_2069C38`), 6 lightning ->
  `sub_206A624` on every other kart, 5/9 blue shell / bomb.
- **Map objects** `sub_206E874` (after the broadphase query): per-object callbacks return flags 8 (wall reaction),
  2 (cap factor by head-on-ness), 1 (push: speed-cap terms +0x39C/+0x3A0); item boxes return none.
- **Damage state** +0x180, handlers at 0x021655C4: 2 = spin (`sub_206BB04`), 3 = tumble (`sub_206B16C`); 4, 5, 6, 8
  not mapped. Hit start `sub_206BF88`: +0x44 &= 0xFFFFF7F4 (hop, takeoff, drift), drift dir/charge/counters 0,
  +0x48 &= 0xDFE77FDF (boost, terrain-ignore, mini-turbo, shove), boost/mini-turbo/shove timers 0, slipstream boost
  off. While +0x180 != 0: `sub_1FFC6C0` skips pivot/steer/drift/accel (turn still applied), `sub_1FFB9E0` friction
  every tick, no lean drag (`sub_1FFB930`), input mask 0xE04 at 0x217564A (`sub_1FFC67C`; also +0x48 &
  0x06052840), applied when the pad is next read (`sub_2043648`).
- **Spin** (`sub_206BBB4`): rate ±1872 (sign of lean +0x2D4), turns +0x366, progress +0x368 advanced in
  `sub_1FFA4B4`; done past turns·0xFFFF; then +0x48 |= 0x44000, +0x23A = 10 (lock). Visual only (+0x150 matrix).
- **Tumble** (`sub_206B358`): fwd = (fwd + 2048)·2458; flip axis +0x31C = norm(right + 738·forward), rate +0x360
  1638 (-10/tick), progress +0x318, angle +0x314, quaternion +0x34C. Handler: progress 0 -> vy 9421; landed
  (+0x44 0x10000) -> vy 7373, then 4096; after one turn 30 ticks (+0x35C). +0x4C 0x10 makes `sub_20641F0` build
  the collision matrix +0x150 = M1 · T(-5·up) · R(flip) · T(5·up); the sphere (`sub_1FFC008`) uses its up row
  +0x15C and translation +0x98.
- **Lightning** (`sub_206A624`): +0x394 = 2867, timer +0x53A = {510,450,390,330,270,210,150,90}[place-1],
  +0x4C 0x80, spin 2 turns. `sub_206A354`: count down, 25-tick grow (+0x53C), then +0x394 = 4096. Radius
  `sub_1FFCA50` = stats r · +0x394; speed cap `sub_1FFAF18` = limit · (cap factor · +0x394).
- **Air** (`sub_1FF9F60` / `sub_2070484`): airborne > 5 -> +0x3F8 = max(|velocity dir +0xB0 · forward +0x138|, 2867)
  unless hop takeoff (+0x44 0x2), scaling next tick's velocity (`sub_1FFAE14`). Landing `sub_206EDAC`: if falling
  and (airborne > 25 or fell > 122880 below +0x2AC): vy = min(|n(n·v)|.y · 2458, 6144 · terrain) when |n(n·v)| >
  0x2000; airborne > 20, air pitch > 1000, forward·n < 0 -> fwd ·= (1 + forward·n).
- Sessions: `traffic_items.csv` / `kart_items_session.csv` (`tools/bizhawk/autodrive_plan.lua`: autopilot, L
  every 90 frames) exact for 5639 frames.

### Item objects (confirmed: exact replays of recorded shells)

- **Dump**: `kart_logger_lib.lua` KART_ITEMS_PATH logs every broadphase entry flagged 0x4000 (entries
  `*0x0217B598`, 28 bytes, count `*0x0217B590`; +0x0C position pointer = object + 0x50). Race progress table
  `*0x021755FC` (140 bytes per kart; place = +0x50 & 0xF) via KART_RACE_PATH.
- **Item type table** `*0x0217BC14` (168 bytes per type, runtime): +0 object size, +0x24 spawn, +0x28 update,
  +0x64/+0x6C base radii, +0x70 1.0, +0x74 full size, +0x78 grow step.
- **Generic item tick** (ITCM `0x01FFF960`): air counter +0x114 (to 6), growth (+737 to 1.0, then the type
  step to full size), update via +0x120 (`blx` at `0x01FFFA94`), item-item / map-object contacts, airborne
  flag +0x74 0x20000 when +0x114 >= 5, +0xE4 = position, age +0x11C += 1, owner shield +0x78 0x4000 cleared at
  age > 30 (dropped items, bit 0x2000: age > 4 and grounded).
- **Kart-vs-item** `sub_20F97E0`: |item +0x50 - kart contact centre +0x1D8| < kart radius + item +0xE0; owner
  excluded while shielded. Items as of the end of the previous frame (items update after karts).
- **Shell movement** `sub_20F2228` (cruise speed argument): see `kart/shell.rs`. Green shell `sub_20F60D0`:
  cruise 33997, 600-tick life then 0 bounces.
- **Red shell** state machine at +0x23C (`sub_2046B40`: +0x240 ticks, +0x24A state, +0x24C pending,
  +0x24E change), table `0x0216C628` of (enter, update): see `kart/red_shell.rs`. Route nodes: runtime array
  (40 bytes: next[3], prev[3], position pointer, radius, counts at +0x24/+0x26) from IPOI/IPAT.
- **Item slots** (528 bytes per kart at `0x023788E4`, `slots_items.bin`): +0x1EC input flags (0x244 = use,
  0x10 / 0x20 = held up / down), +0x1F0/+0x1F4 item-route cursor, +0x1FC kart. The **throw request** is
  slot + 0x58 (`a1` of `sub_20EFA60`): +0x0C slot, +0x10 kart, +0x14.. held objects, +0x20 count; refreshed
  from the kart by `sub_20EE528` (+0x38 up / +0x44 forward of the collision matrix, +0x50 kart +0x98,
  +0x5C velocity, +0x68 speed +0x2A4, +0x6C = +0x98 - +0x8C, +0x78 stats +0x08 x scale, +0x7C hop bounce,
  +0x80 forward·velocity > 0, +0x84.. size); spring +0x90 back, +0x9C behind, +0xA8 anchor, +0xE4 bob,
  +0xE8 lift 17203. Pickup `sub_20EE2E4` + `sub_20EF9A8`; single held item `sub_20EF65C`; release
  `sub_20EFA60` -> type +0x24 (green `sub_20F6150`, red `sub_20F5D6C`, banana `sub_20F5240`).
- **Throw** `sub_20F2B94` (forward: speed 20480 + |+0x6C|, aim +0x6C + 3.5 forward, start = kart +0x1B8 +
  10 x 0.8 x forward; red adds route 45 / ramp 91 / cursor from the slot). **Drop** `sub_20F3150` (stack
  args 0x4000, 0x3000, 1434 from the banana): speed max(492/4096 of forward movement, 1638) - |movement|,
  lift 1434 + share of the climb; below speed 0x3000 two `MATH_Rand32(246)` draws (race table +0x47C) spread it.
- **Banana**: flight `sub_20F2DF0` (gravity 737, x3973/4096 per tick), landing probe `sub_20F9334`, rest
  `sub_20F6A6C` (anchor = position - radius x normal, wobble = -|vy| x 410/4096), then `sub_20F68B0`
  keeps it at anchor + radius x normal; size spring `sub_20F9DC8` (+0x6C/+0x68/+0x100, 819 and 0.75).

