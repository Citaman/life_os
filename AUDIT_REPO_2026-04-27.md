# Audit repo life_os — 2026-04-27

## Résumé exécutif

Le repo est opérationnel après la correction du workflow du 2026-04-27 : le pipeline local `transform -> build_html -> verify_build` passe, et le dernier workflow GitHub Actions lié au correctif est passé au vert.

Mais le repo n'est pas encore au niveau "professionnel robuste / vraiment dynamique" que tu veux. Il reste une couche historique importante autour de `W16`, d'avril 2026, de pages Notion et de data sources codées en dur. Le risque principal n'est pas que tout soit cassé aujourd'hui ; le risque est que ça recasse dès que tu changes les semaines, les noms de tâches, les data sources, les fichiers CSV ou la structure Notion.

## Vérifications effectuées

Commandes exécutées :

```bash
.venv/bin/python -m compileall -q scripts
CURRENT_WEEK=W18 CURRENT_TRIMESTER='T2 2026' CURRENT_DATE=2026-04-27 .venv/bin/python scripts/transform.py
CURRENT_WEEK=W18 CURRENT_TRIMESTER='T2 2026' CURRENT_DATE=2026-04-27 .venv/bin/python scripts/build_html.py
CURRENT_WEEK=W18 CURRENT_TRIMESTER='T2 2026' CURRENT_DATE=2026-04-27 .venv/bin/python scripts/verify_build.py
```

Résultat :

- Compilation Python : OK
- Transform : OK
- Build HTML : OK, 84 pages générées
- Verify : OK
- Données vues localement : 1391 pages plan, 9 habitudes, 316 backlog, 1 mois finance, 17 lignes budget, 3 entrées journal, 701 transactions Anthonny, 205 transactions Mirane

## Findings prioritaires

| Priorité | Sujet | Impact | Preuve | Correction recommandée |
|---|---|---|---|---|
| P1 | `verify_build.py` vérifie encore du contenu précis de ta base Notion | Le workflow peut retomber en échec dès qu'une tâche, un achievement ou une entrée journal change de nom | `scripts/verify_build.py:162`, `scripts/verify_build.py:168`, `scripts/verify_build.py:191`, `scripts/verify_build.py:199` | Remplacer tous les checks de texte fixe par des checks issus de `snapshots.json` |
| P1 | Le repo contient encore une logique `W16` et avril 2026 | Le système prétend être dynamique, mais plusieurs graphes restent bloqués sur une semaine passée | `scripts/transform.py:32`, `scripts/transform.py:34`, `scripts/transform.py:864`, `scripts/transform.py:866`, `templates/stacked_w16.html`, `templates/area_t2.html:141`, `templates/heatmap_habits.html:517` | Renommer/transformer en `current_week`, calculer les dates depuis `CURRENT_DATE`, supprimer les templates W16 ou les marquer legacy |
| P1 | Import transactions non portable et non dynamique | L'import dépend d'un chemin local absolu et d'un dossier mensuel fixe | `scripts/import_transactions_to_notion.py:34` | Passer le CSV par argument CLI ou env `TRANSACTIONS_CSV_PATH`, détecter le dernier export disponible, valider le schéma |
| P1 | Import transactions create-only | Si une catégorie ou sous-catégorie change dans le CSV, Notion ne se met pas à jour | `scripts/import_transactions_to_notion.py:110` à `scripts/import_transactions_to_notion.py:119` | Ajouter un mode upsert : create si absent, update si `Source clé` existe mais propriétés différentes |
| P1 | `build_html.py` avale des erreurs de template | Un template peut casser et le build continuer avec des pages manquantes ou obsolètes | `scripts/build_html.py:83`, `scripts/build_html.py:95`, `scripts/build_html.py:130`, `scripts/build_html.py:139` | Fail hard par défaut ; ne skipper que les templates explicitement optionnels |
| P1 | IDs Notion dispersés dans workflow et scripts | Changer une data source ou une page demande de chercher dans plusieurs fichiers | `.github/workflows/daily-sync.yml`, `scripts/fetch_notion.py:41`, `scripts/fetch_notion.py:42`, `scripts/sync_pro_fi_page.py:33`, `scripts/sync_transactions_page.py:31` | Créer une config unique versionnée, ex. `config/notion_sources.example.yml`, et valider les env au démarrage |
| P2 | `data/snapshots.json` est généré mais suivi par Git | Un rebuild local modifie le working tree ; un snapshot stale peut masquer un bug | `git ls-files` retourne `data/snapshots.json` | Retirer du tracking ou déplacer vers `data/fixtures/snapshots.sample.json` |
| P2 | `fetch_notion.py` n'a pas de retry/backoff | Une erreur réseau/Notion temporaire peut casser le workflow horaire | `scripts/fetch_notion.py:50` à `scripts/fetch_notion.py:67` | Ajouter retries exponentiels et erreurs contextualisées par data source |
| P2 | Extraction Notion sans validation de schéma | Si une propriété est renommée dans Notion, le code reçoit `None` en silence | `scripts/fetch_notion.py:70` à `scripts/fetch_notion.py:104` | Définir les propriétés attendues par DB et échouer avec message clair si une colonne critique manque |
| P2 | Calcul transactions fragile sur `Direction` et le signe | Une dépense positive ou une direction localisée peut être ignorée | `scripts/transform.py:567` à `scripts/transform.py:573` | Normaliser direction/sign au moment de l'import et vérifier les anomalies |
| P2 | Time budgets et certains KPI sont encore codés en dur | Les heures par pilier et certains labels ne viennent pas de Notion | `scripts/transform.py:44`, `scripts/transform.py:968`, `scripts/transform.py:986` | Créer une DB/config `Time Budget` ou retirer ces métriques tant que la source n'existe pas |
| P2 | Scripts de sync Notion sensibles aux titres de sections | Renommer un heading Notion peut faire échouer ou mal placer la sync | `scripts/sync_pro_fi_page.py`, `scripts/sync_transactions_page.py` | Utiliser des marqueurs stables ou une table de blocs cibles ; ajouter `--dry-run` |
| P3 | `.env.example` est daté W16 | Mauvais point de départ pour exécution locale | `.env.example:16` à `.env.example:18` | Remplacer par valeurs vides ou documenter que les scripts calculent par défaut |
| P3 | Pas de tests, pas de lint, pas de typing config | Le repo dépend d'un smoke test custom et de GitHub Actions | Absence de `tests/`, `pyproject.toml`, `ruff.toml`, `pytest.ini` | Ajouter `pytest`, `ruff`, config minimale et fixtures Notion anonymisées |
| P3 | Documentation mélangée entre état actuel et legacy | Le README parle encore de W16 comme artefact courant | `README.md:48` | Séparer docs actuelles, docs legacy, et scripts de migration |
| P3 | `rebuild_life_os.sh` modifie `.env` | Une commande de build change la configuration locale | `scripts/rebuild_life_os.sh` | Exporter les variables pour le process courant ou écrire `.env.local.generated` |
| P3 | `trigger_remote_sync.sh` peut récupérer le mauvais run | Race possible si deux runs démarrent proches | `scripts/trigger_remote_sync.sh` | Filtrer le run par SHA/createdAt ou afficher seulement le lien workflow |

## Points positifs

| Sujet | État |
|---|---|
| GitHub Actions | Le workflow principal est vert après correction du verify |
| Build local | `transform`, `build_html`, `verify_build` passent avec W18 |
| Données transactionnelles | Les deux comptes sont bien présents dans les snapshots |
| Secrets | `.env` n'est pas tracké |
| Pages générées | 84 pages HTML sont produites sans erreur runtime locale |
| Structure générale | Le découpage fetch / transform / build / verify est sain comme base |

## Risques concrets à court terme

1. Si tu renommes `Budget familial maîtrisé`, `Choisir + installer outil tracker budget` ou `Construction budget mai 2026`, le verify peut casser même si la page générée est correcte.
2. Si tu changes une data source transactions dans Notion et oublies un des endroits où l'ID est codé, le workflow peut recasser.
3. Si tu relances l'import transactions après avoir recatégorisé le CSV, les lignes Notion déjà présentes ne seront pas corrigées.
4. Les vues `area-t2`, `stacked-w16` et `heatmap_habits` donnent encore une lecture W16/historique artificielle, donc elles ne sont pas fiables comme vérité dynamique.
5. Une erreur de template peut être masquée par `build_html.py` au lieu de bloquer franchement le build.

## Plan de remise à niveau recommandé

### Phase 1 — Stabiliser le pipeline

Objectif : éviter les échecs inutiles GitHub Actions.

- Rendre `verify_build.py` 100% basé sur `snapshots.json`.
- Supprimer les textes Notion spécifiques des checks.
- Faire échouer `build_html.py` si un template attendu casse.
- Ajouter des messages d'erreur propres pour les env manquantes.
- Ajouter retry/backoff dans `fetch_notion.py`.

### Phase 2 — Enlever les hardcodes dangereux

Objectif : que la semaine, la date et les sources ne soient plus figées.

- Remplacer les defaults W16/2026-04-19 par un calcul Europe/Paris.
- Renommer `habits_w16` en `habits_week`.
- Remplacer `stacked_w16` par `tasks_current_week`.
- Transformer `stacked_w16.html` en template dynamique ou le déplacer en legacy.
- Mettre les IDs Notion dans une config unique validée au démarrage.
- Retirer `data/snapshots.json` du tracking ou le convertir en fixture.

### Phase 3 — Rendre les transactions fiables

Objectif : que les catégories et sous-catégories restent à jour.

- Passer le CSV en argument ou env.
- Valider les colonnes du CSV.
- Ajouter upsert Notion.
- Ajouter détection des anomalies : direction inconnue, dépense positive, revenu négatif, date invalide.
- Optionnel : ajouter un mode dry-run et un rapport d'import avant mutation Notion.

### Phase 4 — Standard pro

Objectif : rendre le repo maintenable.

- Ajouter `pyproject.toml`.
- Ajouter `ruff`.
- Ajouter `pytest`.
- Ajouter des fixtures JSON minimales pour `fetch/transform/verify`.
- Ajouter une CI qui lance compile, tests, build, verify.
- Séparer scripts actifs et scripts legacy/migration.

## Conclusion

Le repo marche maintenant, mais il est encore dans un état "prototype avancé avec dette historique". Le plus important n'est pas de refaire la page Notion maintenant ; c'est de solidifier la chaîne qui alimente tout. La première vraie passe doit supprimer les vérifications hardcodées et la logique W16, parce que ce sont les deux sources les plus probables de prochaines pannes.

## Vérification Notion visible

### Verdict

Les pages Notion ne montrent pas encore "tout proprement". Plusieurs pages affichent encore des mentions visibles de type `LIVE-TODO`, `DB Journal à venir`, `à venir`, `W16`, ou embarquent des HTML qui affichent `TODO` / `Source manquante`. Ce n'est donc pas encore conforme à l'objectif : pas de placeholder visible, pas de page en attente de données, pas de fausse promesse dynamique.

### Pages Notion inspectées

| Page | État | Problèmes visibles |
|---|---|---|
| `Life OS` | Pas propre | Date et semaine figées `Vendredi 19 avril 2026 · W16`, cartes piliers statiques, mentions `LIVE-TODO Phase B`, lien vers plusieurs cockpits concurrents |
| `Dashboard` | Pas propre | Date W16, section `Aperçu du jour` et progression T2 liées à des embeds qui contiennent encore des placeholders, texte `à venir` dans roadmap |
| `Intérieur` | Pas propre | Date W16, séance du jour figée vendredi 19 avril, `DB Journal à venir` en double, embeds qui peuvent afficher TODO/source manquante |
| `Famille` | Pas propre | Date W16, plusieurs `à venir`, `DB Journal à venir` en double, journal non réellement branché |
| `Pro & Financier` | Meilleur état, mais pas clean | W16 dans l'intro, texte indiquant que time tracker n'est pas connecté, lien vers page transactions dédiée supprimée |
| `Création` | Pas propre | W16, plusieurs programmes `à venir`, `DB Journal à venir` en double |
| `Spirituel` | Pas propre | W16, `à venir`, embeds livre/prédication affichent `TODO` / source manquante |
| `Today` | Utilisable mais trop manuel | Champs `...`, checklists statiques à recocher/réécrire, pas alimenté par les bases |
| `Life OS — Daily Cockpit` | Incomplet | Mentionne Habitudes W17 alors que le contexte actuel est W18, contient plusieurs vues DB visibles, pas encore le cockpit simple final |
| `Life OS — Cockpit utile (ancienne)` | Ancien / doublon | Page de vues DB brute, pas un cockpit final |
| `Life OS — Daily Cockpit` autre page | Ancien / doublon | Uniquement vues DB, pas de structure d'usage quotidienne |
| `Transactions réelles par compte` | Cassé | La page est marquée `deleted` par l'API Notion et pointe vers les anciennes bases transactions supprimées |

### Embeds HTML qui affichent encore des placeholders

Fichiers `dist/*.html` contenant encore des signaux visibles `TODO`, `Source manquante`, `DB ... à brancher`, `Aucune donnée`, `données non saisies`, ou `à venir` :

| Embed | Problème |
|---|---|
| `radar.html` | `Radar équilibre 5 piliers — à venir`, cible pilier manquante |
| `sankey-week.html` | DB Time Tracker manquante |
| `area-t2.html` | Historique habitudes insuffisant, message W16 |
| `stacked-w16.html` | W16 figé, aucune tâche complétée W16 |
| `line-poids-interieur.html` | Mesures corps non branchées |
| `tree-family-famille.html` | DB Personnes non branchée |
| `book-progression-spirituel.html` | Progression livre non branchée |
| `line-predication-spirituel.html` | Rapports prédication non branchés |
| `journal-pilier-interieur.html` | Journal pilier non branché |
| `journal-pilier-famille.html` | Journal pilier non branché |
| `journal-pilier-creation.html` | Journal pilier non branché |
| `journal-pilier-spirituel.html` | Journal pilier non branché |
| `kpi-interieur-signature.html` | `DB Mesures corps à brancher` |
| `kpi-famille-signature.html` | `DB Couple à brancher` |
| `kpi-spirituel-signature.html` | `DB Rapports prédication à brancher` |
| `heatmap-habits-*` | Semaines W13-W15 non saisies + libellés W16 figés |
| `sankey-pilier-*` | Message fallback `données à venir` possible côté JS |

Les embeds finance principaux `sankey-revenu-profi.html`, `treemap-depenses-profi.html`, `treemap-transactions-account-anthonny.html`, `treemap-transactions-account-mirane.html`, `history-transactions-account-anthonny.html`, `history-transactions-account-mirane.html` ne ressortent pas comme placeholders dans le scan local. Le problème finance visible est plutôt la page Notion dédiée transactions supprimée et les liens historiques.

### Priorités de correction Notion

| Priorité | Correction |
|---|---|
| P0 | Remplacer ou recréer la page `Transactions réelles par compte`, puis corriger `PAGE_TRANSACTIONS_REAL` et les liens dans `Pro & Financier` |
| P0 | Supprimer/masquer tous les embeds qui affichent `TODO` ou `Source manquante` tant que les données ne sont pas réellement disponibles |
| P0 | Nettoyer les pages principales de toutes les mentions `LIVE-TODO`, `DB Journal à venir`, `W16`, dates figées et textes de placeholder |
| P1 | Choisir une seule page cockpit active et mettre les autres en archive/legacy |
| P1 | Rebrancher les sections du cockpit sur des vues filtrées de bases existantes plutôt que checklists statiques |
| P1 | Remplacer les journaux non branchés par une vraie DB journal commune filtrée par pilier, ou retirer les sections |
| P2 | Ne garder dans Notion que les vues/embeds qui ont une donnée réelle aujourd'hui ; déplacer les ambitions futures dans un backlog |

### Conclusion Notion

Le repo génère une partie de données utiles, surtout sur Pro & Financier et les transactions réelles, mais l'expérience Notion globale n'est pas encore saine. Pour atteindre le niveau attendu, il faut arrêter d'exposer les pages et embeds "future state" dans l'interface quotidienne. La bonne approche est de rendre visible uniquement ce qui marche vraiment, et de déplacer tout le reste en backlog ou en archive.
