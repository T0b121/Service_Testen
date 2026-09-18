#!/usr/bin/env python3
"""Build public Graphify HTML from a committed snapshot; never read runtime state."""
import argparse
import ast
from collections import Counter
import html
import importlib.metadata
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

import yaml

REPO = Path(__file__).resolve().parents[2]
REMOTE = 'https://github.com/T0b121/Service_Testen'
TOOL_REV = '26b02b5e3430e4ab85dd7e72c7b98836d8e65c48'


def run(*args, cwd=None):
    subprocess.run(args, cwd=cwd, check=True)


def graphify(*args, cwd=None):
    run(sys.executable, '-m', 'graphify', *map(str, args), cwd=cwd)


def read_stacks(root):
    """Read declarations as data, without importing or executing stack hooks."""
    stacks = []
    for path in sorted((root / 'compose').glob('*/stack.py')):
        values = {}
        tree = ast.parse(path.read_text())
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {'REQUIRES', 'AUTH_GROUPS', 'SSO'}:
                        values[target.id] = ast.literal_eval(node.value)
        compose = yaml.safe_load(path.with_name('compose.yml').read_text())
        deps = values.get('REQUIRES', [])
        if path.parent.name != 'core' and 'core' not in deps:
            deps = ['core', *deps]  # model.discover adds the mandatory core dependency
        stacks.append(dict(name=path.parent.name, dependencies=deps,
            services=sorted(compose.get('services', {})),
            groups=values.get('AUTH_GROUPS', []),
            sso=values.get('SSO', {}).get('type', '—'),
            user_hook=any(isinstance(n, ast.FunctionDef) and n.name == 'sync_user' for n in tree.body)))
    return stacks


def page(title, body):
    return f'''<!doctype html>
<html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · Service_Testen</title>
<style>
:root{{color-scheme:dark;--ink:#edf2fa;--muted:#aebed3;--line:#2b3c53}}*{{box-sizing:border-box}}
body{{margin:0;background:#101923;color:var(--ink);font:16px/1.65 system-ui,sans-serif}}
main{{max-width:1140px;margin:auto;padding:44px 24px 70px}}a{{color:#8ed9cd;text-underline-offset:4px}}
nav{{display:flex;gap:22px;flex-wrap:wrap;margin:20px 0 40px}}h1{{font-size:clamp(2.2rem,6vw,4rem);line-height:1.1;margin:20px 0}}
h2{{margin-top:42px}}p{{max-width:85ch}}.eyebrow{{text-transform:uppercase;letter-spacing:.16em;color:#8ed9cd;font-size:12px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));gap:16px;margin:32px 0}}
.card{{padding:24px;background:#192637;border:1px solid var(--line);border-radius:12px}}.number{{display:block;font-size:36px}}
small,.muted{{color:var(--muted)}}.table{{overflow:auto}}table{{width:100%;border-collapse:collapse;text-align:left}}
th,td{{padding:12px;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:#8ed9cd}}code{{overflow-wrap:anywhere}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#192637;padding:24px;border-radius:12px}}
footer{{margin-top:50px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted)}}
</style><main><div class="eyebrow">Service_Testen · Repository-Analyse</div>
<nav><a href="index.html">Übersicht</a><a href="graph.html">Interaktiver Graph</a><a href="callflow.html">Aufrufbeziehungen</a><a href="tree.html">Dateibaum</a><a href="report.html">Graphify-Bericht</a></nav>
{body}<footer>Erstellt mit <a href="https://github.com/Graphify-Labs/graphify">Graphify-Labs/graphify</a>.
Statische Analyse; kein Nachweis für fehlerfreien Betrieb.</footer></main></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default='HEAD', help='Committed source revision')
    parser.add_argument('--output', default='docs/graphify')
    args = parser.parse_args()
    revision = subprocess.check_output(['git', 'rev-parse', '--verify', args.ref + '^{commit}'], cwd=REPO, text=True).strip()
    output = (REPO / args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='service-graphify-') as temporary:
        root = Path(temporary) / 'Service_Testen'
        root.mkdir()
        # Only committed application code and tests enter the corpus. Generated
        # reports, archived code, .env, secrets and runtime mounts are not read.
        archive = subprocess.check_output(['git', 'archive', revision, 'compose', 'tests'], cwd=REPO)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(root, filter='data')
        graphify('extract', root, '--code-only', '--no-cluster', '--max-workers', '2', cwd=REPO)
        generated = root / 'graphify-out'
        # The snapshot has no .git directory: set its verified source provenance.
        data = json.loads((generated / 'graph.json').read_text())
        data['built_at_commit'] = revision
        (generated / 'graph.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        graphify('cluster-only', root, '--no-label', cwd=REPO)
        graphify('export', 'callflow-html', '--graph', generated / 'graph.json', '--output', generated / 'callflow.html', '--lang', 'en', cwd=REPO)
        graphify('tree', '--graph', generated / 'graph.json', '--output', generated / 'tree.html', '--label', 'Service_Testen', cwd=REPO)
        for name in ('graph.json', 'graph.html', 'callflow.html', 'tree.html', 'GRAPH_REPORT.md'):
            shutil.copyfile(generated / name, output / name)
        stacks = read_stacks(root)
        data = json.loads((output / 'graph.json').read_text())
        nodes, edges = data['nodes'], data['links']
        counts = Counter(e.get('confidence', 'UNKNOWN') for e in edges)
        source_files = {n['source_file'] for n in nodes if n.get('source_file')}
        metadata = dict(source_commit=revision, graphify_version=importlib.metadata.version('graphifyy'),
            graphify_commit=TOOL_REV, scope='Committed compose/ and tests/; local AST extraction; no semantic LLM pass',
            nodes=len(nodes), edges=len(edges), source_files=len(source_files),
            communities=len({n.get('community') for n in nodes}), edge_confidence=dict(counts), stacks=stacks)
        (output / 'analysis.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
        degree = Counter()
        for edge in edges:
            degree[edge['source']] += 1
            degree[edge['target']] += 1
        by_id = {n['id']: n for n in nodes}
        hubs = ''.join(f'<li><code>{html.escape(by_id[k].get("label", k))}</code> – {v} Verbindungen</li>' for k,v in degree.most_common(10))
        rows = ''.join('<tr>' + ''.join(f'<td>{html.escape(str(v))}</td>' for v in (
            s['name'], ', '.join(s['dependencies']) or '—', ', '.join(s['services']),
            s['sso'], 'vorhanden' if s['user_hook'] else 'nicht vorhanden')) + '</tr>' for s in stacks)
        body = f'''<h1>Code verstehen.<br>Zusammenhänge erkunden.</h1>
<p>Analyse des aktiven Stack-Managers, seiner Integrationen und Tests. Quellstand:
<a href="{REMOTE}/commit/{revision}"><code>{revision[:12]}</code></a>.</p>
<div class="cards"><div class="card"><span class="number">{len(nodes)}</span>Knoten</div>
<div class="card"><span class="number">{len(edges)}</span>Verbindungen</div>
<div class="card"><span class="number">{metadata['communities']}</span>Graph-Gruppen</div>
<div class="card"><span class="number">{len(stacks)}</span>Stacks</div></div>
<h2>Drei Ansichten desselben Codes</h2><div class="cards">
<div class="card"><h3><a href="graph.html">Interaktiver Graph →</a></h3><p>Knoten suchen, Gruppen filtern und Verbindungen verfolgen.</p></div>
<div class="card"><h3><a href="callflow.html">Aufrufbeziehungen →</a></h3><p>Automatisch ermittelte Architekturabschnitte, Diagramme und Aufruftabellen.</p></div>
<div class="card"><h3><a href="tree.html">Dateibaum →</a></h3><p>Vom Verzeichnis bis zum Symbol navigieren.</p></div></div>
<h2>Was die Analyse zeigt</h2><p>Die am stärksten verbundenen Knoten sind gute Ausgangspunkte
für das Lesen des Codes. Viele Verbindungen bedeuten nicht automatisch ein Problem.</p><ol>{hubs}</ol>
<h2>Stack-Übersicht</h2><p>Zusätzlich aus <code>stack.py</code> und <code>compose.yml</code> gelesen,
ohne die Dienste oder ihre Hooks auszuführen. „Hook vorhanden“ besagt nicht, dass alle Nutzeraktionen unterstützt werden.
Die verpflichtende Abhängigkeit von <code>core</code> ist berücksichtigt.</p>
<div class="table"><table><thead><tr><th>Stack</th><th>Abhängigkeiten</th><th>Services</th><th>SSO-Typ</th><th>Nutzer-Hook</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Umfang und Grenzen</h2><ul>
<li>Graphify {metadata['graphify_version']}, festgelegter Tool-Commit <code>{TOOL_REV[:12]}</code>; lokale AST-Analyse von <code>compose/</code> und <code>tests/</code>.</li>
<li>{len(source_files)} Quelldateien sind im Graphen vertreten. Das ist keine vollständige Liste aller Repository-Dateien.</li>
<li>{counts.get('EXTRACTED', 0)} Verbindungen sind als EXTRACTED, {counts.get('INFERRED', 0)} als INFERRED markiert. Abgeleitete Beziehungen können unvollständig oder falsch sein.</li>
<li>Markdown, YAML und sonstige Konfiguration werden nicht semantisch durch ein LLM ausgewertet. Die Stack-Tabelle ist eine zusätzliche strukturierte Auswertung.</li>
<li><code>_alt/</code>, diese Analyseseiten sowie lokale Umgebungsdateien, Secrets und Laufzeitdaten sind ausgeschlossen.</li>
<li>Der Graph ist eine Momentaufnahme. Dynamische Python-Aufrufe, Docker-Verhalten, Authentik-Regeln und tatsächliche Zugriffsrechte werden damit nicht vollständig bewiesen.</li>
<li>Die Graphify-Ansichten laden JavaScript-Bibliotheken von öffentlichen CDNs; dafür ist Internetzugriff erforderlich.</li></ul>
<p>Offene Implementierungspunkte und Praxistests: <a href="{REMOTE}/issues/1">Issue #1</a>.
Weitere Prüfschritte: <a href="{REMOTE}/blob/{revision}/docs/validierung.md">Validierungsdokumentation</a>.</p>
<h2>Daten und Nachvollziehbarkeit</h2><p><a href="graph.json">Graph als JSON</a> ·
<a href="analysis.json">Metadaten und Stack-Inventar</a> · <a href="GRAPH_REPORT.md">Originalbericht als Markdown</a> ·
<a href="{REMOTE}/tree/main/tools/graphify">Build-Anleitung und Skript</a></p>'''
        (output / 'index.html').write_text(page('Graphify-Analyse', body))
        (output / 'report.html').write_text(page('Graphify-Bericht', '<h1>Graphify-Bericht</h1><p>Automatisch erzeugter Originalbericht. Begriffe wie „Surprising Connections“ sind Heuristiken des Tools.</p><pre>' + html.escape((output / 'GRAPH_REPORT.md').read_text()) + '</pre>'))
        (output / '.nojekyll').touch()
        print(f'Published artifact directory: {output}; source: {revision}')


if __name__ == '__main__':
    main()
