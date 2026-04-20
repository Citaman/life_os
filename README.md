# Life OS — Anthonny

Personal Life OS with Notion as source of truth + GitHub Pages as visualization layer.

## Architecture

```
NOTION (3 DBs · édition + source de vérité)
  ├─ Plan d'exécution  (achievements · sous-achievements · tâches)
  ├─ Habitudes         (9 habitudes W-weekly · checkboxes L-D + formula Fait)
  └─ Backlog Vie       (registre intentions tous piliers · 6 horizons)
         │
         │  read-only API · token repo secret NOTION_TOKEN
         ▼
PYTHON 3.12 (GitHub Actions cron 5h UTC = 6-7h Paris)
  ├─ scripts/fetch_notion.py   paginate 3 DBs → raw.json
  ├─ scripts/transform.py       raw.json → snapshots.json (métriques W05-W16)
  └─ scripts/build_html.py      Jinja2 templates → 15 HTMLs
         │
         ▼
GITHUB PAGES  (branche gh-pages · auto-deploy)
  └─ 15 embeds HTML autonomes (D3 + Chart.js + Lucide)
         │
         │  iframe src="..."
         ▼
NOTION (iframes embed blocks à la place des CHART-TODO)
```

## Phases

| Phase | Status | Scope |
|---|---|---|
| **V1 Notion V8.4** | ✅ livré 2026-04-19 | Pages Notion natives avec callouts + vues DB + placeholders |
| **V2 Phase B** | 🚧 en cours | 15 chart embeds → iframe dans Notion, regen quotidien |
| **V3 React app** | 🔮 après V2 | Standalone React dashboard, même pipeline Python |

## Les 15 embeds V2

### Dashboard (4)
- `radar.html` — Radar 5 piliers actuel vs cible
- `sankey-week.html` — Sankey semaine 168h → 7 catégories
- `area-t2.html` — Area chart 5 piliers W05-W26 projection
- `stacked-w16.html` — Stacked column tâches W16 par pilier

### Piliers communs (× 3 templates × 5 piliers = 15 pages via paramétrage)
- `sankey-pilier-{slug}.html` — Sankey temps du pilier
- `heatmap-habits-{slug}.html` — Heatmap 4 sem × 7 j
- `tree-deps-{slug}.html` — Tree Achievement → Sous → Tâche

### Sections spécifiques par pilier (7)
- `line-poids-interieur.html`
- `tree-family-famille.html`
- `sankey-revenu-profi.html`
- `treemap-depenses-profi.html`
- `skill-tree-creation.html`
- `book-progression-spirituel.html`
- `line-predication-spirituel.html`

## Stack

- Python 3.12 · notion-client · jinja2 · python-dotenv
- D3 v7 · d3-sankey v0.12 · Chart.js v4.4 · Lucide icons (CDN)
- GitHub Actions · GitHub Pages

## Secrets requis

- `NOTION_TOKEN` — intégration Notion partagée sur les 3 DBs

## Commandes locales

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # puis renseigner NOTION_TOKEN

# Pipeline complet
python scripts/fetch_notion.py
python scripts/transform.py
python scripts/build_html.py

# Serveur local pour tester embeds
cd dist && python -m http.server 8000
# → http://localhost:8000/radar.html
```

## URL déployée

`https://citaman.github.io/life_os/` (après setup GitHub Pages sur la branche gh-pages)

## Licence

Personnel · non distribué.
