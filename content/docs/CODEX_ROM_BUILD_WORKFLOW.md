# User-supplied ROM build workflow

The intended release contains our Rust implementation and tools. Users supply
their own ROM locally. This describes engineering boundaries, not legal clearance.

## Existing foundation

### Recompiler status (2026-10-10)

`rom_builder/` is currently a ROM validator, TUI, and staging launcher; its `--build` action still
compiles the frozen `game/` reference port. It is not yet the promised ROM-to-game recompiler.
`recomp/build.rs` is a separate spike that lifts a capped ARM subset from metadata-selected ARM9
main/autoload/overlay images and is not yet linked into a runnable game. User ROM loading exposes decompressed ARM9
main/autoload sections and expanded ARM9 overlays through
`mkds_builder::extract::{arm9_sections, arm9_overlays}`, plus zero-copy NitroFS access through
`rom::NitroFs`. The build script consumes section/overlay images by exact segment identity and
checks boundaries against each selected guest image. The remaining integration is to compile
generated Rust into the game runtime and boot through replacement DS services. Current spike
validation still accepts AMCE revision 0 only; other regions/revisions need their own address
metadata before they can be safely lifted.

### Rust builder (rom_builder/, 2026-10-10)

`rom_builder/` (crate `mkds_builder`) is the Rust port of `tools/rom_builder.py` with a ratatui TUI.
No Python needed. Run `cargo run --release --manifest-path rom_builder/Cargo.toml` for the TUI, or
`mkds_builder ROM --inspect|--build|--run [--out DIR] [--source CHECKOUT] [--allow-unverified] [--offline] [--course NAME] [--json]`.
The bundle contains the game exe, `manifest.json` and `play.exe` (a copy of the builder that re-checks the ROM hash, then launches).
Tests: `cargo test --manifest-path rom_builder/Cargo.toml`.

### First local builder (2026-10-10)

Python 3.11+ and Rust/Cargo are required. Start the plain terminal menu:

```powershell
python tools/rom_builder.py
```

Or use explicit commands from the repository root:

```powershell
python tools/rom_builder.py "C:\path\owned-copy.nds" --inspect
python tools/rom_builder.py "C:\path\owned-copy.nds" --build --out "C:\path\My MKDS Build"
python "C:\path\My MKDS Build\play.py"
```

`--run` builds and launches; `--course cross_course` skips the menu.
`--offline` tells Cargo to use only dependencies already available locally.
`--target-dir "C:\path\My Cargo Cache"` isolates the compiler's artifacts from
other development builds or running executables. A fresh cache needs a full
dependency compile; the tool continues to use Cargo's reported executable path.
The output directory must be empty, and defaults to `~/MKDS Builds/<ROM hash prefix>`.
The launcher supports moving the output bundle; it retains an absolute reference to
the user's ROM. If that ROM is moved or changed, generate a fresh bundle.

The tool checks header ranges, directory traversal, file allocation ranges and
required assets, then records SHA-256, game code, revision, ARM9 fingerprint,
lockfile fingerprint and executable fingerprint in `manifest.json`. It accepts
the locally studied AMCE revision-0 reference dump by full SHA-256. Other AMCE
revision-0 files need `--allow-unverified` (or the menu's experimental choice);
that permits experimentation with modified courses without claiming parity.
Other game codes/revisions are rejected. Validation is structural and does not
prove all game archives are intact or all modifications compatible.

Builds use `cargo build --release --locked` and Cargo's reported executable path.
The bundle contains the native executable, `play.py` and a provenance manifest.
The ROM is read externally at runtime; it is neither copied nor extracted.
The launcher rechecks its ROM hash before starting and runs with the bundle as
its working directory. This is a development builder for our current Rust port;
it does not generate arbitrary game source from an NDS file. Existing ROM-derived
tables and incomplete gameplay still need the separate fidelity/release work
described below. The tool builds the current checkout, including local changes.

Builder checks: `python -m unittest discover -s tools/tests -p test_rom_builder.py -v`.

`vm_model/src/assets.rs` already reads the NDS filesystem, LZ10-compressed CARC
archives and NARC entries directly. `game/src/main.rs` accepts `--rom PATH` or
`MKDS_ROM`; extracted assets do not need to be distributed for that path.

`tools/nds_extract.py ROM --out DIRECTORY` produces decompressed code sections,
overlay manifests and IDA load plans. It requires ndspy. `asset_organizer.py`
organizes an existing dump; it does not itself perform ROM extraction.

Example development run, from the repository root:

```powershell
cargo run --release --manifest-path game/Cargo.toml -- --rom "C:\path\owned-copy.nds"
```

This is a native Rust executable reading original data. It does not currently
automatically recompile all decompiled C. Generating C with IDA is a research
workflow, not a necessary runtime prerequisite or a portable end-user build step.

## Proposed reproducible release path

1. Accept a ROM path and compute game code, revision, size and SHA-256 locally.
   Report explicitly whether that revision is supported; do not silently apply
   AMCE address maps to another revision.
2. Read assets directly, or extract to a user-owned cache keyed by ROM hash.
   Include cache format/version and source provenance in a generated manifest.
3. Read tables from supported binary locations where practical, rather than
   relying on committed generated asset dumps. Document each table's source and
   how it is interpreted. Review hard-coded ROM-derived tables separately.
4. Build our implementation using the checked-in Cargo lockfile, or distribute
   a reviewed native binary with a ROM picker. End users should not need IDA,
   BizHawk or a C decompiler merely to play the port.
5. Verify the result from an empty cache and an explicit ROM path. Ensure no
   developer-local asset directories, save states or absolute paths are required.

Before publishing, audit the package for ROMs, extracted assets/code binaries,
exported Nintendo C/assembly, IDA databases, emulator save states, audio exports
and generated build artifacts containing game data. A ROM requirement alone
does not determine the copyright status of other included material. Obtain
appropriate legal review for the actual package and intended distribution.

## Documentation target

For each original routine retain segment + address, meaningful name, callers,
inputs/outputs and structure fields, state transitions, arithmetic details,
confidence, Rust counterpart and verification evidence. Unknown routines remain
explicitly unknown. Separate game logic from SDK, hardware, networking and debug
code so that documenting everything does not imply porting every routine.

Claude's current semantic catalog is `docs/FUNCTION_MAP.md`; the animation
supplement is `analysis/CODEX_ANIMATION_MAP.md`. The former is generated from
source comments and `docs/function_notes.md` and currently targets plan0. A
future catalog migration should reconcile segment identities against plan2.

### Native build flow (2026-10-14, current implementation)
`mkds_builder <your.nds> --build --out <empty dir>` generates Rust from your ROM (`mkds_gen`), links it to the native
host (`recomp/native`), compiles it with locked dependencies and stages `game`, `play`, `manifest.json`,
`generation.json` and `coverage.csv`. `--run` also launches it; extra runtime options go after `play`
(`--headless --instructions N`, `--frames N`, `--mute`, `--capture DIR`, `--input-script CSV`). Incomplete coverage
fails the build unless `--allow-incomplete`; `--keep-generated` keeps the generated source. The frozen hand-written port is
only built by `--reference-port`. First builds take ~15 minutes.

The generated full-table runtime has completed an input-driven three-lap race and reached first-place results in a headless
acceptance run. That verifies the generated game code and runtime path, but does not establish smooth windowed playback.
The latest packaged windowed measurement recorded about 20 fps in menus and 31 fps in a race at roughly half real-time,
with severe audio underruns. A fresh packaged build using the latest core changes and improved render scheduling still needs
acceptance. See the [native build baseline and contract](NATIVE_BUILD_BASELINE_AND_CONTRACT.md) for test evidence and open limits.
