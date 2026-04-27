# PRD — Life OS clean, dynamique et utilisable

Date : 2026-04-27  
Produit : Notion Life OS + repo `life_os` + pipeline GitHub Pages  
Statut : Draft de cadrage équipe

## 1. Contexte

Le système actuel contient une base solide : Notion comme source de vérité, `life_os` pour transformer les données, GitHub Pages pour publier des embeds HTML, et GitHub Actions pour synchroniser.

Mais l'expérience visible n'est pas encore fiable pour un usage quotidien. Plusieurs pages affichent encore des éléments de prototype : `W16`, dates figées, `LIVE-TODO`, `DB Journal à venir`, `TODO`, `Source manquante`, ou des sections futures non alimentées.

L'objectif n'est pas de faire une version plus ambitieuse. L'objectif est de rendre le système simple, propre, dynamique, et utilisable maintenant.

## 2. Objectif produit

Créer une version Life OS qui respecte quatre principes :

1. Une seule page quotidienne utile, simple, ouverte tous les jours.
2. Zéro placeholder visible dans les pages actives.
3. Toutes les informations visibles viennent d'une base Notion ou d'un calcul `life_os`.
4. Le pipeline ne casse pas quand une tâche, une semaine, une page ou une data source change.

## 3. Utilisateur cible

Utilisateur principal : Anthonny.

Besoins immédiats :

- Voir les tâches réelles du jour et de la semaine.
- Suivre finance, workout et objectif personnel sans ouvrir tout le système.
- Cocher les habitudes et actions réellement présentes dans les bases.
- Avoir une page simple, pas une page décorative.
- Garder la version high-end comme projet secondaire, sans bloquer l'usage quotidien.

## 4. Non-objectifs

Cette phase ne doit pas :

- Refaire tout le Life OS high-end.
- Ajouter de nouveaux graphes complexes.
- Créer de nouvelles bases si une base existante peut couvrir le besoin.
- Exposer des éléments “à venir” dans les pages actives.
- Construire une page jolie mais statique.
- Garder plusieurs cockpits concurrents visibles.

## 5. Équipe recommandée — 6 personnes

| Rôle | Responsabilité principale | Profil attendu |
|---|---|---|
| Product Owner / Life OS Lead | Arbitrer le scope, valider ce qui est utile au quotidien, prioriser finance/workout/objectifs | Comprend les objectifs personnels, tranche vite, refuse le superflu |
| Notion Architect | Nettoyer les pages, vues, bases, relations, filtres, archives, cockpit actif | Expert Notion, bases liées, vues filtrées, UX Notion native |
| Data Pipeline Engineer | Stabiliser `fetch -> transform -> build -> verify`, enlever hardcodes, rendre les checks dynamiques | Python, Notion API, GitHub Actions |
| Frontend Embed Engineer | Nettoyer les templates HTML, retirer placeholders visibles, rendre les embeds robustes et lisibles | HTML/CSS/JS, Jinja, visualisation simple |
| QA / Release Engineer | Vérifier Notion + HTML + GitHub Pages, écrire tests, checklists, critères de non-régression | CI, smoke tests, validation visuelle, rigueur |
| UX Systems Designer | Définir l'expérience quotidienne minimaliste, hiérarchie d'information, règles d'affichage | UX produit, dashboards opérationnels, simplicité radicale |

## 6. Scope fonctionnel

### 6.1 Cockpit quotidien unique

Créer une seule page active, nommée par exemple :

`Life OS — Today`

Elle doit contenir uniquement :

- Tâches du jour venant de `Plan d'exécution`.
- Tâches de la semaine venant de `Plan d'exécution`.
- Habitudes de la semaine venant de `Habitudes`.
- Finance du mois venant de `Finance mensuelle`, `Lignes budget mensuel`, transactions si utile.
- Workout du jour venant de la base sport ou d'une structure fiable.
- Objectifs actifs venant des achievements/sous-achievements.
- Un lien discret vers le backlog, pas une vue massive.

### 6.2 Pages piliers

Les pages piliers restent disponibles, mais elles ne doivent afficher que des sections alimentées.

Règle :

- Si la donnée existe : afficher la vue ou l'embed.
- Si la donnée n'existe pas : masquer la section ou la déplacer en backlog.
- Ne jamais afficher `TODO`, `Source manquante`, `DB à brancher`, `à venir` comme contenu utilisateur.

### 6.3 Pro & Financier

Priorité haute.

Doit afficher :

- Budget mensuel actif.
- Lignes budget mensuel.
- Transactions Anthonny.
- Transactions Mirane.
- Journal finance réel.
- Tâches finance de la semaine.

Doit corriger :

- Page transactions dédiée marquée `deleted`.
- Liens vers anciennes bases supprimées.
- Mentions W16 ou date figée.

### 6.4 Workout

Doit afficher le workout lié au jour :

- Lundi et jeudi : Séance A Upper.
- Mardi et vendredi : Séance B Lower.
- Mercredi : récupération.
- Samedi : récupération ou rattrapage.
- Dimanche : reset.

La table d'exercices peut rester proche du format donné par Anthonny, mais elle ne doit pas être une checklist quotidienne à recopier.

### 6.5 Repo et pipeline

Le repo doit :

- Calculer la semaine/date actuelle dynamiquement.
- Ne plus dépendre de `W16`.
- Ne plus vérifier des noms précis de tâches dans `verify_build.py`.
- Centraliser les IDs Notion.
- Échouer clairement si une data source critique manque.
- Ne pas masquer les erreurs de template.
- Générer uniquement des pages actives utiles, ou marquer les pages legacy hors interface active.

## 7. Requirements détaillés

| ID | Requirement | Priorité | Owner |
|---|---|---|---|
| R1 | Une seule page cockpit active est visible depuis `Life OS` | P0 | Notion Architect |
| R2 | Les anciennes pages cockpit sont déplacées/renommées en legacy | P0 | Notion Architect |
| R3 | Aucune page active ne contient `LIVE-TODO`, `DB Journal à venir`, `Source manquante`, `TODO` visible | P0 | QA |
| R4 | La page transactions dédiée est restaurée ou recréée avec les nouvelles bases | P0 | Notion Architect |
| R5 | `PAGE_TRANSACTIONS_REAL` pointe vers une page existante non supprimée | P0 | Data Pipeline Engineer |
| R6 | `verify_build.py` utilise les données de `snapshots.json`, pas des noms hardcodés | P0 | Data Pipeline Engineer |
| R7 | Les defaults `W16` / `2026-04-19` sont remplacés par un calcul dynamique Europe/Paris | P0 | Data Pipeline Engineer |
| R8 | Les templates W16 sont renommés dynamiquement ou déplacés en legacy | P1 | Frontend Embed Engineer |
| R9 | `build_html.py` échoue si un template attendu casse | P1 | Data Pipeline Engineer |
| R10 | Les embeds qui n'ont pas de donnée réelle sont retirés des pages actives | P1 | Frontend Embed Engineer + Notion Architect |
| R11 | Les IDs Notion sont centralisés dans une config unique | P1 | Data Pipeline Engineer |
| R12 | L'import transactions accepte un CSV en argument/env et fait un upsert | P1 | Data Pipeline Engineer |
| R13 | Les vues Notion du cockpit sont filtrées : aujourd'hui, semaine, actifs, finance active | P0 | Notion Architect |
| R14 | La QA valide Notion + local HTML + GitHub Pages après chaque phase | P0 | QA |

## 8. Critères d'acceptation

Une version est acceptée seulement si :

- Le cockpit actif peut être ouvert chaque jour sans modifier du texte à la main.
- Toutes les tâches visibles viennent de `Plan d'exécution`.
- Toutes les habitudes visibles viennent de `Habitudes`.
- La finance visible vient des bases finance/transactions.
- Aucun placeholder utilisateur n'est visible.
- Aucun texte `W16` ne reste dans les pages actives, sauf archive explicitement nommée.
- `transform -> build_html -> verify_build` passe localement.
- GitHub Actions passe.
- Les pages GitHub Pages affichent les mêmes valeurs que les snapshots.
- La page Notion `Transactions réelles par compte` n'est plus supprimée ou n'est plus référencée.

## 9. Plan de delivery

### Phase 0 — Freeze et inventaire

Durée cible : 0,5 jour

- Identifier les pages actives.
- Identifier les pages legacy.
- Lister tous les embeds visibles.
- Lister toutes les bases réellement utilisées.
- Définir le cockpit unique cible.

Livrable : inventory Notion + map pages/bases/embeds.

### Phase 1 — Stopper les régressions

Durée cible : 1 jour

- Fix `verify_build.py` dynamique.
- Fix dates/semaine dynamiques dans `transform.py`.
- Fail hard dans `build_html.py`.
- Centraliser les IDs critiques.
- Ajouter une vérification de page transactions non supprimée.

Livrable : pipeline qui ne casse pas sur changement de contenu Notion.

### Phase 2 — Nettoyage Notion actif

Durée cible : 1 à 2 jours

- Nettoyer `Life OS`.
- Choisir une seule page cockpit.
- Archiver/renommer les cockpits anciens.
- Supprimer ou masquer les sections non alimentées.
- Corriger transactions réelles par compte.
- Retirer `DB Journal à venir` et `LIVE-TODO`.

Livrable : pages actives sans placeholder visible.

### Phase 3 — Cockpit quotidien utilisable

Durée cible : 1 à 2 jours

- Construire la page quotidienne avec vues filtrées.
- Ajouter tâches du jour/semaine.
- Ajouter habitudes semaine.
- Ajouter finance active.
- Ajouter workout du jour.
- Ajouter objectifs actifs.
- Ajouter reset hebdo simple.

Livrable : page utilisable tous les matins et tous les soirs.

### Phase 4 — QA et release

Durée cible : 0,5 à 1 jour

- Vérifier les pages Notion.
- Vérifier les HTML locaux.
- Vérifier GitHub Pages.
- Vérifier workflow GitHub.
- Capturer screenshots avant/après.
- Produire rapport de release.

Livrable : release validée, screenshots, checklist.

## 10. Définition de Done

La tâche est terminée quand :

- Le cockpit quotidien est le seul point d'entrée recommandé.
- Les pages actives ne montrent aucun placeholder.
- Les bases actuelles sont bien connectées.
- Les anciennes pages ne polluent plus la navigation.
- Le pipeline local et distant passe.
- Le rapport QA liste zéro blocker.

## 11. Risques

| Risque | Impact | Mitigation |
|---|---|---|
| Trop vouloir garder la version high-end visible | Interface confuse | Masquer tout ce qui n'est pas alimenté |
| Renommer des pages/blocs Notion casse les scripts | Sync instable | Utiliser IDs/config centralisée |
| Supprimer une page encore référencée | Liens cassés | Inventaire avant modification |
| Données insuffisantes pour certains graphes | Placeholders visibles | Retirer les graphes jusqu'à données réelles |
| Scope creep design | Retard et frustration | Priorité à l'usage quotidien |

## 12. Backlog post-MVP

- Time Tracker réel.
- Mesures corps.
- DB Personnes / Famille.
- Rapports prédication.
- Journal commun multi-pilier.
- Visual QA automatisée avec screenshots.
- Version high-end Life OS V8 propre.
- Tests unitaires et fixtures Notion.
- Import transactions upsert complet.

## 13. Décision produit recommandée

La priorité absolue est de rendre invisible tout ce qui n'est pas prêt. Une page simple avec 6 vues fiables vaut mieux que 20 sections ambitieuses avec `TODO`.

La version high-end doit devenir une tâche dans le système, pas le système lui-même.
