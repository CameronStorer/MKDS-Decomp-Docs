# Lane 3 runtime interface (codex-runtime, 2026-10-14)

## Shared rendering API (agent-runtime, 2026-10-15)

`Session::render_snapshot(&mut self) -> recomp::machine::RenderSnapshot` synchronizes
GX and copies the rendering inputs: IO, palette, OAM, nine VRAM banks, completed
polygons and viewport. The owned snapshot is `Send`; it retains no live machine
references. `Machine::render_snapshot` exposes the same operation for core callers.

`RenderSnapshot::screens(&self) -> Vec<u32>` returns 256x384 pixels, physical top
screen first, packed 0x00RRGGBB. `screens_profiled()` returns `RenderedScreens` with
the same `pixels`, total `took`, and three `parts` durations (3D, engine A, engine B).
Both entry points borrow snapshot memory while rendering: no emulated bus or
second copy of the snapshot is needed. `Session::screens()` delegates to this API.
`Machine::render_frame3d()` and snapshots share the same 3D helper; live 2D bus
rendering and snapshots share the same borrowed-memory implementation.

The native host transports snapshots to its existing worker and presents the
returned pixels. Worker scheduling, pacing, input, audio and statistics remain
host responsibilities. Runtime parity checks now test snapshot/transport
consistency; regression fixtures independently record the pre-refactor pixels.

Synthetic regression fixtures cover VRAM mappings, palette and sprite
data, extended backgrounds, 3D composition and screen swapping. They also verify
that overwriting live GPU state cannot change a captured frame and that a snapshot
renders on another thread. Private comparison material is under
`8_scratch/agent_runtime_render/`; it is not a distributable game asset.

## Block 1 loose-assets entry (agent-runtime, T119)

```rust
mkds_native::run_from_assets(
    assets_path, expected_rom_sha256, expected_assets_sha256,
    lifted::LIFTED, lifted::SEGMENT_SIGS, options,
)?;
```

Both expected hashes must be embedded in generation provenance. Do not obtain the
expected asset hash from the same untrusted input manifest. The entry opens only
`assets/manifest.json` and its loose files, validates format 1, sizes, SHA-256,
consecutive FAT IDs, directory count, paths and address bounds, and recomputes the
aggregate asset hash. It prints the manifest-byte SHA-256 for audit. The launcher
can additionally compare that exact manifest hash against its bundle provenance.

The virtual card is an in-memory address map populated from those verified bytes.
Original header, FNT, FAT, code, overlays and file offsets are preserved; directory
IDs are encoded by the unchanged FNT. Unallocated bytes are 0xff. No source `.nds`
is opened or written. The software card transfer protocol remains modelled in
block 1. This preserves file-by-ID and file-by-name behavior without requiring a
new FAT allocation scheme. Assets are loaded once, so later on-disk changes do not
alter the verified session. Editing assets requires a new generation/provenance
workflow; modified-ROM support remains out of scope.

Standalone diagnostic syntax:
`mkds_runtime_probe --assets DIR ROM_SHA256 ASSETS_SHA256 --headless --instructions N`.
It explicitly uses the interpreter oracle, so it does not prove zero-interpreter
acceptance. `run_from_assets` currently uses the existing ARM9 table and interpreted
ARM7; the production ARM7 hook must follow Agent 2's differential-tested `LIFTED7`
handoff. Do not claim Block 1 complete on the strength of asset loading alone.

Verification: synthetic rip/load tests cover card reads, unchanged FNT/FAT,
wrong provenance, changed data, invalid IDs, paths, sizes and format versions.
The opt-in `real_rom_rip_card_and_boot_parity` test passed on the local AMCE0 ROM:
all 610 FAT byte ranges and the decompressed ARM9 match; ARM9 and ARM7 register
arrays match at each of 100 successive 1,000-instruction ARM9 boot slices. This
does not certify a finished race or zero interpreted execution.

`--input-log` now observes `Machine::set_input` directly: normal input, scripted
input and IRQ-wait input changes share one log with the applied hardware-cycle
timestamp. Duplicate held snapshots are omitted. Write errors fail the run.
The prior log missed changes applied inside IRQ waits; this fixes the diagnostic
coverage, not the still-unreproduced menu double-move itself.

## Existing ROM-based diagnostic interface

Agent 1 owns builder integration and Agent 2 owns generation. Codex owns the native
host crate `2_native_game/native` (`mkds_native`) and `recomp::boot::session`.

Generated game crates should depend on `mkds_native` by checkout-relative or
resolved explicit path and call:

```rust
mkds_native::run_with_signatures(
    &rom_bytes, &whole_decompressed_arm9,
    lifted::LIFTED, lifted::SEGMENT_SIGS, options,
)?;
```

`options` is `mkds_native::Options::default()` for an interactive window; call
`Options::from_args(...)` to parse arguments after the explicit ROM path.
The host does not load a fallback ROM, generate code, or select metadata.
The generated main/launcher must validate that its ROM matches generation provenance.
The whole ARM9 image includes autoload source data; do not load only split sections.

`Options` supports headless diagnostic runs, an optional instruction limit, an
optional frame limit, muted audio, and an output directory for final screen captures.
CLI flags: `--headless --instructions N`, `--frames N`, `--mute`, `--capture DIR`,
and `--input-script CSV`. Input CSV columns are `frame,buttons,x,y`, strictly
increasing hardware frame numbers, active-high DS button masks (decimal or hex),
and optional touch coordinates. Blank x/y releases the pen. Snapshots remain held
until the next row. A supplied script replaces live input, enabling reproducible
menu/race checks. Escape and window close still stop an interactive run.
Live keys: Z=A, X=B, Enter=Start, Right Shift=Select, arrows=D-pad, S=R, A=L,
C=X, V=Y. Left mouse button on the bottom screen supplies calibrated touch.
The checked-in `2_native_game/native/diagnostics/confirm_menu.csv` is a generic menu
bring-up script. It has reached a race in current AMCE0 diagnostics; it does not
steer or finish a race and does not prove course compatibility.
Capture output includes private local VRAM/palette/register snapshots as well as
top/bottom PPMs; do not package those ROM-derived assets for distribution.
`render_snapshot DIR` re-renders 2D evidence without repeating boot (3D geometry is
not included in this diagnostic snapshot).
`--gx-trace FILE` records the complete GX stream to a new local file. Reusing an
existing file is refused. `replay_gx FILE MATCHING_CAPTURE_DIR` reproduces both
screens from exactly those writes and the matching VRAM snapshot. The trace is
`GXTR0001` followed by little-endian offset/value u32 pairs and one width byte.
It can contain ROM-derived geometry and remains private diagnostic data.
Headless runs report their counts; they do not certify playable completion.
Errors propagate to the generated main, which must print the error and exit nonzero.

The host uses `Session` for fine-grained ARM9/ARM7 interleaving, rendering both
physical screens, input, and draining stereo audio. Lifted and interpreted ARM9
instructions are counted separately. ARM7 remains interpreted as in existing boot.
Interactive IRQ waits poll native events at most every 8 ms of wall time. Close
and Escape leave normally; display failures propagate as errors. Focus loss
releases input even while the guest waits. Headless execution has no UI callback.
These are existing block-budget charges rather than cycle-accurate counts: a
lifted block can finish after using up the remaining slice budget.

Overlay signatures are verified against guest RAM at hardware-frame boundaries.
Writes by ARM9, ARM7, and DMA to the watched code window invalidate the prior
overlay selection before the next dispatch. Partial or unknown code remains
interpreted. The report includes separate `overlay_instructions` budget charges.
The original `run(rom, image, table, options)` remains compatible and supplies no
signatures, so its overlays remain interpreted. New generated games must use
`run_with_signatures`; do not use `Dispatcher::new(all_overlays)`.

Standalone `mkds_runtime_probe` deliberately passes an empty lift table to test the
runtime without compiling old checked-in generated crates. It is a diagnostic tool,
not the generated game executable. Generated builds must pass their real lift table.
