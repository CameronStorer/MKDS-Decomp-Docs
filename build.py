"""Build the public research site from reviewed documentation snapshots."""
from pathlib import Path
from collections import Counter
import csv
import html
import hashlib
import json
import re
import shutil
from urllib.parse import unquote, urlsplit
import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_site'


def slug(path):
    return path.replace('/', '--').removesuffix('.md').lower() + '.html'


def frame(title, body, active=''):
    versions = {name: hashlib.sha256((ROOT / 'assets' / name).read_bytes()).hexdigest()[:10]
                for name in ('style.css', 'theme.css', 'site.js')}
    manifest = json.loads((ROOT / 'content/manifest.json').read_text(encoding='utf-8'))
    links = []
    # Collapsible groups: the first two are open; a group also opens when it holds the current page.
    for group, open_default in (('Start here', True), ('Native build', True), ('Function maps', False),
                                ('Research', False), ('Hand-port archive', False)):
        entries = [p for p in manifest['documents'] if p['group'] == group]
        if not entries:
            continue
        is_open = open_default or any(active == p['path'] for p in entries)
        links.append(f'<details class="nav-group"{" open" if is_open else ""}><summary class="nav-label">{group}</summary>')
        for p in entries:
            selected = ' class="selected" aria-current="page"' if active == p['path'] else ''
            links.append(f'<a href="{slug(p["path"])}"{selected}>{html.escape(p["title"])}</a>')
        links.append('</details>')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · MKDS Research</title><meta name="description" content="A public research log of MKDS decompilation and its native Windows Rust build.">
<link rel="icon" type="image/png" href="assets/mkds-icon.png">
<link rel="stylesheet" href="assets/style.css?v={versions['style.css']}"><link rel="stylesheet" href="assets/theme.css?v={versions['theme.css']}"><script src="assets/site.js?v={versions['site.js']}" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header><a class="brand" href="index.html"><img class="brand-icon" src="assets/mkds-icon.png" width="48" height="48" alt=""><span class="brand-name">MK<span class="ds">DS</span><b>DECOMPILATION RESEARCH</b></span></a>
<nav aria-label="Primary"><a href="index.html">Overview</a><a href="functions.html">Function explorer</a>
<a href="https://github.com/CameronStorer/mkds-native-builder">Build it yourself ↗</a><a href="https://github.com/CameronStorer/mkds-decomp-docs">GitHub ↗</a></nav>
<button id="menu-toggle" aria-label="Toggle documentation navigation" aria-expanded="false">☰</button></header>
<div class="layout"><aside id="sidebar"><a class="explorer-link" href="functions.html">⌕ Explore functions</a>{''.join(links)}
<div class="snapshot">Documentation snapshot<br><strong>{html.escape(manifest['updated'])}</strong></div></aside>
<main id="main">{body}<footer>Independent research by Cameron Storer. Documentation of a work in progress.
<br>Not affiliated with Nintendo. MKDS and associated names belong to their respective owners.
<br>Title-screen checkerboard and Mario icon decoded from the original game. <a href="https://github.com/CameronStorer/mkds-decomp-docs/blob/main/assets/ATTRIBUTION.md">Visual asset sources</a>.</footer></main></div></body></html>'''


def rewrite_links(rendered, source, documents):
    def replace(m):
        href = html.unescape(m.group(1))
        text = m.group(2)
        parts = urlsplit(href)
        if parts.scheme in ('https', 'http', 'mailto') or href.startswith('#'):
            return m.group(0)
        target = (ROOT / 'content' / Path(source).parent / unquote(parts.path)).resolve()
        try:
            rel = target.relative_to((ROOT / 'content').resolve()).as_posix()
        except ValueError:
            rel = ''
        if rel in documents:
            fragment = ('#' + parts.fragment) if parts.fragment and not re.fullmatch(r'L\d+', parts.fragment) else ''
            return f'<a href="{slug(rel)}{fragment}">{text}</a>'
        if rel == 'docs/FUNCTION_TABLE.csv':
            return f'<a href="functions.html">{text}</a>'
        return f'<span class="local-reference" title="Reference to a file in the local research workspace">{text}</span>'
    return re.sub(r'<a href="([^"]+)">(.*?)</a>', replace, rendered, flags=re.S)


def build():
    OUT.mkdir(exist_ok=True)
    (OUT / 'assets').mkdir(exist_ok=True)
    for p in (ROOT / 'assets').iterdir():
        if p.is_file() and p.suffix != '.md':
            shutil.copyfile(p, OUT / 'assets' / p.name)
    shutil.copyfile(ROOT / 'content/docs/figure8_simulation.png', OUT / 'assets/figure8_simulation.png')
    manifest = json.loads((ROOT / 'content/manifest.json').read_text(encoding='utf-8'))
    documents = {p['path'] for p in manifest['documents']}
    for p in manifest['documents']:
        source = (ROOT / 'content' / p['path']).read_text(encoding='utf-8')
        # Reviewed prose must not introduce executable markup into the public site.
        if re.search(r'<\s*(script|iframe|object|embed|style)\b|\bon\w+\s*=', source, re.I):
            raise ValueError(f'Unreviewed active markup: {p["path"]}')
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'sane_lists'], extension_configs={'toc': {'toc_depth': '2-3'}})
        rendered = rewrite_links(md.convert(source), p['path'], documents)
        rendered = rendered.replace('src="figure8_simulation.png"', 'src="assets/figure8_simulation.png"')
        rendered = re.sub(r'<table>', '<div class="table-scroll"><table>', rendered)
        rendered = rendered.replace('</table>', '</table></div>')
        toc = f'<details class="page-toc"><summary>On this page</summary>{md.toc}</details>' if md.toc_tokens else ''
        body = f'<div class="eyebrow">{html.escape(p["group"])} / Research notes</div><div class="source-note">Source: <code>{html.escape(p["path"])}</code> · Updated {html.escape(p["modified"])}</div>{toc}<article class="prose">{rendered}</article>'
        (OUT / slug(p['path'])).write_text(frame(p['title'], body, p['path']), encoding='utf-8')
    with (ROOT / 'content/functions.csv').open(encoding='utf-8-sig', newline='') as f:
        functions = list(csv.DictReader(f))
    fields = ['name', 'segment', 'ea', 'size', 'status', 'area', 'meaning', 'callers', 'callees', 'our_code']
    data = [{key: row.get(key, '') for key in fields} for row in functions]
    (OUT / 'assets/functions.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    counts = Counter(p['status'] for p in functions)
    counts['annotated'] = counts['known'] + counts['described']
    cards = ''.join(f'<div class="stat"><strong>{counts[s]:,}</strong><span>{label}</span></div>' for s, label in [('annotated', 'Recorded meanings'), ('inferred', 'Inferred areas'), ('sdk', 'SDK classifications'), ('unknown', 'Still unknown')])
    overview = f'''<section class="title-screen" aria-label="MKDS research"><div class="title-screen-copy"><div class="eyebrow">MKDS / Native Windows build</div>
<h1>Understand the original.<br><span class="muted">Build it natively.</span></h1>
<p class="lead">An open research log: mapping the game's code, and turning a player's own ROM into a native Rust program with one command. No game data is published here.</p>
<div class="hero-actions"><a class="button" href="{slug('docs/NATIVE_BUILD_STATUS.md')}">Native build status →</a><a class="text-link" href="https://github.com/CameronStorer/mkds-native-builder">Build it yourself ↗</a><a class="text-link" href="functions.html">Explore {len(functions):,} functions →</a></div></div><img class="title-screen-icon" src="assets/mkds-icon.png" width="96" height="96" alt=""></section>
<section class="stats" aria-label="Function classification counts">{cards}</section>
<p class="caption">Function classifications from the current export inventory. These are documentation counts, not a percentage of game completion. Recorded meanings include {counts['known']:,} reviewed annotations and {counts['described']:,} unverified sweep descriptions. Inferred and SDK labels also require review.</p>
<section class="section"><div class="section-heading"><span class="eyebrow">Latest</span><h2>Block 1 complete: no interpreter in the shipped game</h2></div>
<p>From a user's own ROM, one command unpacks the game files, translates all 11,297 listed ARM9 functions and the ARM7 program into Rust, and compiles a native program. A full race to the results screen ran 1.67 billion ARM9 instructions with none interpreted; two fresh builds produced identical source.</p>
<a class="text-link" href="{slug('docs/NATIVE_BUILD_STATUS.md')}">Read the status and measurements →</a></section>
<section class="section"><div class="section-heading"><span class="eyebrow">The project</span><h2>From evidence to a native build</h2></div>
<div class="feature-grid"><a class="feature" href="{slug('docs/NATIVE_BUILD_STATUS.md')}"><span class="feature-number">01 / NATIVE BUILD</span><h3>Status and results</h3><p>What the one-command build does, what was measured, and the honest limits.</p><span>Read the status →</span></a>
<a class="feature" href="{slug('docs/GENERATOR_CONTRACT.md')}"><span class="feature-number">02 / HOW IT WORKS</span><h3>Machine code to Rust</h3><p>Function discovery, ARM/Thumb lifting, overlays and how coverage is reported.</p><span>Read about the generator →</span></a>
<a class="feature" href="{slug('docs/FUNCTION_MAP.md')}"><span class="feature-number">03 / CODE MAPPING</span><h3>What each routine means</h3><p>Address-based correlations, field layouts and connections to the Rust code.</p><span>Browse identified functions →</span></a>
<a class="feature" href="{slug('analysis/race_logic_map.md')}"><span class="feature-number">04 / ORIGINAL BEHAVIOR</span><h3>Follow the game logic</h3><p>Input paths, race state and structure offsets, checked against captures of the original.</p><span>Read the research →</span></a></div></section>
<section class="method"><div><span class="eyebrow">Verification matters</span><h2>A mapping is a claim.<br>A measurement is evidence.</h2></div><p>Every translated function is checked against a reference interpreter; builds are accepted only after a race is driven to the results screen with interpreter counters at zero. Inferred labels are kept distinct from verified behavior.</p></section>
<div class="notice">This site publishes reviewed documentation snapshots. Changes become live after documentation is synced and pushed to the repository; it does not read the developer's PC automatically.</div>'''
    (OUT / 'index.html').write_text(frame('Overview', overview), encoding='utf-8')
    explorer = '''<div class="eyebrow">Code inventory / Search & inspect</div><h1>Function explorer</h1>
<p class="lead">Find a routine by address, meaning, subsystem or Rust counterpart. Click a column heading to sort; click it again to reverse. Scroll to load 200 more rows.</p>
<div class="explorer-controls"><label class="search-label">Search functions<input id="function-search" type="search" placeholder="Try sub_2087B78, steering, animation…" autocomplete="off"></label>
<label>Status<select id="status-filter"><option value="">All statuses</option><option>known</option><option>described</option><option>inferred</option><option>sdk</option><option>unknown</option></select></label>
<label>Area<select id="area-filter"><option value="">All areas</option></select></label></div>
<p class="caption">Known = a reviewed annotation; described = an unverified sweep annotation; inferred = a candidate area; SDK = a library classification; unknown = unmapped. None alone proves frame-exact behavior.</p>
<div id="function-count" role="status" aria-live="polite">Loading function inventory…</div>
<div class="table-scroll"><table class="function-table"><thead><tr>
<th scope="col" aria-sort="none"><button class="column-sort" data-sort="name" data-label="function">Function <span class="sort-indicator" aria-hidden="true">↕</span></button></th>
<th scope="col" aria-sort="none"><button class="column-sort" data-sort="ea" data-label="address">Address / segment <span class="sort-indicator" aria-hidden="true">↕</span></button></th>
<th scope="col" aria-sort="none"><button class="column-sort" data-sort="status" data-label="status">Status <span class="sort-indicator" aria-hidden="true">↕</span></button></th>
<th scope="col" aria-sort="none"><button class="column-sort" data-sort="area" data-label="area">Area <span class="sort-indicator" aria-hidden="true">↕</span></button></th>
<th scope="col" aria-sort="none"><button class="column-sort" data-sort="meaning" data-label="meaning">Meaning <span class="sort-indicator" aria-hidden="true">↕</span></button></th>
</tr></thead><tbody id="function-rows"></tbody></table></div>
<div id="scroll-sentinel" class="load-more-panel"><p id="load-status">Loading function inventory…</p><button id="load-more" class="button" hidden>Load 200 more functions ↓</button></div>
<dialog id="function-detail"><button id="close-detail" class="dialog-close" aria-label="Close function detail">×</button><div id="detail-body"></div></dialog>
<noscript><p>The interactive explorer needs JavaScript. <a href="docs--function_map.html">Read the function map</a> instead.</p></noscript>'''
    (OUT / 'functions.html').write_text(frame('Function explorer', explorer), encoding='utf-8')
    (OUT / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Built {len(documents)} documentation pages and {len(functions):,} function records')


if __name__ == '__main__':
    build()
