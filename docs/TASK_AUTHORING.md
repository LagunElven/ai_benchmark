# Guide de création des tâches de benchmark

## Objectif

Une tâche doit tester une capacité précise, tout en ressemblant suffisamment à une situation réelle pour être utile au choix d'un assistant d'entreprise.

## Une bonne tâche

Une bonne tâche :

- possède une vérité terrain ou un comportement attendu ;
- contient au moins un mécanisme de validation objective ;
- évite de donner involontairement la solution dans le prompt ;
- est reproductible ;
- ne dépend pas d'un service externe instable ;
- peut être exécutée dans un workspace propre ;
- produit des métriques exploitables ;
- teste une capacité clairement identifiée.

## Niveaux de difficulté

### Easy

- changement local ;
- 1 à 2 fichiers pertinents ;
- erreur relativement évidente ;
- peu ou pas de pièges de framework.

### Medium

- plusieurs fichiers ;
- compréhension du framework ;
- cas limites ;
- risque plausible de solution partielle.

### Hard

- architecture multi-couches ;
- concurrence, transactions ou event sourcing ;
- bug intermittent ;
- contexte important ;
- solution devant préserver plusieurs invariants.

## task.yaml — proposition initiale

```yaml
id: AXON-04
revision: 1
name: Ignore obsolete ProduitBaminet snapshots
category: axon
difficulty: medium

suites:
  - smoke
  - core
  - full

tags:
  - java
  - axon
  - upcaster
  - snapshot
  - repair

modes:
  - one-shot
  - repair

toolchain:
  language: java
  version: "21"
  requirements:
    - Maven 3.9+

runtime:
  internet: false
  max_iterations: 3
  timeout_seconds: 600
  max_output_tokens: 12000

workspace:
  source: workspace
  include:
    - source: public-tests
      target: public-tests

validation:
  public:
    - command: ["./mvnw", "-q", "test"]
  hidden:
    - command: ["./mvnw", "-q", "-Pbenchmark-hidden", "test"]

metrics:
  - pass_at_1
  - pass_at_3
  - tests_passed
  - tests_total
  - input_tokens
  - output_tokens
  - elapsed_seconds
  - files_modified
  - patch_lines_added
  - patch_lines_removed

metric_extractors: []
```

Ce format sera ajusté après implémentation des premiers cas.

## Prompt d'une tâche de développement

Le prompt doit expliquer :

1. le problème utilisateur ;
2. les contraintes fonctionnelles ;
3. ce qui peut être modifié ;
4. les commandes éventuellement autorisées ;
5. la définition fonctionnelle du succès sans divulguer les tests cachés.

Eviter :

- « utilise impérativement telle annotation » si le but est justement de voir si le modèle trouve la bonne stratégie ;
- les noms de tests cachés révélant les cas limites ;
- les commentaires `TODO` placés exactement à l'endroit du bug pour les tâches de diagnostic.

## Tests publics et cachés

### Publics

Ils peuvent servir à :

- vérifier que le projet fonctionne avant modification ;
- montrer le style des tests ;
- donner un feedback de réparation.

### Cachés

Ils doivent tester :

- cas limites ;
- régressions ;
- solutions naïves ;
- invariants non triviaux ;
- scénarios concurrents lorsque pertinent.

Les tests cachés ne doivent jamais exister dans l'espace accessible au modèle pendant son travail.

## Exemple Axon Upcaster

Scénario : événement revision 5.0 possédant `dateOuverture`; revision 5.1 introduit `datePremierVersement`.

Le modèle doit écrire/corriger un upcaster tel que :

- l'événement cible 5.0 soit converti vers 5.1 ;
- `datePremierVersement` soit initialisé depuis `dateOuverture` ;
- les autres événements ne soient pas modifiés ;
- les autres propriétés JSON soient préservées ;
- les valeurs null/absentes soient gérées selon la spécification de la tâche.

Les tests cachés peuvent couvrir :

- événement cible normal ;
- `dateOuverture = null` ;
- `dateOuverture` absente ;
- mauvais type d'événement ;
- mauvaise révision ;
- propriétés inconnues à préserver.

## Exemple Spring lost update

Scénario : deux traitements chargent la même entité. Un modifie un statut, l'autre un autre champ. Certaines interleavings font disparaître la première modification.

Le modèle doit diagnostiquer le problème et rendre le système robuste.

Validation cachée :

- exécuter plusieurs ordres/interleavings ;
- vérifier qu'aucune donnée n'est silencieusement perdue ;
- vérifier le comportement d'erreur/retry attendu ;
- empêcher une solution qui sérialise globalement toute l'application sauf si explicitement acceptable.

## Exemple long-context

Créer un projet avec un problème stable et plusieurs variantes ajoutant des fichiers non pertinents.

Les variantes doivent conserver :

- le même bug ;
- les mêmes fichiers réellement nécessaires ;
- la même solution logique.

Elles modifient uniquement la quantité de contexte parasite et éventuellement la profondeur des relations entre classes.

Mesurer :

- réussite ;
- fichiers pertinents trouvés ;
- fichiers inutiles modifiés ;
- taille du patch ;
- tokens ;
- temps.

## Legacy

Pour COBOL, Delphi, WinDev et ABAL, préférer des règles métier testables plutôt que des exercices de syntaxe isolée.

Très bon motif :

1. fournir un programme legacy ;
2. définir un corpus d'entrées/sorties ;
3. demander explication, correction ou migration ;
4. valider les sorties sur un ensemble caché.

Pour les langages dont la toolchain est difficilement automatisable, une migration vers Java peut servir de cible exécutable, à condition d'avoir une vérité terrain solide sur le comportement source.

## ABAL

Ne jamais substituer ABAP à ABAL.

Si la syntaxe précise n'est pas vérifiée par une source fiable, ne pas inventer une tâche de production. Deux options :

- fournir la documentation ABAL/Open ABAL comme contexte de tâche ;
- utiliser un fixture marqué explicitement comme synthétique jusqu'à validation par un exemple réel.

Il est souhaitable d'avoir deux catégories de résultat :

- `abal_closed_book`
- `abal_with_docs`

## Documents

Créer autant que possible les documents depuis une source structurée connue, puis produire les variantes d'image automatiquement.

Exemple :

1. générer un document avec valeurs connues ;
2. rendre en image/PDF ;
3. appliquer rotation/bruit/compression/résolution ;
4. demander une extraction JSON ;
5. comparer au JSON de vérité terrain.

Ne pas utiliser uniquement des documents réels sensibles.

## Versionnement d'une tâche

Incrémenter `revision` lorsque l'un de ces éléments change de façon à affecter la comparabilité :

- prompt ;
- données d'entrée ;
- comportement attendu ;
- tests publics ;
- tests cachés ;
- scoring ;
- limite d'itérations.

Une correction purement documentaire sans impact sur l'exécution ne nécessite pas forcément une nouvelle révision.
