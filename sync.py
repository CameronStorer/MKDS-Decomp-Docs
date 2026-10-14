"""Copy an explicit list of research docs, not the project directory, for publication."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
DOCUMENTS = [
    ('PROGRESS.md', 'Shared progress', 'Progress'),
    ('docs/NEXT_GOALS.md', 'Current progress', 'Progress'),
    ('docs/ROADMAP.md', 'Roadmap', 'Progress'),
    ('docs/KART_PORT.md', 'Kart port findings', 'Progress'),
    ('docs/FUNCTION_MAP.md', 'Identified functions', 'Function maps'),
    ('docs/FUNCTION_TABLE.md', 'Inventory coverage', 'Function maps'),
    ('docs/function_notes.md', 'Function meanings', 'Function maps'),
    ('analysis/race_logic_map.md', 'Race logic', 'Research'),
    ('analysis/kart_struct.md', 'Kart structure', 'Research'),
    ('analysis/kart_runtime.md', 'Runtime correlations', 'Research'),
    ('analysis/kart_runtime_drift.md', 'Drift correlations', 'Research'),
    ('analysis/state_machines.md', 'State machines', 'Research'),
    ('analysis/vm_report.md', 'VM / dispatcher scan', 'Research'),
    ('analysis/CODEX_ANIMATION_MAP.md', 'Original animation logic', 'Animation'),
    ('analysis/CODEX_PARTICLE_MAP.md', 'Particles and fall contacts', 'Research'),
    ('docs/CODEX_RAINBOW_WORK_LOG.md', 'Rainbow Road movement fidelity', 'Research'),
    ('analysis/CODEX_NPC_MAP.md', 'NPC and traffic animation', 'Research'),
    ('docs/CODEX_NSBCA_HANDOFF.md', 'Joint-animation decoder', 'Animation'),
    ('docs/CODEX_NSBTP_HANDOFF.md', 'Face-pattern decoder', 'Animation'),
    ('docs/CODEX_ROM_BUILD_WORKFLOW.md', 'ROM build workflow', 'Project notes'),
    ('docs/RUST_PROJECT_COMPARISON.md', 'Rust project comparison', 'Project notes'),
    ('docs/NATIVE_BUILD_BASELINE_AND_CONTRACT.md', 'Native build baseline', 'Project notes'),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT.parent)
    args = parser.parse_args()
    source = args.source.resolve()
    target = ROOT / 'content'
    target.mkdir(exist_ok=True)
    manifest = {'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), 'documents': []}
    for rel, title, group in DOCUMENTS:
        path = source / rel
        text = path.read_text(encoding='utf-8')
        if not re.match(r'^#\s+\S', text.lstrip()):
            raise ValueError(f'{rel}: expected a Markdown title; refusing to sync')
        # Normalize machine-specific paths; never import credentials or arbitrary folders.
        text = re.sub(r'C:[/\\]Users[/\\]camer[/\\]Desktop[/\\]My_NDS_GAME', 'WORKSPACE', text, flags=re.I)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding='utf-8')
        manifest['documents'].append({'path': rel, 'title': title, 'group': group, 'modified': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime('%Y-%m-%d')})
    shutil.copyfile(source / 'docs/FUNCTION_TABLE.csv', target / 'functions.csv')
    shutil.copyfile(source / 'docs/figure8_simulation.png', target / 'docs/figure8_simulation.png')
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Synced {len(DOCUMENTS)} reviewed documentation files and function inventory')


if __name__ == '__main__':
    main()
