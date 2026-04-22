# Life OS — Anthonny

Personal Life OS with Notion as source of truth + GitHub Pages as visualization layer.

## Architecture

```
NOTION (6 DBs · édition + source de vérité)
  ├─ Plan d'exécution  (achievements · sous-achievements · tâches)
  ├─ Habitudes         (9 habitudes W-weekly · checkboxes L-D + formula Fait)
  └─ Backlog Vie       (registre intentions tous piliers · 6 horizons)
  ├─ Finance mensuelle (synthèse mensuelle du foyer)
  ├─ Lignes budget mensuel (postes détaillés revenus / dépenses / allègements)
  └─ Journal Pro & Financier (décisions · suivis · blocages)
         │
         │  read-only API · token repo secret NOTION_TOKEN
         ▼
PYTHON 3.12 (GitHub Actions cron horaire + dispatch manuel)
  ├─ scripts/fetch_notion.py   paginate core DBs + finance DBs → raw.json
  ├─ scripts/transform.py      raw.json → snapshots.json (métriques piliers + mois finance actif)
  └─ scripts/build_html.py     Jinja2 templates → embeds HTML
         │
         ▼
GITHUB PAGES  (branche gh-pages · auto-deploy)
  └─ embeds HTML autonomes (D3 + Chart.js + Lucide)
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

- `NOTION_TOKEN` — intégration Notion partagée sur les DBs utilisées

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

# Raccourci
bash scripts/rebuild_life_os.sh

# Déclencher le refresh GitHub Pages sans push de code
bash scripts/trigger_remote_sync.sh --watch

# Serveur local pour tester embeds
cd dist && python -m http.server 8000
# → http://localhost:8000/radar.html
```

## Workflow finance mensuel

La source de vérité finance/pro est maintenant portée par 3 data sources Notion :

- `Finance mensuelle` : 1 ligne par mois actif, avec solde de départ, revenus cash, dépenses budgétées, résultat prévu et fin de mois estimée
- `Lignes budget mensuel` : détails des postes du mois (`Flux`, `Bloc`, `Catégorie`, `Montant`, `Payeur`, `Ordre`)
- `Journal Pro & Financier` : décisions, actions, risques, suivis

Règle simple pour ajouter un nouveau mois :

1. créer une nouvelle ligne dans `Finance mensuelle`
2. renseigner `Mois clé` au format `YYYY-MM`
3. cocher `Actif` sur le mois à afficher dans le dashboard
4. créer les lignes correspondantes dans `Lignes budget mensuel` avec le même `Mois clé`
5. ajouter si besoin des entrées dans `Journal Pro & Financier`
6. relancer localement `bash scripts/rebuild_life_os.sh` pour vérifier
7. si tu veux rafraîchir GitHub Pages tout de suite, lancer `bash scripts/trigger_remote_sync.sh --watch`

```bash
bash scripts/rebuild_life_os.sh
bash scripts/trigger_remote_sync.sh --watch
```

Les vues `sankey-revenu-profi`, `treemap-depenses-profi` et la KPI signature du pilier `Pro & Financier` lisent automatiquement le mois `Actif`.

## Boucle minimale

La boucle de travail est maintenant :

1. dump / saisir les données dans Notion
2. lancer `bash scripts/rebuild_life_os.sh`
3. ouvrir `dist/sankey-revenu-profi.html` ou `dist/treemap-depenses-profi.html`
4. si c'est bon, lancer `bash scripts/trigger_remote_sync.sh --watch`

Le workflow GitHub tourne aussi automatiquement toutes les heures. Donc même sans action manuelle, les changements Notion remontent vers GitHub Pages.

## URL déployée

`https://citaman.github.io/life_os/` (après setup GitHub Pages sur la branche gh-pages)

## Licence

Personnel · non distribué.
