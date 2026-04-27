# Plan de nettoyage Notion / cockpit — 2026-04-27

## Cadre

Ce document est un plan d'execution manuel pour nettoyer Notion sans mutation automatique.

Sources utilisees :

- `AUDIT_REPO_2026-04-27.md`
- `AUDIT_V22.md`
- `AUDIT_PASS8.md`
- `PRD_LIFE_OS_CLEANUP_2026-04-27.md`

Hors scope de ce plan :

- Ecriture dans Notion.
- Modification des scripts, templates, donnees ou README.
- Execution de `scripts/cleanup_v22.py` ou de scripts de sync Notion.

Objectif de sortie :

- Une seule page cockpit quotidienne active.
- Aucune page active avec `W16`, `LIVE-TODO`, `CHART-TODO`, `DB Journal à venir`, `TODO`, `Source manquante`, `à venir` ou page `deleted` referencee.
- Toutes les sections visibles sont branchees sur des vues Notion dynamiques ou sur des embeds deja alimentes.

## Etat cible

### Navigation active

La page racine `Life OS` doit devenir un hub court :

- Lien principal vers le cockpit quotidien cible.
- Liens secondaires vers les 5 pages piliers nettoyees.
- Lien vers `Pro & Financier`.
- Lien vers la nouvelle page `Transactions réelles par compte` si elle est recreee.
- Lien discret vers `Backlog / Legacy`, pas vers les anciens cockpits.

La racine ne doit plus contenir :

- Date figée `Vendredi 19 avril 2026`.
- Semaine `W16`.
- Mentions `LIVE-TODO Phase B`.
- Cartes KPI statiques non branchees.
- Plusieurs liens concurrents vers des cockpits.

### Cockpit quotidien cible

Une seule page doit etre designee comme cockpit actif, idealement `Life OS — Today`.

Le cockpit doit contenir uniquement des vues dynamiques :

| Section | Source | Filtre minimum | Affichage cible |
|---|---|---|---|
| Taches du jour | `Plan d'exécution` | `Type = Tâche atomique`, `Date prévue = aujourd'hui`, statut non archive | Vue liste compacte, groupee par pilier ou statut |
| Taches de la semaine | `Plan d'exécution` | `Type = Tâche atomique`, `Date prévue` dans la semaine courante, statut non archive | Vue table/liste avec date, pilier, statut |
| Habitudes | `Habitudes` | semaine courante ou derniere semaine disponible, habitudes actives | Vue table compacte avec fait/cible/progression |
| Finance | `Finance mensuelle`, `Lignes budget mensuel`, transactions | mois actif, comptes actifs | Budget actif, lignes budget, transactions recentes par compte |
| Workout | base sport existante ou vue fiable de `Plan d'exécution` | jour courant, pilier `Intérieur`, type workout | Seance du jour uniquement, sans historique fake |
| Objectifs actifs | achievements / sous-achievements dans `Plan d'exécution` | statut actif/en cours, non archive | Vue compacte par pilier, progression si sourcee |

Regles du cockpit :

- Pas de checklist statique a recopier.
- Pas de champ `...`.
- Pas d'embed avec placeholder.
- Pas de roadmap future visible.
- Pas de journal futur non branche.
- Les vues doivent rester valides quand la date et la semaine changent.

## Pages a garder actives

| Page | Decision | Actions |
|---|---|---|
| `Life OS` | Garder comme hub | Reduire a navigation propre, supprimer W16/date figée/placeholders, ne garder qu'un lien cockpit actif |
| `Life OS — Today` | Garder ou convertir en cockpit actif | Remplacer les checklists et champs manuels par les vues dynamiques listees ci-dessus |
| `Pro & Financier` | Garder actif, priorite haute | Retirer W16, texte time tracker non connecte si visible, lien vers page transactions deleted, placeholders journal/time tracker |
| `Intérieur` | Garder actif apres nettoyage | Garder workout structurel si utile, supprimer fake historique, W16, journal non branche, placeholders mesures corps |
| `Famille` | Garder actif apres nettoyage | Garder vues alimentees, supprimer date-night fake, journal fake, W16, sections `à venir` |
| `Création` | Garder actif apres nettoyage | Garder objectifs actifs reels, corriger count actif, supprimer roadmaps/counts stale et journal fake |
| `Spirituel` | Garder actif apres nettoyage | Garder habitudes/objectifs reels, supprimer heures predication fake, embeds source manquante, journal fake |
| Nouvelle `Transactions réelles par compte` | Recréer | Page non deleted avec embeds/vues transactions Anthonny + Mirane et liens depuis `Pro & Financier` |

## Pages a archiver ou retirer de la navigation active

| Page | Decision | Raison | Action manuelle |
|---|---|---|---|
| `Life OS — Cockpit utile (ancienne)` | Archiver | Ancien cockpit brut, doublon | Renommer `Archive — Life OS — Cockpit utile (ancienne)` et retirer de la racine |
| `Life OS — Daily Cockpit` incomplet | Archiver ou convertir | Mentionne Habitudes W17 alors que la periode courante est W18 dans l'audit ; pas cockpit final | Si non choisi comme cockpit cible, renommer `Archive — Life OS — Daily Cockpit` |
| Autre `Life OS — Daily Cockpit` | Archiver | Doublon compose de vues DB brutes | Renommer `Archive — ...` et retirer des liens |
| `Today` manuel | Convertir ou archiver | Utilisable mais trop manuel, champs `...`, checklists statiques | Soit l'utiliser comme base du cockpit dynamique, soit l'archiver apres creation de `Life OS — Today` |
| `Dashboard` | Sortir de la navigation quotidienne | Page pas propre : W16, placeholders, KPI stale, roadmap `à venir` | Garder seulement comme page analytics apres nettoyage complet, sinon renommer `Archive — Dashboard V8` |
| Ancienne `Transactions réelles par compte` deleted | Ne pas reutiliser | API Notion la marque `deleted` et elle pointe vers anciennes bases | Creer une nouvelle page ; ne laisser aucun lien vers l'ancienne |

## Nettoyage par page

### `Life OS`

Actions P0 :

- Supprimer la ligne/date figée `Vendredi 19 avril 2026 · W16`.
- Supprimer toutes les mentions `LIVE-TODO Phase B`.
- Retirer les liens vers les cockpits archives.
- Remplacer les cartes statiques par des liens courts ou des vues dynamiques si elles sont vraiment utiles.
- Verifier qu'aucun embed visible ne contient `TODO`, `Source manquante`, `à venir`.

### `Dashboard`

Decision recommandee : ne pas garder comme entree quotidienne tant que la page n'est pas nettoyee.

Actions si la page reste active :

- Supprimer les annotations `LIVE-TODO` identifiees dans `AUDIT_V22.md`.
- Mettre a jour les KPI stale avec les valeurs sourcees, ou retirer les KPI non fiables :
  - achievements actifs : `9`, pas `10`.
  - progression piliers : `Intérieur 15 %`, les autres `0 %` selon l'audit V2.2.
  - roadmap Création : `15`, pas `7`.
- Retirer les sections roadmap/embeds qui affichent `à venir`.
- Retirer ou masquer `area-t2`, `stacked-w16`, `radar` tant qu'ils affichent W16/placeholders.

### `Intérieur`

Actions P0 :

- Supprimer `W16` et toute date figée.
- Garder uniquement le workout du jour s'il est utile, sans historique fake.
- Supprimer les faux historiques :
  - bullets `Historique récent`.
  - callouts journal dates avril 2026.
- Retirer les placeholders mesures corps / poids tant que la DB `Mesures corps` n'existe pas.
- Retirer `DB Journal à venir` de la page active.
- Remplacer les vues Habitudes filtrees `Semaine = W16` par semaine courante / derniere semaine disponible.

### `Famille`

Actions P0 :

- Supprimer `W16`, `LIVE-TODO`, `CHART-TODO`.
- Supprimer date-night et evenements hardcodes sans DB source.
- Supprimer les callouts journal fake.
- Retirer `DB Journal à venir`.
- Garder les habitudes et objectifs seulement si les vues sont filtrees dynamiquement.

### `Pro & Financier`

Actions P0 :

- Supprimer `W16` dans l'intro.
- Supprimer le lien vers l'ancienne page `Transactions réelles par compte` deleted.
- Creer un lien vers la nouvelle page transactions non deleted.
- Retirer le texte indiquant que le time tracker n'est pas connecte si la section est visible comme KPI.
- Supprimer la metrique patrimoine `47 200 €` et delta associe si aucune DB `Comptes` ne l'alimente.
- Supprimer journal fake et `DB Journal à venir`.
- Garder uniquement :
  - Budget mensuel actif.
  - Lignes budget mensuel.
  - Transactions Anthonny.
  - Transactions Mirane.
  - Taches finance de la semaine.
  - Journal finance reel si `Journal Pro & Financier` est vraiment alimente.

### `Création`

Actions P0 :

- Corriger `2 / 2` en etat source, ou retirer si non dynamique.
- Corriger roadmap `7 programmes` vers `15` si la section reste visible, sinon masquer la roadmap.
- Supprimer `W16`, `LIVE-TODO`, `CHART-TODO`.
- Supprimer tous les faux journaux avril 2026.
- Retirer `DB Journal à venir`.
- Ne garder que les objectifs et sous-objectifs actifs venant de la source.

### `Spirituel`

Actions P0 :

- Supprimer `W16`, `LIVE-TODO`, `CHART-TODO`.
- Supprimer heures predication hardcodees `24 h / 30 h` tant que la DB/source n'existe pas.
- Supprimer les embeds livre/predication qui affichent `TODO` ou `Source manquante`.
- Supprimer les faux journaux avril 2026.
- Retirer `DB Journal à venir`.

## Sections et embeds a retirer des pages actives

Retirer ou masquer tant que les donnees ne sont pas alimentees :

| Element | Raison |
|---|---|
| `radar.html` | Affiche `Radar équilibre 5 piliers — à venir`, cible pilier manquante |
| `sankey-week.html` | DB Time Tracker manquante |
| `area-t2.html` | Historique insuffisant et message W16 |
| `stacked-w16.html` | W16 figé, aucune tache completee W16 |
| `line-poids-interieur.html` | Mesures corps non branchees |
| `tree-family-famille.html` | DB Personnes non branchee |
| `book-progression-spirituel.html` | Progression livre non branchee |
| `line-predication-spirituel.html` | Rapports predication non branches |
| `journal-pilier-*` | Journal pilier non branche |
| `kpi-interieur-signature.html` | `DB Mesures corps à brancher` |
| `kpi-famille-signature.html` | `DB Couple à brancher` |
| `kpi-spirituel-signature.html` | `DB Rapports prédication à brancher` |
| `heatmap-habits-*` | Libelles W16 / semaines historiques artificielles |
| `sankey-pilier-*` | Fallback `données à venir` possible |

Embeds finance a garder si les pages chargees ne contiennent pas de placeholder :

- `sankey-revenu-profi.html`
- `treemap-depenses-profi.html`
- `treemap-transactions-account-anthonny.html`
- `treemap-transactions-account-mirane.html`
- `history-transactions-account-anthonny.html`
- `history-transactions-account-mirane.html`

## Liens casses et page transactions

### Page `Transactions réelles par compte`

Etat audite :

- Page marquee `deleted` par l'API Notion.
- Elle reference d'anciennes bases transactions supprimees.
- `Pro & Financier` contient encore un lien vers cette page.

Plan manuel :

1. Creer une nouvelle page Notion `Transactions réelles par compte`.
2. Ajouter une section `Anthonny` :
   - vue transactions compte Anthonny ;
   - embed treemap Anthonny ;
   - embed historique Anthonny.
3. Ajouter une section `Mirane` :
   - vue transactions compte Mirane ;
   - embed treemap Mirane ;
   - embed historique Mirane.
4. Ajouter une section `Controle` :
   - mois actif ;
   - derniere date importee ;
   - nombre de transactions par compte ;
   - lien vers budget mensuel actif.
5. Remplacer le lien dans `Pro & Financier` par la nouvelle page.
6. Retirer toute reference a l'ancienne page deleted.
7. Apres validation, mettre a jour la config/env du repo dans une tache separee, hors present write set.

### Autres liens casses identifies

Dans l'audit embeds, `index.html` contient trois liens brises avec `pro_fi` au lieu de `pro-fi` :

- `sankey-pilier-pro_fi.html`
- `heatmap-habits-pro_fi.html`
- `tree-deps-pro_fi.html`

Action Notion :

- Ne pas exposer l'index embeds comme navigation utilisateur tant que ces liens ne sont pas corriges dans le repo.
- Si un lien Notion pointe directement vers une URL `pro_fi`, le remplacer par la version `pro-fi`.

## Ordre d'execution recommande

### Phase 1 — Freeze navigation

- Choisir la page cockpit cible.
- Retirer de `Life OS` tous les liens vers les cockpits non retenus.
- Renommer les anciens cockpits avec prefixe `Archive —`.
- Ne rien supprimer definitivement avant QA.

### Phase 2 — Nettoyage P0 des pages actives

- Nettoyer `Life OS`.
- Nettoyer le cockpit cible.
- Nettoyer `Pro & Financier`.
- Recréer `Transactions réelles par compte`.
- Retirer tous les embeds/sections placeholder des pages actives.

### Phase 3 — Nettoyage des piliers

- Nettoyer `Intérieur`, `Famille`, `Création`, `Spirituel`.
- Remplacer les filtres `W16` par filtres dynamiques.
- Supprimer faux journaux, historiques fake, metriques sans source.

### Phase 4 — QA et release Notion

- Executer la checklist QA ci-dessous.
- Capturer les pages actives avant/apres.
- Documenter les pages archivees.
- Ouvrir le cockpit le lendemain pour verifier que les vues dynamiques suivent la date.

## Checklist QA Notion apres modifications

### Navigation

- [ ] `Life OS` contient un seul lien cockpit principal.
- [ ] Aucun ancien cockpit n'est visible depuis la navigation active.
- [ ] Les pages archivees ont un prefixe explicite `Archive —`.
- [ ] `Pro & Financier` pointe vers une page transactions non deleted.
- [ ] Aucun lien utilisateur ne pointe vers une URL ou page Notion deleted.

### Cockpit quotidien

- [ ] Taches du jour chargees depuis `Plan d'exécution`.
- [ ] Taches de la semaine chargees depuis `Plan d'exécution`.
- [ ] Habitudes chargees depuis `Habitudes`.
- [ ] Finance chargee depuis les bases finance/transactions.
- [ ] Workout du jour vient d'une source dynamique ou d'une vue fiable.
- [ ] Objectifs actifs viennent des achievements/sous-achievements.
- [ ] Aucune checklist statique n'est necessaire pour l'usage quotidien.

### Pages actives

- [ ] Recherche Notion sur les pages actives : aucun `W16`.
- [ ] Recherche Notion sur les pages actives : aucun `LIVE-TODO`.
- [ ] Recherche Notion sur les pages actives : aucun `CHART-TODO`.
- [ ] Recherche Notion sur les pages actives : aucun `DB Journal à venir`.
- [ ] Recherche Notion sur les pages actives : aucun `Source manquante`.
- [ ] Recherche Notion sur les pages actives : aucun `TODO` visible utilisateur.
- [ ] Recherche Notion sur les pages actives : aucun `à venir` visible utilisateur sauf dans un backlog explicitement archive.
- [ ] Aucun KPI visible n'a une valeur hardcodee non sourcee.
- [ ] Aucun faux historique ou faux journal avril 2026 ne reste visible.

### Embeds

- [ ] Chaque embed visible charge sans placeholder.
- [ ] Aucun embed visible n'affiche `TODO`, `Source manquante`, `Aucune donnée`, `données non saisies`, `DB ... à brancher`.
- [ ] Les embeds finance Anthonny et Mirane s'affichent.
- [ ] Les embeds W16 sont absents des pages actives.
- [ ] Les iframes ne servent pas de source principale quand une vue Notion dynamique suffit.

### Transactions

- [ ] La nouvelle page `Transactions réelles par compte` existe et n'est pas deleted.
- [ ] Section Anthonny presente.
- [ ] Section Mirane presente.
- [ ] Les transactions recentes sont visibles par compte.
- [ ] Le mois actif finance est identifiable.
- [ ] L'ancienne page deleted n'est referencee nulle part dans les pages actives.

## Strategie de non-regression

### Regles d'interface

- Toute page active doit etre utilisable sans texte de promesse future.
- Une section sans source reelle est archivee ou supprimee de la page active.
- Une page archivee doit etre clairement nommee `Archive — ...`.
- Un embed avec placeholder ne doit jamais etre expose dans le cockpit.
- Un KPI visible doit etre soit dynamique, soit retire.

### Recherches obligatoires avant release

Dans Notion, lancer ces recherches sur les pages actives :

- `W16`
- `LIVE-TODO`
- `CHART-TODO`
- `DB Journal à venir`
- `TODO`
- `Source manquante`
- `à venir`
- `deleted`

Critere d'acceptation :

- Zero resultat dans les pages actives.
- Les seuls resultats toleres doivent etre dans des pages `Archive — ...` ou dans un backlog explicitement non quotidien.

### Controle des liens

- Ouvrir chaque lien depuis `Life OS`.
- Ouvrir chaque lien depuis le cockpit cible.
- Ouvrir chaque lien depuis `Pro & Financier`.
- Confirmer qu'aucun lien n'ouvre une page Notion supprimee.
- Confirmer que la page transactions cible n'est pas l'ancienne page deleted.

### Controle dynamique

- Changer la vue cockpit sur demain/semaine suivante quand possible, ou attendre le lendemain.
- Verifier que les filtres date/semaine suivent automatiquement.
- Verifier que les vues ne referencent pas `W16`, `W17`, `W18` en dur.
- Verifier que les taches cochees dans `Plan d'exécution` disparaissent ou changent de statut dans le cockpit.
- Verifier que les habitudes modifiees dans `Habitudes` se refletent dans la vue cockpit.

## Definition of Done

Le nettoyage Notion est pret quand :

- `Life OS` a une navigation simple et non concurrente.
- Le cockpit quotidien cible est la seule page d'usage quotidien.
- Les pages actives n'affichent aucun placeholder.
- Aucun `W16` actif ne reste visible.
- Aucune page `deleted` n'est referencee.
- `Transactions réelles par compte` existe comme nouvelle page non deleted ou n'est plus referencee.
- Les anciennes pages cockpit sont archivees.
- Les pages piliers ne contiennent que des sections alimentees ou utiles.
- La checklist QA est cochee sans exception bloquante.
