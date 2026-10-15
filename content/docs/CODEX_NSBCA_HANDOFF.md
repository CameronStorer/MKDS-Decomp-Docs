# NSBCA decoder handoff to Claude

Implemented and integrated 2026-10-08. The running game now samples detailed
driver joint poses before SBC hierarchy and skinning. The decoder remains
engine-independent; `nitro_driver.rs` controls presentation and
`3_hand_port/game/src/driver_animation.rs` updates the renderer.

## Files

- `3_hand_port/vm_model/src/nitro_anim.rs`: parser, fixed-point channels, local-pose sampling.
- `3_hand_port/vm_model/src/lib.rs`: one module export (`pub mod nitro_anim;`).
- `3_hand_port/vm_model/tests/nitro_anim.rs`: local asset corpus and truncation checks.
- `3_hand_port/vm_model/examples/animation_info.rs`: inspect animations and sampled matrices.
- `3_hand_port/vm_model/examples/compare_animation_capture.rs`: compare live SDK captures.
- `5_tools/bizhawk/codex_anim/`: isolated capture runner and fixture generator.
- `3_hand_port/vm_model/tests/data/animation_runtime.csv`: original SDK regression evidence.

## API

```rust
use vm_model::nitro_anim::{JointAnimation, NodePose, ONE};

let animations = JointAnimation::parse_all(nsbca_bytes)?;
let animation = &animations[0];
// rest_pose contains the NSBMD's LOCAL node translation, rotation and scale.
// Do not pass world matrices or inverse-bind transforms.
let pose = animation.sample_pose(frame * ONE, &rest_pose);
let local_matrix = pose[node_index].matrix();
```

`num_frames`, `name`, `flags`, and `tracks` are public. Each track exposes its
`node_index`; it is not necessarily the track's array index. `sample_node`
supports sampling one node without allocating a pose vector.

Coordinates remain in the model's original units. `NodePose` uses signed fx12
components and a column-vector rotation. `matrix()` returns `[[f32; 4]; 3]`,
with translation in column 3, matching `nitro.rs`'s private `Mat` convention.
It composes T * R * S. It also retains `inverse_scale`, the animation's stored
reciprocal scale, separately for SBC scale compensation.

Unmapped nodes retain their supplied rest pose. Channel flags distinguish
identity from model defaults; do not substitute identity for every missing
channel. A track with the overall identity bit set produces identity TRS.

Sampling takes a frame number in fx12, not seconds. Clamp matches the SDK's
range `[0, num_frames * 4096 - 1]`. The caller owns playback speed and looping:
wrap the frame by `num_frames * ONE` when appropriate. Animation flag bit 0
enables fractional sampling; bit 1 permits final-to-first interpolation.
Integer samples on step-two/step-four tracks still interpolate.

## Renderer integration

`Model::local_poses` retains local rest TRS and inverse scale;
`Model::parse_all_with_poses` applies sampled nodes before the existing SBC walk.
The game loads four clips once per detailed driver, updates positions/normals
on changed poses, and leaves topology, UVs and outer model transforms intact.
Claude's pivot correction already makes detailed drivers face forward; do not
reintroduce the obsolete 180-degree correction from the earlier handoff.

Drive frames follow steering (one frame per tick, two while drifting), then
recenter. Damage selects spin immediately. Ordinary eight-racer finishes select
win for places 1..3 and lose for 7..8; other places retain drive. Non-immediate
transitions use the original 410/fx12 blend increment. Face patterns from
`KartModelMain/character/common/P_faceanim.nsbtp` use normal frame 0 and closed
frame 1 for spin/lose. Missing detailed models retain the existing fallback.

Remaining: victory idle alternation (`sub_207B354`), complete team/battle/time
trial result logic, one-shot return transitions, special mode-6 steering guard,
and runtime captures for crossfade and expression transitions. Ghosts use a
centered drive pose because the current recording does not expose steering.

## Evidence and limits

- All 115 NSBCA files in `6_data/gamefile_assets/unpacked` parsed and sampled at every
  integer frame and half frame: 19,070 complete poses, without errors.
- Mario's 29-frame drive animation has 7 tracks and produces changing poses.
- Every truncated prefix of Mario's drive file is rejected.
- Focused tests cover pivot orientation, signed packed rotations, reduced-rate
  tails, translation midpoint rounding, normalized rotation interpolation,
  sparse node indices, and identity versus model-default channels.
- The existing core simulation suite passes alongside these tests.
- BizHawk now verifies **every integer frame of Mario's drive clip**: 1,687
  joint samples, 16,629 animated components, zero mismatches. The capture's RAM
  animation bytes hash-identically to the extracted `P_MR_drive.nsbca`.
- The 203 unique joint/frame combinations (7 joints x 29 frames) are retained
  as a regression fixture, without embedding the animation asset. The test
  reads the local extracted asset and requires exact integer equality.
- Renderer corpus: 48 driver clips skinned at every integer frame; finite
  vertices/normals and unchanged topology/UVs/materials. Explicit rest poses
  exactly reproduce the static parser. Mario drive pulls arms inward.
- The release game builds. Engine screenshots before/after at the Figure-8
  start show Mario's arms moved inward into the driving pose. Spin and result
  presentation still need equivalent visual/runtime checks.

The runtime comparison covers the drive clip's animated rotation and translation
channels. Identity channels have unwritten fields in SDK output; those fields
are excluded. This capture has no model-default channels or animated scales.
Fractional sampling, reduced-rate tracks, other clips, reciprocal scale, and
model-default channels still need runtime captures. The SDK comparison verifies
local sampler output; corpus tests and the engine screenshot separately verify
that animated poses reach the rendered mesh.
Unsupported byte orders, file versions, step-eight tracks, unknown animation
flags, and nonzero reserved curve bits return an explicit error.

Primary references: [NSBMD/NSBCA format notes](https://github.com/scurest/nsbmd_docs/blob/master/nsbmd_docs.txt)
and [NitroSystem animation assembly](https://github.com/pret/pokediamond/blob/master/arm9/asm/NNS_G3D_nsbca.s).
The notes contain speculative sampling details; this implementation uses the
SDK routines and this ROM's exports to resolve them. Local routine references:

- `sub_2013C78`: pivot/packed rotation decoding.
- `sub_2013E18`, `sub_2014164`: fractional/integer rotation sampling.
- `sub_201456C`, `sub_2014724`: fractional/integer scale pair sampling.
- `sub_2014954`, `sub_2014AD0`: fractional/integer translation sampling.
- `sub_2014C5C`: channel flags and dispatch.

## Commands (from the project root)

```powershell
cargo test --manifest-path 3_hand_port/vm_model/Cargo.toml
cargo run --manifest-path 3_hand_port/vm_model/Cargo.toml --example animation_info -- 6_data/gamefile_assets/unpacked/data/KartModelSub/character/mario/P_MR_drive.nsbca 0
& 5_tools/bizhawk/codex_anim/run.ps1
cargo run --manifest-path 3_hand_port/vm_model/Cargo.toml --example compare_animation_capture -- 5_tools/bizhawk/codex_anim
python 5_tools/bizhawk/codex_anim/make_fixture.py
```

Codex used `--target-dir "$env:TEMP/codex-mkds-nsbca-target"` to avoid competing
with Claude's existing build outputs.
