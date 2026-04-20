# V2 Phase B — Pass log (10 passes)

Build orchestré pendant ta séance de sport · 2026-04-20, ~1 h autonome.

## URLs live

- **Dashboard embeds** : https://citaman.github.io/life_os/
- **Repo** : https://github.com/Citaman/life_os
- **Notion** : les 6 pages V8.4 (Dashboard + 5 piliers) ont chacune une section "Embeds live · {pilier}" au bas avec les iframes live qui se rechargent chaque matin.

## État final

| Métrique | Valeur |
|---|---|
| Passes effectuées | 10 (+ setup) |
| Commits | 11 |
| Pipeline Python | 3 scripts (fetch 40 s · transform 2 s · build 1 s) |
| Templates Jinja | 17 |
| HTMLs rendus | 27 (index + 4 dashboard + 15 piliers communs + 7 spécifiques) |
| Embeds Notion | 26 blocks poussés sur 6 pages |
| GitHub Actions | cron quotidien 5 h UTC + workflow_dispatch + push-triggered |
| Deploy time | 43 s en moyenne |
| Emojis | 0 (vérifié à chaque pass) |
| Agents délégués | 17 (Pass 4: 4, Pass 5: 3, Pass 6: 7, Pass 8: 1, Pass 9: 4) |

## Les 10 passes

### Pass 1 · Foundation
- `requirements.txt` (notion-client, jinja2, dotenv)
- `.env` avec NOTION_TOKEN + 3 DS IDs + 7 page IDs
- 3 scripts skeleton : fetch / transform / build
- `_base.html` palette V8 (5 piliers), Inter, Lucide, KPI card styles

### Pass 2 · Pipeline data live
- `fetch_notion.py` paginate les 3 DBs : **1391 pages Plan d'exécution + 9 habitudes + 316 Backlog Vie**
- `transform.py` produit `snapshots.json` avec :
  - Rollups piliers (avec override + sous-rollup fallback pour les %)
  - Roadmaps filtrées (Abandonné exclu)
  - 12 semaines historique habit completion
  - Time allocation 168 h
  - Badge W16 = **VERT 81 %** auto-computed

### Pass 3 · Design system
- `_macros.html` : progress_ring · sparkline · kpi_card · pilier_badge · section_header · heatmap_cell · bar_horizontal · status_pill
- `_index.html` : directory des 27 embeds organisé en 3 groupes

### Pass 4 · 4 dashboard embeds (parallel agents)
- `radar.html` 813 lignes · SVG 5-axis + polygones actuel/cible
- `sankey-week.html` 605 lignes · d3-sankey 168 h → 7 buckets → sous-activités
- `area-t2.html` 574 lignes · Chart.js multi-séries 5 piliers
- `stacked-w16.html` 686 lignes · Chart.js stacked bar 7 jours × 5 piliers

### Pass 5 · 3 templates paramétrés × 5 piliers (15 pages)
- `sankey_pilier.html` · heures hebdo pilier → sub-activities
- `heatmap_habits.html` · 4 sem × 7 j, W13-15 synthétique, W16 réel
- `tree_deps.html` · SVG hiérarchique Achievement → Sous, Bézier edges

### Pass 6 · 7 embeds spécifiques (parallel agents)
- `line-poids-interieur.html` · 5 mesures poids + cible 120 kg dashed
- `tree-family-famille.html` · arbre familial SVG + 6 membres
- `sankey-revenu-profi.html` · revenu brut → net → 9 postes
- `treemap-depenses-profi.html` · D3 treemap dépenses mensuelles
- `skill-tree-creation.html` · dark card 3 tracks prérequis
- `book-progression-spirituel.html` · 6 séries + prochaine étude
- `line-predication-spirituel.html` · tendance 6 mois + cible 30h

### Pass 7 · GitHub Actions + Pages
- `.github/workflows/daily-sync.yml` : cron + workflow_dispatch + push
- Repo switched public (Pages free tier)
- Pages configured workflow source
- First run : 40 s · live URL confirmée

### Pass 8 · Audit agent (→ `AUDIT_PASS8.md`)
- 6 parfaits · 14 mineurs · 7 majeurs
- Top 3 issues : liens index brisés, bug radar callout, area-t2 projection manquante
- 10 priorités listées

### Pass 9 · Fix 10 priorités (4 parallel agents)
1. index.html pro_fi → pro-fi + count 27
2. body min-height 100vh → auto (supprime scroll vide iframe)
3. radar biggest gap logique fixée (Création +8 pts violet)
4. area-t2 projection dashed W17-W26 (5 nouvelles séries)
5. heatmap cells 28 → 32px + panneau tracker W16 droit + hover
6. sankey piliers L2 (Intérieur, Pro&Fi, Spirituel)
7. tree-deps-interieur 1164 → 586px (cap 10 sous/ach, rowgap 38→27)
8. skill-tree note color invisible → #6B3FA0
9. treemap #10B981 → #1E4D8C palette pro-fi + accents eyebrow
10. hover tooltips sur tree-deps × 5

### Pass 10 · Notion integration
- `scripts/update_notion_embeds.py` via `notion-client blocks.children.append`
- 26 embed blocks ajoutés aux 6 pages Notion
- Structure par page : divider + H2 "Embeds live · {pilier}" + H3 par embed + embed block URL + caption + source note

## Commits (11 total)

```
e53e9ed Pass 10 — Notion integration: iframes live pushed to 6 pages
0bf51e6 Pass 9 — fix audit 10 priorités
5baa518 Pass 7 — GitHub Actions daily cron + Pages deploy
002ee18 Pass 6 — 7 embeds spécifiques pilier (27 total rendus)
d7758d2 Pass 5 — 3 templates pilier paramétrés (15 pages rendues)
1f7a1e2 Pass 4 — 4 dashboard embeds
be4335a Pass 3 — design system: _macros.html + _base.html design tokens
9910c92 Pass 2 — data pipeline live: 1391 plan + 9 habits + 316 backlog
de9780a Pass 1 — foundation
cac1991 initial commit: README + gitignore
```

## Ce qui reste à vérifier à ton retour

1. Ouvre https://citaman.github.io/life_os/ et clique chaque tuile → les 27 embeds doivent s'afficher proprement
2. Ouvre les 6 pages Notion (Dashboard + 5 piliers) et scroll tout en bas → la section "Embeds live · {pilier}" contient les iframes qui se chargent
3. Les anciennes sections CHART-TODO sont **toujours là** en haut des pages Notion (je n'ai pas touché à elles). Tu peux les supprimer manuellement OU je le fais au retour.
4. Quelques embeds peuvent paraître étriqués en iframe Notion selon la largeur que tu leur donnes — on peut ajuster height/width des iframe blocks dans Notion UI.

## Ce qui est à polir (V2.1 si besoin)

- `AUDIT_PASS8.md` a plus d'items mineurs non priorisés (hover sur heatmap, viewBox sankey initial)
- Tâches atomiques du jour ne sont pas dans un embed séparé (elles sont déjà dans la view native Notion)
- La synthèse W13-W15 des heatmaps est SYNTHÉTIQUE (calculée depuis le trend, pas réelle). Quand tu ajoutes les semaines passées dans la DB Habitudes, le build regénèrera en utilisant les vraies données
- Le net worth 47 200 € est hardcodé — future DB "Comptes" à créer
- Les journals (4 entrées par pilier) sont hardcodés dans les pages Notion — futur DB Journal

## Prochaine étape naturelle : V3 React app

Le pipeline Python et le `snapshots.json` sont prêts pour être consommés par une app React Vite. C'est le projet suivant après validation V2.

---

*2026-04-20 06:05 · Pass log figé · repo : https://github.com/Citaman/life_os · pages : https://citaman.github.io/life_os/*
