# MKDS decompilation research

Public documentation of Cameron Storer's Mario Kart DS research and native
Windows Rust port. Includes progress notes, function meanings, runtime
correlations, structure maps, state machines and animation research.

Site: [MKDS research documentation](https://docs.cameronstorer.com/mkds-decomp-docs/)

The custom domain and HTTPS certificate are configured. HTTPS serving is
verified, and GitHub Pages redirects HTTP requests to HTTPS.

The interactive function explorer is built from the research inventory. Known,
inferred, SDK and unknown classifications are distinct. Counts describe mapping
coverage, not game completion or universal runtime verification.

## Explore the research

- [Current progress](content/docs/NEXT_GOALS.md) and [roadmap](content/docs/ROADMAP.md).
- [Function inventory coverage](content/docs/FUNCTION_TABLE.md),
  [identified functions](content/docs/FUNCTION_MAP.md), and
  [function meanings](content/docs/function_notes.md).
- [Kart port findings](content/docs/KART_PORT.md),
  [race logic](content/analysis/race_logic_map.md), and
  [runtime correlations](content/analysis/kart_runtime.md).
- [Original animation logic](content/analysis/CODEX_ANIMATION_MAP.md),
  [joint-animation decoder](content/docs/CODEX_NSBCA_HANDOFF.md), and
  [face-pattern decoder](content/docs/CODEX_NSBTP_HANDOFF.md).

The website adds a searchable function explorer with status and subsystem
filters, sortable column headings, and scrolling that reveals 200 rows at a
time. A Load more button also supports keyboard navigation. Sorting and filters
apply to the complete inventory. These documents are snapshots of the active research workspace;
individual findings record their evidence and remaining limitations.

## Build locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe build.py
python -m http.server 8000 --directory _site
```

Open http://localhost:8000. The builder outputs static HTML, CSS, JavaScript and
function metadata. GitHub Actions builds and publishes every push to `main`.

After building, run `node tests/explorer.cjs` to check sorting, filters, incremental
loading, and function details against the generated inventory.

## Update from the game research workspace

When function meanings change, run these commands from the game workspace:

```powershell
python tools/function_map.py
python tools/function_table.py
```

Then, from this documentation repository, publish the latest snapshot:

```powershell
.\publish.ps1 -SourceDirectory "C:\path\to\My_NDS_GAME"
```

Install `requirements.txt` first using the local build instructions above.
`publish.ps1` synchronizes the selected documents, builds the site, commits the
content changes, and pushes them to GitHub. GitHub Actions deploys the new site.
It requires Python, Git, and permission to push to this repository.

To review the snapshot before publishing, run:

```powershell
python sync.py --source "C:\path\to\My_NDS_GAME"
git diff -- content
```

`sync.py` copies only explicitly listed documentation, the function metadata
CSV, and the selected research figure. Review additions to its allowlist before
including more workspace files.

Local workspace changes are not automatically public. They become live after
syncing and pushing this repository. Snapshots retain source-file names and
update dates; references to unpublished local code are shown as local references.

## Repository scope

This repository contains research documentation, site tooling, and two small
[theme graphics decoded from the game](assets/ATTRIBUTION.md). ROMs, raw game
asset archives, extracted code binaries, decompiled source exports, save states and IDA
databases are not included. No copyright license for third-party material is
implied. This independent project is not affiliated with Nintendo.
