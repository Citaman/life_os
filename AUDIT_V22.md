# Audit V2.2 — Notion pages vs snapshots.json

Generated: 2026-04-20 · Truth source: `data/snapshots.json`

---

## Key reference values (snapshots.json)

| Metric | Snapshot value |
|---|---|
| badge_week.score | 81 |
| badge_week.status | VERT |
| badge_week.total_fait | 43 |
| badge_week.total_cible | 53 |
| badge_week.streak_weeks_vert | null |
| trimester t2_percent | 0 % |
| trimester sous_total_done | 0 |
| trimester sous_total_active | 14 |
| trimester achievements_total_active | **9** (not 10) |
| tasks_today.done | 0 |
| tasks_today.total | 4 |
| pilier interieur — progress_avg | **15** |
| pilier famille — progress_avg | **0** |
| pilier pro_fi — progress_avg | **0** |
| pilier creation — progress_avg | **0** |
| pilier spirituel — progress_avg | **0** |
| interieur — achievements_active count | **2** |
| famille — achievements_active count | **2** |
| pro_fi — achievements_active count | **2** |
| creation — achievements_active count | **1** (not 2) |
| spirituel — achievements_active count | **2** |
| interieur — habits_w16 fait/cible | 16/19 = **84 %** |
| famille — habits_w16 fait/cible | 5/6 = **83 %** |
| pro_fi — habits_w16 fait/cible | 5/7 = **71 %** |
| creation — habits_w16 fait/cible | 10/12 = **83 %** |
| spirituel — habits_w16 fait/cible | 7/9 = **78 %** |
| interieur — roadmap count | 5 |
| famille — roadmap count | 5 |
| pro_fi — roadmap count | **7** (not 6) |
| creation — roadmap count | **15** (not 7) |
| spirituel — roadmap count | 5 |
| signature_metric (all piliers) | null — no metric DB yet |

---

## Dashboard (347845e8-e836-81ba-94a4-c5c274844bac)

| Block ID | Type | Current text (truncated 60) | Issue | Fix action |
|---|---|---|---|---|
| 2ae9ab74 | paragraph | "Vendredi 19 avril 2026 · Paris 14 °C · Semaine W16…" | Date hardcoded "19 avril" — today is 20 avril | UPDATE via sync script (template-driven already) |
| 3ead10c2 | heading_1 | "0 / 4" | OK — matches tasks_today (done=0, total=4) | KEEP |
| 78b91f55 | paragraph | "complétées · 4 en attente" | OK — matches tasks_today | KEEP |
| 911b4545 | paragraph | "computed · Plan d'exécution…" | LIVE-TODO annotation — value already correct, note is noise | DELETE |
| 7ff164e9 | heading_1 | "81 %" | OK — matches badge_week.score=81 | KEEP |
| 134aaebc | paragraph | "VERT · 43 / 53 habitudes tenues" | OK — matches badge_week (no streak, no "3ᵉ sem consécutive") | KEEP |
| 27bdf5fd | paragraph | "computed · somme Habitudes.Fait / somme Cible /sem…" | LIVE-TODO annotation — redundant | DELETE |
| e623393a | heading_1 | "0 %" | OK — matches t2_percent=0 | KEEP |
| bbae2cf3 | paragraph | "0 sous-achievements done · 14 en cours · 1391 pages…" | OK — matches snapshot | KEEP |
| 422745a3 | paragraph | "computed · sous-achievements Atteint/Complété…" | LIVE-TODO annotation — redundant | DELETE |
| 9a3f89a2 | callout | "10 achievements actifs · 2 par pilier…" | **STALE**: snapshot = 9 active (Création has 1, not 2). "2 par pilier" is wrong | UPDATE to "9 achievements actifs · Création : 1 actif · autres : 2/pilier" |
| d1b17eb0 | paragraph | "LIVE-TODO Phase B : Score % = Fait / (Cible × 1)…" | LIVE-TODO annotation inside Habitudes callout — redundant | DELETE |
| cd42af0e | paragraph | "Viz non-natives Notion (Radar · Sankey · Area chart…)" | Embedded charts already exist, this TODO paragraph is stale | DELETE |
| 0ed4bb56 | paragraph | "51 %" | **STALE**: snap.piliers.interieur.progress_avg = 15 | UPDATE to "15 %" |
| 61a65779 | paragraph | "LIVE-TODO Phase B : moyenne Progression actuelle…" | LIVE-TODO annotation — redundant | DELETE |
| 318e3e50 | paragraph | "52,5 %" | **STALE**: snap.piliers.famille.progress_avg = 0 | UPDATE to "0 %" or "—" |
| 7609680a | paragraph | "LIVE-TODO Phase B : rollup moyenne Pilier=Famille" | LIVE-TODO annotation — redundant | DELETE |
| 6e136260 | paragraph | "51,5 %" | **STALE**: snap.piliers.pro_fi.progress_avg = 0 | UPDATE to "0 %" or "—" |
| de73930f | paragraph | "LIVE-TODO Phase B : rollup moyenne Pilier=Pro & Fi" | LIVE-TODO annotation — redundant | DELETE |
| ef1edea1 | paragraph | "27,5 %" | **STALE**: snap.piliers.creation.progress_avg = 0 | UPDATE to "0 %" or "—" |
| 61a28607 | paragraph | "LIVE-TODO Phase B : rollup moyenne Pilier=Création…" | LIVE-TODO annotation — redundant | DELETE |
| 6c2f3afd | paragraph | "62,5 %" | **STALE**: snap.piliers.spirituel.progress_avg = 0 | UPDATE to "0 %" or "—" |
| 8bb7cf4e | paragraph | "LIVE-TODO Phase B : rollup moyenne Pilier=Spirituel" | LIVE-TODO annotation — redundant | DELETE |
| d7bf04eb | heading_2 | "Roadmap Création 2026–2027" | Roadmap is shown for Création here on Dashboard — snap has 15 roadmap entries for création | OK — section label only, no count claim here |
| 3b267b1e | callout | "7 programmes séquencés · Gantt · Actifs + Planifiés" | **STALE**: snap.piliers.creation.roadmap has 15 entries (this is the Dashboard Création roadmap, different scope?) — if roadmap count is from snap, must be 15 | UPDATE to "15 programmes séquencés · Gantt · Actifs + Planifiés" |
| e2100c19 | toggle | "Séquençage détaillé des 7 programmes" | **STALE** heading: 7 vs 15 from snap | UPDATE to "Séquençage détaillé des 15 programmes" |
| 82d731b4 | paragraph | "Dernière mise à jour : 2026-04-19 · V8.4 harmonisée…" | Date stale (was 19 avril, today is 20) — acceptable low-priority | UPDATE date to 2026-04-20 on next sync |

---

## Intérieur (348845e8-e836-8179-9cbe-f8940b5d1195)

| Block ID | Type | Current text (truncated 60) | Issue | Fix action |
|---|---|---|---|---|
| 14e38acc | heading_1 | "81 %" | **STALE**: real interieur habit % = 16/19 = 84 % | UPDATE to "84 %" |
| e6a1ba09 | paragraph | "17 / 21 cibles semaine" | **STALE**: real = 16 / 19 | UPDATE to "16 / 19 cibles semaine" |
| d4e29e2d | paragraph | "LIVE-TODO Phase B : somme Fait / (Cible×1)…" | LIVE-TODO annotation — redundant | DELETE |
| ce6956ea | heading_1 | "122,7 kg" | **STALE**: signature_metric = null (no DB). No valid source | UPDATE to "— kg" (null placeholder) |
| f75e3331 | paragraph | "125 → 122,7 · -2,3 kg depuis janv." | **STALE**: hardcoded weight, no DB backing | UPDATE to "— · pas de DB Mesures corps" or DELETE |
| 1fe415a3 | paragraph | "LIVE-TODO Phase B : DB « Mesures corps »…" | LIVE-TODO annotation | DELETE |
| 52926420 | paragraph | "LIVE-TODO Phase B : count Type=Achievement…" | LIVE-TODO annotation | DELETE |
| 88b977fc | paragraph | "plafond Time Budget respecté" | OK — contextual note, not computed | KEEP |
| 69d0db2f | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Intérieur + Type=Achievement…" | Redundant note — DB view is already embedded below | DELETE |
| 02be5ad1 | paragraph | "CHART-TODO Phase B : 2 progress rings SVG…" | Leftover CHART-TODO inline paragraph | DELETE |
| 1182532c | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Intérieur + Type=Sous-achi…" | Redundant note — DB view embedded below | DELETE |
| 7befb750 | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Intérieur + Type=Tâche ato…" | Redundant note — DB view embedded below | DELETE |
| 56dcd371 | paragraph | "CHART-TODO Phase B : bar chart horizontal Tâches/jour…" | Leftover CHART-TODO inline paragraph | DELETE |
| 394d6243 | paragraph | "Vue liée Habitudes DB ci-dessous — filtrée Pilier=Intérieur + Semaine=W16" | Redundant note | DELETE |
| 379438fa | paragraph | "CHART-TODO Phase B : heatmap 4 dernières semaines…" | Leftover CHART-TODO | DELETE |
| 19745350 | paragraph | "Vue liée Timeline ci-dessous — Plan d'exécution filtrée Pilier=Intérieur + Type=…" | Redundant note | DELETE |
| d195ba88 | paragraph | "Historique récent :" inside toggle | Heading for fake bullet list | DELETE (with children) |
| 551c2466 | bulleted_list_item | "Samedi 19 avril : PR développé couché 65 kg (3 × 8)…" | **FAKE** hardcoded history — DELETE | DELETE |
| e367fc51 | bulleted_list_item | "Jeudi 17 avril : tractions +10 kg (1er essai BW+10)…" | **FAKE** hardcoded history | DELETE |
| 65f0d0ee | bulleted_list_item | "Mardi 15 avril : dos/biceps classique" | **FAKE** hardcoded history | DELETE |
| c639d5bb | bulleted_list_item | "Lundi 14 avril : pecs/triceps classique" | **FAKE** hardcoded history | DELETE |
| 83ad0e8f | callout | "SAMEDI 19 AVRIL 2026" | **FAKE** journal entry — dates didn't happen | DELETE entire callout + child |
| a8488d84 | paragraph | "Séance pecs/triceps — nouveau PR…" | Child of fake journal callout | DELETE (with parent) |
| 21afba8b | callout | "JEUDI 17 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 909d6839 | paragraph | "Dos/biceps + tractions testées +10 kg…" | Child of fake journal callout | DELETE (with parent) |
| be0915f9 | callout | "MARDI 15 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 96170ae3 | paragraph | "4ᵉ semaine consécutive coucher 22 h 30…" | Child of fake journal callout | DELETE (with parent) |
| 2b24b600 | callout | "LUNDI 14 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 5779ad3c | paragraph | "Revue hebdo W15. Sport 4/5 cible…" | Child of fake journal callout | DELETE (with parent) |
| f3a9edf9 | paragraph | "LIVE-TODO Phase B : DB Journal dédiée…" | LIVE-TODO annotation | REPLACE with single TODO callout "DB Journal à venir" |
| 3ee519e8 | paragraph | "Dernière mise à jour : 2026-04-19 · V8.4 pilier Intérieur" | Date stale | UPDATE date to 2026-04-20 |

---

## Famille (348845e8-e836-818d-96ba-da79b2fcfb03)

| Block ID | Type | Current text (truncated 60) | Issue | Fix action |
|---|---|---|---|---|
| f095a3f6 | heading_1 | "83 %" | OK — matches snap famille habit % = 5/6 = 83 % | KEEP |
| 1fe89d81 | paragraph | "5 / 6 sessions lecture James" | OK — matches snap | KEEP |
| 1133e791 | paragraph | "LIVE-TODO Phase B : somme Fait Habitudes Pilier=Famille" | LIVE-TODO annotation | DELETE |
| 35089d3f | heading_1 | "Samedi 21 h" | **STALE/FAKE**: date-night is hardcoded — no DB source | UPDATE to "—" (null placeholder) |
| 3b5f7be9 | paragraph | "1/1 prévu · ciné + resto quartier" | **STALE/FAKE**: hardcoded event detail — no DB | UPDATE to "—" or DELETE |
| 39331c71 | paragraph | "LIVE-TODO Phase B : rollup Couple Mirane achievement" | LIVE-TODO annotation | DELETE |
| f2818be7 | paragraph | "LIVE-TODO Phase B : count Type=Achievement + Pilier=Famille…" | LIVE-TODO annotation | DELETE |
| fb4e8b34 | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Famille + Type=Achievement…" | Redundant note | DELETE |
| 3eaa1354 | paragraph | "CHART-TODO Phase B : 2 progress rings SVG…" | Leftover CHART-TODO inline | DELETE |
| e8521af2 | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Famille + Type=Sous-achiev…" | Redundant note | DELETE |
| cdd2fc36 | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Famille + Type=Tâche atomi…" | Redundant note | DELETE |
| c46b8600 | paragraph | "CHART-TODO Phase B : bar chart horizontal Tâches Famille/jour W16" | Leftover CHART-TODO | DELETE |
| d43d6912 | paragraph | "Vue liée Habitudes DB ci-dessous — filtrée Pilier=Famille + Semaine=W16" | Redundant note | DELETE |
| d0a87980 | paragraph | "CHART-TODO Phase B : heatmap 4 dernières semaines…" | Leftover CHART-TODO | DELETE |
| a5957fd8 | paragraph | "Vue liée Timeline ci-dessous — Plan d'exécution filtrée Pilier=Famille + Type=Ac…" | Redundant note | DELETE |
| 858ddc69 | paragraph | "CHART-TODO Phase B : arbre généalogique SVG…" | Leftover CHART-TODO | DELETE |
| 34741f52 | callout | "SAMEDI 12 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| aa6730a9 | paragraph | "Date-night Mirane — cinéma + resto quartier…" | Child of fake journal callout | DELETE (with parent) |
| ab77397d | callout | "JEUDI 10 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 2e77e787 | paragraph | "James — lecture Le Petit Prince…" | Child of fake journal callout | DELETE (with parent) |
| 3e0ba4ad | callout | "DIMANCHE 7 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| d242848c | paragraph | "Check-in dominical — revue budget famille…" | Child of fake journal callout | DELETE (with parent) |
| 703a547d | callout | "VENDREDI 4 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| fdb1dcdb | paragraph | "Harper — premier mot…" | Child of fake journal callout | DELETE (with parent) |
| 4f4fb568 | paragraph | "LIVE-TODO Phase B : DB Journal dédiée…" | LIVE-TODO annotation | REPLACE with single TODO callout "DB Journal à venir" |
| 48ed1476 | paragraph | "Dernière mise à jour : 2026-04-19 · V8.4 pilier Famille" | Date stale | UPDATE date to 2026-04-20 |

---

## Pro & Financier (348845e8-e836-81b0-aaf7-e3b81b92416c)

| Block ID | Type | Current text (truncated 60) | Issue | Fix action |
|---|---|---|---|---|
| 0308efde | heading_1 | "71 %" | OK — matches snap pro_fi habit % = 5/7 = 71 % | KEEP |
| 29050a06 | paragraph | "5 / 7 Budget 10 min" | OK — matches snap | KEEP |
| cf2ad71c | paragraph | "LIVE-TODO Phase B : somme Fait Habitudes Pilier=Pro & Fi" | LIVE-TODO annotation | DELETE |
| 0cc9fdf7 | heading_1 | "47 200 €" | **STALE/FAKE**: signature_metric = null — no DB source | UPDATE to "— €" (null placeholder) |
| f2ee226f | paragraph | "+5 000 € vs W05 · épargne 18 %" | **STALE/FAKE**: hardcoded delta, no DB backing | UPDATE to "—" or DELETE |
| dba477bf | paragraph | "LIVE-TODO Phase B : DB « Comptes »…" | LIVE-TODO annotation | DELETE |
| 2258857d | paragraph | "LIVE-TODO Phase B : count Type=Achievement + Pilier=Pro & Fi…" | LIVE-TODO annotation | DELETE |
| dd58876f | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Pro & Financier + Type=Ach…" | Redundant note | DELETE |
| 2b9d137e | paragraph | "CHART-TODO Phase B : 2 progress rings SVG…" | Leftover CHART-TODO | DELETE |
| 9d6cfa7f | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Pro & Financier + Type=Sou…" | Redundant note | DELETE |
| cc375fb1 | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Pro & Financier + Type=Tâc…" | Redundant note | DELETE |
| 33e62e55 | paragraph | "CHART-TODO Phase B : bar chart horizontal tâches/jour…" | Leftover CHART-TODO | DELETE |
| f066f11b | paragraph | "Vue liée Habitudes DB ci-dessous — filtrée Pilier=Pro & Financier + Semaine=W16" | Redundant note | DELETE |
| 7c999dfb | paragraph | "CHART-TODO Phase B : heatmap 4 dernières semaines…" | Leftover CHART-TODO | DELETE |
| 00b2c490 | paragraph | "Vue liée Timeline ci-dessous — Plan d'exécution filtrée Pilier=Pro & Financier +…" | Redundant note | DELETE |
| 32923e17 | callout | "6 programmes séquencés · Gantt · Actifs + Planifiés" | **STALE**: snap.piliers.pro_fi.roadmap = 7 entries (not 6) | UPDATE to "7 programmes séquencés…" |
| 23e5127d | toggle | "Séquençage détaillé des 6 programmes" | **STALE**: should be 7 | UPDATE to "Séquençage détaillé des 7 programmes" |
| e718eae8 | callout | "VENDREDI 11 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 57f57003 | paragraph | "Échangé avec RH AVIV sur mutuelle family…" | Child of fake journal callout | DELETE (with parent) |
| fad5af7d | callout | "LUNDI 14 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 13d72501 | paragraph | "Décision PEA : pas de mouvement avant septembre…" | Child of fake journal callout | DELETE (with parent) |
| 08a2140b | callout | "MARDI 15 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 1d15efb4 | paragraph | "Taxe foncière 854 € payée…" | Child of fake journal callout | DELETE (with parent) |
| cb1e2707 | callout | "SAMEDI 19 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 353ae7b9 | paragraph | "Revue hebdo budget W16…" | Child of fake journal callout | DELETE (with parent) |
| 4335403d | paragraph | "LIVE-TODO Phase B : DB Journal dédiée…" | LIVE-TODO annotation | REPLACE with single TODO callout "DB Journal à venir" |
| c8ece303 | paragraph | "Dernière mise à jour : 2026-04-19 · V8.4 pilier Pro & Financier" | Date stale | UPDATE date to 2026-04-20 |

---

## Création (348845e8-e836-8119-8920-f14c27aa5f30)

| Block ID | Type | Current text (truncated 60) | Issue | Fix action |
|---|---|---|---|---|
| 0d4b729a | heading_1 | "2 / 2" | **STALE**: snap.piliers.creation.achievements_active count = **1** (not 2) | UPDATE to "1 / 2" |
| 7a6b49fa | paragraph | "plafond Time Budget (Tech+Arts combinés)" | OK — contextual | KEEP |
| 8ff71385 | paragraph | "LIVE-TODO Phase B : count Type=Achievement + Pilier=Création…" | LIVE-TODO annotation | DELETE |
| 49e50263 | heading_1 | "83 %" | OK — matches snap création habit % = 10/12 = 83 % | KEEP |
| 038678ad | paragraph | "10 / 12 sessions code + maths" | OK — matches snap | KEEP |
| 2b93c605 | paragraph | "LIVE-TODO Phase B : somme Fait Habitudes Pilier=Création…" | LIVE-TODO annotation | DELETE |
| 9ba05b0e | heading_1 | "27,5 %" | **STALE**: snap.piliers.creation.progress_avg = 0 | UPDATE to "0 %" or "—" |
| 87f7f8fd | paragraph | "Pilier le plus bas · à intensifier fin T2" | Commentary based on stale value — should be rechecked | UPDATE or DELETE (stale context) |
| 87476544 | paragraph | "LIVE-TODO Phase B : rollup moyenne achievements Pilier=Création" | LIVE-TODO annotation | DELETE |
| e5a9fc8d | callout | "2 chantiers structurants — Maths S1 algèbre linéaire (30 %)…" | **STALE**: only 1 achievement active; "30 %" is hardcoded | UPDATE to "1 chantier actif" + remove hardcoded % |
| 296f4335 | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Création + Type=Achievemen…" | Redundant note | DELETE |
| 3e90bc85 | paragraph | "CHART-TODO Phase B : 2 progress rings SVG…" | Leftover CHART-TODO | DELETE |
| 1646316c | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Création + Type=Sous-achie…" | Redundant note | DELETE |
| 97ff747f | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Création + Type=Tâche atom…" | Redundant note | DELETE |
| 5d9ba32e | paragraph | "CHART-TODO Phase B : bar chart horizontal tâches/jour (L=2, M=1, M=2, J=1, V=2…" | Leftover CHART-TODO with hardcoded day counts | DELETE |
| 9a88ac85 | paragraph | "Vue liée Habitudes DB ci-dessous — filtrée Pilier=Création + Semaine=W16" | Redundant note | DELETE |
| 5be60c90 | paragraph | "CHART-TODO Phase B : heatmap 4 dernières semaines…" | Leftover CHART-TODO | DELETE |
| 4ac567f5 | paragraph | "Vue liée Timeline ci-dessous — Plan d'exécution filtrée Pilier=Création + Type=A…" | Redundant note | DELETE |
| d6e4fc1f | callout | "7 programmes séquencés · Gantt · Actifs + Planifiés…" | **STALE**: snap.piliers.creation.roadmap = 15 entries | UPDATE to "15 programmes séquencés…" |
| 608c214c | toggle | "Séquençage détaillé des 7 programmes" | **STALE**: should be 15 | UPDATE to "Séquençage détaillé des 15 programmes" |
| 0547f1fb | callout | "MARDI 15 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| a43b4f99 | paragraph | "Micrograd — forward pass Value class réussi…" | Child of fake journal callout | DELETE (with parent) |
| 81530326 | callout | "MERCREDI 16 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| f949dd57 | paragraph | "MIT 18.06 chap. 3 — élimination de Gauss…" | Child of fake journal callout | DELETE (with parent) |
| 3f2861f0 | callout | "VENDREDI 18 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| fc91429c | paragraph | "Pull request repo micrograd soumis…" | Child of fake journal callout | DELETE (with parent) |
| 4059a2e9 | callout | "DIMANCHE 13 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| daf76ccb | paragraph | "Revue W15 — 6/6 sessions micrograd…" | Child of fake journal callout | DELETE (with parent) |
| dc79ef7e | paragraph | "LIVE-TODO Phase B : DB Journal Pilier=Création" | LIVE-TODO annotation | REPLACE with single TODO callout "DB Journal à venir" |
| 4d7e4e98 | paragraph | "Dernière mise à jour : 2026-04-19 · V8.4 pilier Création" | Date stale | UPDATE date to 2026-04-20 |

---

## Spirituel (348845e8-e836-8133-a818-ea7de5c6b17e)

| Block ID | Type | Current text (truncated 60) | Issue | Fix action |
|---|---|---|---|---|
| 311b76e2 | heading_1 | "2 / 2" | OK — snap.piliers.spirituel.achievements_active = 2 | KEEP |
| 8436d5fd | paragraph | "plafond Time Budget respecté" | OK | KEEP |
| f72b87f1 | paragraph | "LIVE-TODO Phase B : count Type=Achievement + Pilier=Spirituel…" | LIVE-TODO annotation | DELETE |
| 492aafed | heading_1 | "78 %" | OK — matches snap spirituel habit % = 7/9 = 78 % | KEEP |
| 1036f738 | paragraph | "7 / 9 étude + prédication" | OK — matches snap | KEEP |
| 9df3272c | paragraph | "LIVE-TODO Phase B : somme Fait Habitudes Pilier=Spirituel" | LIVE-TODO annotation | DELETE |
| 7fea15dc | heading_1 | "24 h / 30 h" | **STALE/FAKE**: signature_metric = null — no DB source for prédication hours | UPDATE to "— h / 30 h" |
| d63a4e02 | paragraph | "80 % objectif mensuel · 11 jours restants" | **STALE/FAKE**: computed from hardcoded 24 h, no DB | UPDATE to "—" or DELETE |
| df22cc9e | paragraph | "LIVE-TODO Phase B : rollup heures prédication…" | LIVE-TODO annotation | DELETE |
| 5613e428 | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Spirituel + Type=Achieveme…" | Redundant note | DELETE |
| 80c31ef0 | paragraph | "CHART-TODO Phase B : 2 progress rings SVG…" | Leftover CHART-TODO | DELETE |
| cbf75c28 | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Spirituel + Type=Sous-achi…" | Redundant note | DELETE |
| 4fe0e11d | paragraph | "Vue liée Plan d'exécution ci-dessous — filtrée Pilier=Spirituel + Type=Tâche ato…" | Redundant note | DELETE |
| f9784542 | paragraph | "CHART-TODO Phase B : bar chart horizontal…" | Leftover CHART-TODO | DELETE |
| 2016adb8 | paragraph | "Vue liée Habitudes DB ci-dessous — filtrée Pilier=Spirituel + Semaine=W16" | Redundant note | DELETE |
| ff4e9caa | paragraph | "CHART-TODO Phase B : heatmap 4 dernières semaines…" | Leftover CHART-TODO | DELETE |
| 5ef9f73d | paragraph | "Vue liée Timeline ci-dessous — Plan d'exécution filtrée Pilier=Spirituel + Type=…" | Redundant note | DELETE |
| 2cc8aef6 | callout | "MARDI 15 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 782f0aad | paragraph | "Réunion Vie et Ministère Sucy-Nord…" | Child of fake journal callout | DELETE (with parent) |
| acb5cb12 | callout | "SAMEDI 12 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 66780a36 | paragraph | "Sortie prédication — 3 h secteur Sucy-en-Brie…" | Child of fake journal callout | DELETE (with parent) |
| e7c714db | callout | "MERCREDI 9 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 7516e70a | paragraph | "Étude Jillian — chap. 13 complété…" | Child of fake journal callout | DELETE (with parent) |
| bfebaa51 | callout | "DIMANCHE 6 AVRIL 2026" | **FAKE** journal entry | DELETE entire callout + child |
| 140a20ed | paragraph | "Revue hebdo W15 — bilan spirituel…" | Child of fake journal callout | DELETE (with parent) |
| 3e10e55d | paragraph | "LIVE-TODO Phase B : DB Journal Pilier=Spirituel" | LIVE-TODO annotation | REPLACE with single TODO callout "DB Journal à venir" |
| ad1596cb | paragraph | "Dernière mise à jour : 2026-04-19 · V8.4 pilier Spirituel" | Date stale | UPDATE date to 2026-04-20 |

---

## Summary

| Category | Count |
|---|---|
| Blocks to DELETE (redundant "Vue liée…" notes) | 18 |
| Blocks to DELETE (leftover CHART-TODO inline paragraphs) | 14 |
| Blocks to DELETE (LIVE-TODO annotations) | 20 |
| Blocks to DELETE (fake journal callouts + children, 4×6 pages) | 24 callouts + 24 children = **48** |
| Blocks to DELETE (fake "Historique récent" bullets in Intérieur toggle) | 5 (heading + 4 bullets) |
| **Total blocks to DELETE** | **~105** |
| Blocks to UPDATE (hardcoded numbers → real from snapshots) | **15** |
| Blocks to REPLACE (LIVE-TODO journal → "DB Journal à venir" callout) | 5 |
| Blocks OK | All others |

### Top hardcoded number violations

1. **Dashboard "Les 5 piliers"** — all 5 pilier progress % hardcoded (51%, 52.5%, 51.5%, 27.5%, 62.5%) vs snapshots (15%, 0%, 0%, 0%, 0%). All 5 must be updated.
2. **Dashboard achievements callout** — claims "10 achievements actifs · 2 par pilier" — real is 9 (Création has 1 active, not 2).
3. **Création page — KPI column** — claims "2 / 2" achievements and "27,5 %" progress — real is 1 active and 0 %.
4. **Intérieur habit % KPI** — "81 % / 17/21" vs real 84% / 16/19.
5. **Pro & Fi roadmap count** — "6 programmes" vs 7 in snap.
6. **Création roadmap count** — "7 programmes" vs 15 in snap.
7. **Signature metrics** (Intérieur poids 122.7 kg, Pro net worth 47200€, Spirituel prédication 24h/30h) — all signature_metric = null, all hardcoded without DB backing.

---

## Cleanup script plan — `scripts/cleanup_v22.py`

```python
"""
cleanup_v22.py — DELETE redundant blocks, UPDATE stale KPIs.
DO NOT RUN YET — audit only.

Approach:
  1. Load snapshots.json to get truth values.
  2. For each DELETE operation: client.blocks.delete(block_id=ID)
  3. For each UPDATE operation: client.blocks.update(block_id=ID, paragraph={rich_text=[...]})
     or heading_1/heading_2/callout depending on type.
  4. For REPLACE Journal LIVE-TODO → single callout:
     a. Delete the LIVE-TODO paragraph.
     b. client.blocks.children.append(block_id=PARENT_SECTION_ID, children=[callout block])
"""

import json
from notion_client import Client

client = Client(auth=os.environ["NOTION_TOKEN"])
snap = json.load(open("data/snapshots.json"))

# ─────────────────────────────────────────────────────────────
# PHASE 1 — DELETE redundant annotations + fake content
# ─────────────────────────────────────────────────────────────

BLOCKS_TO_DELETE = [
    # Dashboard — LIVE-TODO / redundant
    "911b4545",  # computed note tâches
    "27bdf5fd",  # computed note badge
    "422745a3",  # computed note trimestre
    "d1b17eb0",  # LIVE-TODO Habitudes
    "cd42af0e",  # Viz non-natives TODO
    # Dashboard — LIVE-TODO piliers
    "61a65779",  # Intérieur LIVE-TODO
    "7609680a",  # Famille LIVE-TODO
    "de73930f",  # Pro LIVE-TODO
    "61a28607",  # Création LIVE-TODO
    "8bb7cf4e",  # Spirituel LIVE-TODO

    # Intérieur — LIVE-TODO + redundant notes
    "d4e29e2d",  # LIVE-TODO habitudes
    "1fe415a3",  # LIVE-TODO poids
    "52926420",  # LIVE-TODO achievements
    "69d0db2f",  # Vue liée achievements
    "02be5ad1",  # CHART-TODO rings
    "1182532c",  # Vue liée sous-achievements
    "7befb750",  # Vue liée tâches
    "56dcd371",  # CHART-TODO bar
    "394d6243",  # Vue liée habitudes
    "379438fa",  # CHART-TODO heatmap
    "19745350",  # Vue liée timeline
    # Intérieur — fake Historique récent (inside toggle 24e3c72e)
    "d195ba88",  # "Historique récent :" paragraph
    "551c2466",  # Samedi 19 avril bullet
    "e367fc51",  # Jeudi 17 avril bullet
    "65f0d0ee",  # Mardi 15 avril bullet
    "c639d5bb",  # Lundi 14 avril bullet
    # Intérieur — fake journal callouts (4 entries)
    "83ad0e8f",  # SAMEDI 19 AVRIL callout
    "21afba8b",  # JEUDI 17 AVRIL callout
    "be0915f9",  # MARDI 15 AVRIL callout
    "2b24b600",  # LUNDI 14 AVRIL callout
    # Note: children (a8488d84, 909d6839, 96170ae3, 5779ad3c) auto-deleted with parent

    # Famille — LIVE-TODO + redundant notes
    "1133e791",  # LIVE-TODO habitudes
    "39331c71",  # LIVE-TODO date-night
    "f2818be7",  # LIVE-TODO achievements
    "fb4e8b34",  # Vue liée achievements
    "3eaa1354",  # CHART-TODO rings
    "e8521af2",  # Vue liée sous-achievements
    "cdd2fc36",  # Vue liée tâches
    "c46b8600",  # CHART-TODO bar
    "d43d6912",  # Vue liée habitudes
    "d0a87980",  # CHART-TODO heatmap
    "a5957fd8",  # Vue liée timeline
    "858ddc69",  # CHART-TODO arbre généalogique
    # Famille — fake journal callouts (4 entries)
    "34741f52",  # SAMEDI 12 AVRIL callout
    "ab77397d",  # JEUDI 10 AVRIL callout
    "3e0ba4ad",  # DIMANCHE 7 AVRIL callout
    "703a547d",  # VENDREDI 4 AVRIL callout

    # Pro & Fi — LIVE-TODO + redundant notes
    "cf2ad71c",  # LIVE-TODO habitudes
    "dba477bf",  # LIVE-TODO net worth
    "2258857d",  # LIVE-TODO achievements
    "dd58876f",  # Vue liée achievements
    "2b9d137e",  # CHART-TODO rings
    "9d6cfa7f",  # Vue liée sous-achievements
    "cc375fb1",  # Vue liée tâches
    "33e62e55",  # CHART-TODO bar
    "f066f11b",  # Vue liée habitudes
    "7c999dfb",  # CHART-TODO heatmap
    "00b2c490",  # Vue liée timeline
    # Pro & Fi — fake journal callouts (4 entries)
    "e718eae8",  # VENDREDI 11 AVRIL callout
    "fad5af7d",  # LUNDI 14 AVRIL callout
    "08a2140b",  # MARDI 15 AVRIL callout
    "cb1e2707",  # SAMEDI 19 AVRIL callout

    # Création — LIVE-TODO + redundant notes
    "8ff71385",  # LIVE-TODO achievements
    "2b93c605",  # LIVE-TODO habitudes
    "87476544",  # LIVE-TODO progress
    "296f4335",  # Vue liée achievements
    "3e90bc85",  # CHART-TODO rings
    "1646316c",  # Vue liée sous-achievements
    "97ff747f",  # Vue liée tâches
    "5d9ba32e",  # CHART-TODO bar
    "9a88ac85",  # Vue liée habitudes
    "5be60c90",  # CHART-TODO heatmap
    "4ac567f5",  # Vue liée timeline
    # Création — fake journal callouts (4 entries)
    "0547f1fb",  # MARDI 15 AVRIL callout
    "81530326",  # MERCREDI 16 AVRIL callout
    "3f2861f0",  # VENDREDI 18 AVRIL callout
    "4059a2e9",  # DIMANCHE 13 AVRIL callout

    # Spirituel — LIVE-TODO + redundant notes
    "f72b87f1",  # LIVE-TODO achievements
    "9df3272c",  # LIVE-TODO habitudes
    "df22cc9e",  # LIVE-TODO prédication
    "5613e428",  # Vue liée achievements
    "80c31ef0",  # CHART-TODO rings
    "cbf75c28",  # Vue liée sous-achievements
    "4fe0e11d",  # Vue liée tâches
    "f9784542",  # CHART-TODO bar
    "2016adb8",  # Vue liée habitudes
    "ff4e9caa",  # CHART-TODO heatmap
    "5ef9f73d",  # Vue liée timeline
    # Spirituel — fake journal callouts (4 entries)
    "2cc8aef6",  # MARDI 15 AVRIL callout
    "acb5cb12",  # SAMEDI 12 AVRIL callout
    "e7c714db",  # MERCREDI 9 AVRIL callout
    "bfebaa51",  # DIMANCHE 6 AVRIL callout
]

for block_id in BLOCKS_TO_DELETE:
    client.blocks.delete(block_id=block_id)
    print(f"DELETED {block_id}")


# ─────────────────────────────────────────────────────────────
# PHASE 2 — UPDATE stale KPIs with real values from snapshots
# ─────────────────────────────────────────────────────────────

def plain_text(text):
    return [{"type": "text", "text": {"content": text}}]

# Dashboard — "Les 5 piliers" progress %
updates = [
    # (block_id, new_text)
    ("0ed4bb56", f"{snap['piliers']['interieur']['progress_avg']} %"),      # Intérieur: 15 %
    ("318e3e50", f"{snap['piliers']['famille']['progress_avg']} %"),         # Famille: 0 %
    ("6e136260", f"{snap['piliers']['pro_fi']['progress_avg']} %"),          # Pro: 0 %
    ("ef1edea1", f"{snap['piliers']['creation']['progress_avg']} %"),        # Création: 0 %
    ("6c2f3afd", f"{snap['piliers']['spirituel']['progress_avg']} %"),       # Spirituel: 0 %
    # Dashboard — achievements callout
    ("9a3f89a2", "9 achievements actifs · Création : 1 actif · autres piliers : 2"),
    # Dashboard — roadmap creation count
    ("3b267b1e", f"{len(snap['piliers']['creation']['roadmap'])} programmes séquencés · Gantt · Actifs + Planifiés"),
    # Intérieur — habitudes KPI
    ("14e38acc", "84 %"),      # heading_1 habit %
    ("e6a1ba09", "16 / 19 cibles semaine"),
    # Intérieur — poids (null placeholder)
    ("ce6956ea", "— kg"),
    ("f75e3331", "—  · pas de DB Mesures corps"),
    # Pro & Fi — net worth (null placeholder)
    ("0cc9fdf7", "— €"),
    ("f2ee226f", "—  · pas de DB Comptes"),
    # Création — achievements count
    ("0d4b729a", "1 / 1"),  # 1 active achievement
    ("9ba05b0e", "0 %"),    # progress_avg
    # Spirituel — prédication (null placeholder)
    ("7fea15dc", "— h / 30 h"),
    ("d63a4e02", "—  · pas de DB Journal prédication"),
]

for block_id, new_text in updates:
    # Fetch block to get its type, then update accordingly
    block = client.blocks.retrieve(block_id=block_id)
    btype = block["type"]
    client.blocks.update(
        block_id=block_id,
        **{btype: {"rich_text": plain_text(new_text)}}
    )
    print(f"UPDATED {block_id} → '{new_text}'")

# Roadmap heading toggles
toggle_updates = [
    ("e2100c19", f"Séquençage détaillé des {len(snap['piliers']['creation']['roadmap'])} programmes"),  # Dashboard
    ("608c214c", f"Séquençage détaillé des {len(snap['piliers']['creation']['roadmap'])} programmes"),  # Création
    ("23e5127d", f"Séquençage détaillé des {len(snap['piliers']['pro_fi']['roadmap'])} programmes"),     # Pro & Fi
]
for block_id, new_text in toggle_updates:
    client.blocks.update(block_id=block_id, toggle={"rich_text": plain_text(new_text)})
    print(f"UPDATED toggle {block_id} → '{new_text}'")

# Callout heading for Pro & Fi roadmap
client.blocks.update(block_id="32923e17", callout={"rich_text": plain_text(
    f"{len(snap['piliers']['pro_fi']['roadmap'])} programmes séquencés · Gantt · Actifs + Planifiés"
)})

# Callout for Création roadmap
client.blocks.update(block_id="d6e4fc1f", callout={"rich_text": plain_text(
    f"{len(snap['piliers']['creation']['roadmap'])} programmes séquencés · Gantt · Actifs + Planifiés"
)})

# Création achievements callout title
client.blocks.update(block_id="e5a9fc8d", callout={"rich_text": plain_text(
    "1 chantier actif — ML P0 micrograd from scratch (paliers en cours)"
)})


# ─────────────────────────────────────────────────────────────
# PHASE 3 — REPLACE LIVE-TODO journal paragraphs with TODO callout
# ─────────────────────────────────────────────────────────────

# The LIVE-TODO paragraph at end of Journal section is already deleted in Phase 1.
# Append a TODO callout to each Journal section's parent block.

# Parent block IDs for Journal sections (heading_2 siblings):
JOURNAL_SECTION_PARENTS = {
    "interieur": "348845e8-e836-8179-9cbe-f8940b5d1195",   # page itself
    "famille":   "348845e8-e836-818d-96ba-da79b2fcfb03",
    "pro_fi":    "348845e8-e836-81b0-aaf7-e3b81b92416c",
    "creation":  "348845e8-e836-8119-8920-f14c27aa5f30",
    "spirituel": "348845e8-e836-8133-a818-ea7de5c6b17e",
}

# NOTE: append after the divider that follows the Journal heading.
# Strategy: use blocks.children.append on each page, placing after last fake journal callout position.
# In practice: since we deleted all fake callouts and LIVE-TODO, append to page root —
# the callout will appear at end of page (before Resources section).
# Better approach: insert after specific block using "after" param in append if API supports it
# (Notion API v2022-06-28 does NOT support after param — always appends at end).
# Recommended workaround: manually drag in Notion UI, or use positional block creation via
# a two-step: append new callout, then note its ID for manual reorder.

TODO_CALLOUT_BLOCK = {
    "object": "block",
    "type": "callout",
    "callout": {
        "rich_text": [{"type": "text", "text": {"content": "DB Journal à venir — Phase B"}}],
        "icon": {"type": "emoji", "emoji": "📋"},
        "color": "gray_background"
    }
}
# This will be appended after deleting the LIVE-TODO paragraph.
# For now the deletion in Phase 1 leaves a gap — Phase B will fill it.
```

---

## Notes on execution order

1. Run Phase 1 first (deletions are safe and idempotent).
2. Run Phase 2 (updates) immediately after.
3. Phase 3 (journal TODO callout) requires manual reorder in Notion UI after appending — OR skip and add during DB Journal Phase B build.
4. The Intérieur "Séance du jour" toggle (79e1db7b) and "Split de la semaine" toggle (24e3c72e) contain detailed workout programs + fake history — these are borderline (functional content vs fake). The fake "Historique récent" bullets (d195ba88, 551c2466, e367fc51, 65f0d0ee, c639d5bb) inside the split toggle are listed for deletion above. The workout program itself (exercices, series, poids) is plausible and not dated — classify as KEEP for now.
5. The "Séquençage détaillé" toggles contain hardcoded tables of program names/dates/progress. These are structural placeholders — recommend replacing toggle content with linked DB view in Phase B, but do NOT delete the toggle wrapper itself.
