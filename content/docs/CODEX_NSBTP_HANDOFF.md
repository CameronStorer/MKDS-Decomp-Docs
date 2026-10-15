# Texture-pattern decoder handoff

`3_hand_port/vm_model/src/nitro_pattern.rs` parses BTP0/PAT0 animation dictionaries and M\0PT
tracks, targeting materials by name. Renderer integration now lives in
`3_hand_port/game/src/driver_animation.rs` (2026-10-08).

```rust
use vm_model::nitro_pattern::PatternAnimation;
let clips = PatternAnimation::parse_all(&bytes)?;
let selection = clips[0].sample("P_face", expression_frame);
```

The selection returns texture and optional palette names. A missing palette
means retain the material's existing palette (original index 255). The caller
must choose expression frames and implement looping when wanted; sampling holds
the last key and does not create blink timings.

All 85 local pattern files parse; 361 live SDK selections match, but only the
normal face was captured. `5_tools/bizhawk/codex_pattern/run.ps1` reproduces the
isolated capture; `compare_pattern_capture` compares captured RAM files.
`tests/data/pattern_runtime.csv` retains the one unique normal-face selection.

Use `nitro_playback::AnimationClock` for ordinary original-game playback timing.
The driver drive pose is explicitly controlled by steering, as documented in
`6_data/analysis/CODEX_ANIMATION_MAP.md`. The renderer loads the shared face pattern
from `KartModelMain/character/common`, preserves palette sentinel behavior,
and switches detailed-driver materials to frame 1 during spin/lose and frame 0
otherwise. This follows `sub_207B708` and `sub_2068A64`; live expression-transition
timing still needs capture. No invented blink timer is added.
