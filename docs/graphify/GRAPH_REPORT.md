# Graph Report - Service_Testen  (2026-09-18)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 295 nodes · 728 edges · 30 communities (8 shown, 22 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 30 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9ee995ad`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 11
- Community 13
- Community 14
- Community 15

## God Nodes (most connected - your core abstractions)
1. `ManagerError` - 74 edges
2. `run()` - 23 edges
3. `read_env()` - 16 edges
4. `private_write()` - 16 edges
5. `Authentik` - 15 edges
6. `parse()` - 14 edges
7. `Context` - 14 edges
8. `export_archive()` - 13 edges
9. `Configuration` - 13 edges
10. `Docker` - 13 edges

## Surprising Connections (you probably didn't know these)
- `main()` --uses--> `Configuration`  [INFERRED]
  tests/validate_compose.py → compose/_manager/config.py
- `Archives` --uses--> `ManagerError`  [INFERRED]
  tests/test_backup.py → compose/_manager/model.py
- `Schedules` --uses--> `ManagerError`  [INFERRED]
  tests/test_backup.py → compose/_manager/model.py
- `Templates` --uses--> `ManagerError`  [INFERRED]
  tests/test_config.py → compose/_manager/model.py
- `Exposure` --uses--> `ManagerError`  [INFERRED]
  tests/test_docker.py → compose/_manager/model.py

## Import Cycles
- None detected.

## Communities (30 total, 22 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (38): base64, bootstrap_files(), finish_bootstrap(), Authentik API über den lokalen Servercontainer, ohne öffentliche Bootstrap-…, infrastructure_route(), labels(), routes(), validate_exposure() (+30 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (38): argparse, before_start(), main(), Aufruf ohne Argumente startet das Terminalmenü., export_archive(), import_archive(), inspect_archive(), inventory() (+30 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (27): aiohttp, Any, asyncio, allowed_host(), download_model(), download_status(), Server-side, allow-listed model downloads for the ComfyUI web interface., Expose only model sources declared by ComfyUI's bundled templates. (+19 more)

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (9): Authentik, Configuration, secret_path(), Context, ManagerError, Eine verständliche, ohne Secret-Inhalte auszugebende Fehlermeldung., State, Exception (+1 more)

### Community 4 - "Community 4"
Cohesion: 0.12
Nodes (16): encode(), Entry, lines(), parse(), Vorlagen sind Daten; weder Shellbefehle noch Variablenwerte werden ausgeführt., Logische ENV-Zeilen, einschließlich zitierter mehrzeiliger Werte., read_env(), unquote() (+8 more)

### Community 5 - "Community 5"
Cohesion: 0.17
Nodes (8): Docker, discover(), order(), visit(), Path, Stack, Dependencies, main()

### Community 6 - "Community 6"
Cohesion: 0.25
Nodes (18): addMissingModelActions(), currentGraphSources(), getWorkflowSources(), humanSize(), leafText(), makeElement(), nearestDownload(), openInstaller() (+10 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (18): BASE_CURRENCY, DATABASE_URL, DEFAULT_LANG, DEFAULT_TIMEZONE, DEFAULT_URI, INSTANCE_NAME, read_secret(), SAML_BEHIND_PROXY (+10 more)

## Knowledge Gaps
- **21 isolated node(s):** `install-sd-turbo-cpu.sh script`, `bootstrap-worker.sh script`, `apply-security-settings.sh script`, `onlyoffice-entrypoint.sh script`, `JWT_SECRET` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 90 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ManagerError` connect `Community 3` to `Community 0`, `Community 1`, `Community 4`, `Community 5`, `Community 8`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Why does `run()` connect `Community 1` to `Community 0`, `Community 3`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `read_env()` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `ManagerError` (e.g. with `Authentik` and `Configuration`) actually correct?**
  _`ManagerError` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `install-sd-turbo-cpu.sh script`, `bootstrap-worker.sh script`, `apply-security-settings.sh script` to the rest of the system?**
  _21 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07706766917293233 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.1027450980392157 - nodes in this community are weakly interconnected._