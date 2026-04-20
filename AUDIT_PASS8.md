# Audit Pass 8 — 27 embeds vs V8

## Résumé
- Embeds parfaits : 6
- Embeds avec anomalies mineures : 14
- Embeds avec anomalies majeures : 7

---

## Issues globales
- [ ] **`min-height: 100vh` dans body** (tous les 27 fichiers) — force le body à au moins la hauteur de la fenêtre, crée une barre de scroll vide inutile dans les iframes. Remplacer par `min-height: auto`.
- [ ] **`index.html` liens brisés × 3** — href pointent vers `sankey-pilier-pro_fi.html`, `heatmap-habits-pro_fi.html`, `tree-deps-pro_fi.html` (underscore) mais les fichiers réels utilisent le tiret (`-pro-fi.html`). Clic depuis index = 404.
- [ ] **`area-t2.html` : absence de projection W17-W26** — V8 §4.7 impose une série dashed allant jusqu'à W26. Actuellement : 12 points réels W05-W16 seulement. Manque la deuxième série pointillée.
- [ ] **Heatmap cells 28px au lieu de 32px** — `hm-cell` = 28×28px, `hm-grid` uses 28px columns. Spec V8 §8.3 dit 32×32px. Gap visuel léger mais incohérent avec le design system.
- [ ] **Heatmap : pas de panneau tracker W16 (2e colonne)** — V8 §4.6 requiert un layout 2 colonnes (55% heatmap + 45% tracker détail W16 avec cercles L M M J V S D + score). Les 5 heatmaps piliers n'ont que la partie gauche (grille empilée), le panneau droit est absent.
- [ ] **Aucun Gantt dans les embeds** — V8 §4.10 : Gantt obligatoire par pilier. Aucun fichier dans dist/ ne contient de Gantt. C'est un embed manquant (5 fichiers à créer : `gantt-interieur.html`, `gantt-famille.html`, `gantt-pro-fi.html`, `gantt-creation.html`, `gantt-spirituel.html`).
- [ ] **Hover states manquants sur cellules heatmap** — aucun `:hover` sur `.hm-cell`. Spec V8 §4.4 mentionne hover highlight. Applicable aussi aux nœuds des tree-deps SVGs.

---

## Détail par embed (ordre dist/)

### area-t2.html
- Status: **major**
- Issues:
  - Pas de série "Projection linéaire W17-W26" en dashed (V8 §4.7 obligatoire)
  - Subtitle dit "W05 → W16 · 12 semaines" sans mention de la projection
  - Insight card "Plus forte progression T2" : texte correct mais la troisième insight card affiche une "alerte chute" — pas de highlight visuel fort (rouge)
- Fixes à appliquer (Pass 9):
  - Ajouter dataset projection : `borderDash: [5, 3]`, null×12 + valeurs extrapolées W17-W26, `fill: false`
  - Mettre à jour subtitle + légende
  - Styler l'insight alerte en rouge (`border-left: 3px solid #EF4444; color: #EF4444`)

### book-progression-spirituel.html
- Status: **OK**
- Issues: Aucune. Palette spirituel (#B8860B) correcte, section-header OK, bars par série bien rendues, transition `width 0.6s ease` présente.

### heatmap-habits-creation.html
- Status: **minor**
- Issues:
  - Cellules 28×28px (spec 32px)
  - Pas de panneau tracker W16 détail (2e colonne absente)
  - Aucun `:hover` sur les cellules
- Fixes à appliquer (Pass 9):
  - Uniformiser cells → 32px, grid-col → 32px
  - Ajouter colonne droite tracker W16
  - Ajouter `.hm-cell:hover { opacity: 0.8; cursor: default; }`

### heatmap-habits-famille.html
- Status: **minor**
- Issues: Identiques à heatmap-habits-creation.html (28px cells, pas de tracker panel, pas de hover)
- Fixes à appliquer (Pass 9): Mêmes que ci-dessus avec palette famille (#C84B4B)

### heatmap-habits-interieur.html
- Status: **minor**
- Issues: Identiques (28px cells, tracker W16 absent, pas de hover). Section header OK, palette intérieur correcte.
- Fixes à appliquer (Pass 9): Mêmes corrections, palette #2F7D5B

### heatmap-habits-pro-fi.html
- Status: **minor**
- Issues: Identiques (28px cells, tracker W16 absent, pas de hover). Palette pro-fi OK.
- Fixes à appliquer (Pass 9): Mêmes corrections, palette #1E4D8C

### heatmap-habits-spirituel.html
- Status: **minor**
- Issues: Identiques (28px cells, tracker W16 absent, pas de hover). Palette spirituel OK.
- Fixes à appliquer (Pass 9): Mêmes corrections, palette #B8860B

### index.html
- Status: **major**
- Issues:
  - 3 liens brisés : `sankey-pilier-pro_fi.html`, `heatmap-habits-pro_fi.html`, `tree-deps-pro_fi.html` (underscore au lieu de tiret)
  - Mentionne "18 HTMLs" dans le subtitle mais il y en a 27
  - Aucun lien vers les futurs Gantt (embeds manquants)
- Fixes à appliquer (Pass 9):
  - Remplacer `pro_fi` → `pro-fi` dans les 3 hrefs
  - Mettre à jour le count "18 HTMLs" → "27 HTMLs"

### line-poids-interieur.html
- Status: **OK**
- Issues: Aucune. Palette intérieur (#2F7D5B) correcte, line chart bien structuré, KPI callout row propre, table mensurations présente, section-header OK.

### line-predication-spirituel.html
- Status: **OK**
- Issues: Aucune. Palette spirituel correcte (#B8860B), annotation-banner présente, KPI row bien rendue, section-header OK.

### radar.html
- Status: **minor**
- Issues:
  - "Priorité d'équilibre" callout pointe sur Intérieur (+3 pts) au lieu de Création (+8 pts). Bug logique : le pilier avec le plus grand écart est Création (72% vs 80% = gap de 8), pas Intérieur (82% vs 85% = gap de 3).
  - Couleur callout = `#2F7D5B` (Intérieur) alors qu'elle devrait être `#6B3FA0` (Création)
  - Les gap sont affichés `+3 / +0 / +2 / +8 / +3` mais sémantiquement ce sont des déficits (cible - actuel). Le signe `+` est trompeur.
- Fixes à appliquer (Pass 9):
  - Corriger la logique de sélection du "biggest gap" dans le template `radar.html`
  - Changer `--callout-accent` vers l'accent du pilier à plus grand écart
  - Envisager d'afficher les gaps comme `-3 / 0 / -2 / -8 / -3` (shortfall) ou garder `+` mais labelliser "pts manquants"

### sankey-pilier-creation.html
- Status: **OK**
- Issues: Aucune. Race-guard `width < 100` + `window.addEventListener("load")` présents, PILIER_SUBS correct (Maths S1 3h + Micrograd 4h), palette création OK.

### sankey-pilier-famille.html
- Status: **OK**
- Issues: Aucune. Données correctes (Couple 6h, Lecture James 5h, Jeux enfants 7h, Cuisine 4h), palette famille OK, render guard OK.

### sankey-pilier-interieur.html
- Status: **minor**
- Issues:
  - Sankey uniquement 2 nœuds L1 (Sport 5h + Récup 3h) — spec V8 §4.8 prévoit 3 niveaux (Pilier → Sous-catégories → Activités). Les activités de L2 (Pecs 1.5h, Jambes 1.5h, Dos 1.5h, Cardio 0.5h, Étirements 1h, Foam roller 1h, Sommeil récup 1h) ne sont pas incluses.
  - Visual peu informatif avec seulement 2 branches
- Fixes à appliquer (Pass 9):
  - Ajouter niveau L2 dans PILIER_SUBS ou en hardcodant les sous-activités dans le template

### sankey-pilier-pro-fi.html
- Status: **minor**
- Issues:
  - Même problème : Sankey à 2 niveaux seulement (AVIV Travail 42h). Spec prévoit Data work 30h / Meetings 8h / Admin 4h en L2.
- Fixes à appliquer (Pass 9): Ajouter les sous-activités L2 pour Pro & Fi

### sankey-pilier-spirituel.html
- Status: **minor**
- Issues:
  - 4 nœuds L1 corrects (Réunions 3h, Prédication 3h, Étude perso 2h, Étude Jillian 2h). Mais Réunions aurait dû avoir Mardi soir 2h + Dimanche matin 1h en L2 (spec §4.8).
  - Rendu fonctionnel (race guard OK, 10h total correct)
- Fixes à appliquer (Pass 9): Ajouter L2 pour Réunions (sous-activités)

### sankey-revenu-profi.html
- Status: **OK**
- Issues: Aucune. Palette pro-fi (#1E4D8C) correcte, KPI callout row à 4 colonnes OK, section-header OK.

### sankey-week.html
- Status: **minor**
- Issues:
  - SVG id `sankey-svg` sans viewBox forcé au départ (viewBox dynamique via D3 — OK si race guard présent, mais le guard vérifie `.getBoundingClientRect().width` sans fallback viewBox initial statique comme recommandé en §7.1)
  - Le chart "Admin / autre 23h" manque de contexte — pas de tooltip explicatif
- Fixes à appliquer (Pass 9):
  - Ajouter `viewBox="0 0 1000 500" preserveAspectRatio="xMidYMid meet"` initial sur `<svg id="sankey-svg">`

### skill-tree-creation.html
- Status: **minor**
- Issues:
  - `skill-tree-note` utilise `color: #FAFAFA` pour les balises `<strong>` sur fond clair (`rgba(107,63,160,0.08)`) → texte quasi invisible (blanc sur quasi-blanc)
  - Hover sur les nœuds SVG non implémenté (spec §8 : hover states obligatoires)
- Fixes à appliquer (Pass 9):
  - Corriger `skill-tree-note strong { color: #6B3FA0; }` (remplacer #FAFAFA par l'accent)
  - Ajouter `<title>` sur les cercles SVG + style cursor pointer

### stacked-w16.html
- Status: **OK**
- Issues: Aucune. Chart.js stacked column correct, hover `hoverBackgroundColor` configuré, interaction `mode: "index"` OK, palette 5 piliers correcte, badges-row en bas propre.

### tree-deps-creation.html
- Status: **minor**
- Issues:
  - SVG height = 594px raisonnable mais pas de hover sur les nœuds
  - Labels texte tronqués possibles pour les nœuds "Tâche" à droite (x = 740px dans 900px viewbox, labels débordent)
- Fixes à appliquer (Pass 9):
  - Ajouter `cursor: pointer` et tooltip hover sur cercles SVG
  - Vérifier troncature labels L3

### tree-deps-famille.html
- Status: **minor**
- Issues:
  - SVG height = 400px, 14 nœuds — compact, correct
  - Pas de hover sur nœuds
- Fixes à appliquer (Pass 9): Ajouter hover/tooltip nœuds

### tree-deps-interieur.html
- Status: **major**
- Issues:
  - SVG height = **1164px** pour 35 cercles — très surdimensionné pour un embed iframe. Les nœuds sont éparpillés verticalement, densité faible. Notion iframe sera soit très haute soit coupée.
  - Layout à 2 colonnes (Achievements + Sous-achievements) sans colonne Tâches (pas de 3e niveau visible)
  - Pas de hover sur nœuds
- Fixes à appliquer (Pass 9):
  - Recompacter le layout : `rowSpacing` réduit, ajouter colonne L2 Tâches, viser height ≤ 600px
  - Ajouter hover tooltip sur les nœuds

### tree-deps-pro-fi.html
- Status: **minor**
- Issues:
  - SVG height = 632px, 21 nœuds — acceptable mais dense
  - Pas de hover sur nœuds
- Fixes à appliquer (Pass 9): Hover tooltip nœuds

### tree-deps-spirituel.html
- Status: **minor**
- Issues:
  - SVG height = 400px, compact — OK
  - Pas de hover nœuds
- Fixes à appliquer (Pass 9): Hover tooltip nœuds

### tree-family-famille.html
- Status: **OK**
- Issues: Aucune. Arbre SVG + liste membres complets, palette famille correcte (#C84B4B), member-avatar stylistiquement propre.

### treemap-depenses-profi.html
- Status: **minor**
- Issues:
  - Une insight card utilise `--insight-accent: #10B981` (vert Tailwind) qui est hors palette pro-fi — couleur étrangère dans un embed bleu
  - Eyebrow "REPARTITION DEPENSES" manque l'accent grave → "RÉPARTITION DÉPENSES" (cosmétique mais visible)
- Fixes à appliquer (Pass 9):
  - Remplacer `#10B981` / `#D1FAE5` → `#1E4D8C` / `#C9D8E8` dans l'insight "économies"
  - Corriger l'eyebrow avec accents

---

## Priorités Pass 9

1. **index.html — 3 liens brisés pro_fi → pro-fi** (bloque la navigation depuis l'index)
2. **Radar — bug gap callout** (Création +8 labellisé comme Intérieur +3 — erreur logique visible immédiatement)
3. **area-t2 — ajouter projection dashed W17-W26** (manque structurel critique vs V8 §4.7)
4. **Heatmap × 5 — panneau tracker W16 droit** (manque la moitié du layout §4.6)
5. **min-height: 100vh → auto** dans tous les 27 fichiers (scroll vide dans iframes)
6. **skill-tree-creation — texte blanc invisible** sur note callout
7. **tree-deps-interieur — réduire height 1164 → ≤600px** (surdimensionnement embed)
8. **Sankey piliers × 3 — ajouter niveau L2** (Intérieur, Pro-Fi, Spirituel — rendu trop plat)
9. **treemap — corriger couleur #10B981 hors palette**
10. **Hover tooltip sur nœuds tree-deps × 5 + hm-cell × 5** (polish interaction général)
