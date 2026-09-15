# Enterprise LLM Benchmark — Plan d'action

## 1. Objectif

Construire un jeu de benchmarks reproductible afin d'aider à choisir :

- le matériel GPU ;
- le modèle ;
- la quantification / précision ;
- le moteur d'inférence ;
- les paramètres de serving ;
- et, au final, une solution opérationnelle pour des développeurs et utilisateurs métiers.

Le benchmark doit permettre de rejouer exactement les mêmes tâches sur des configurations différentes.

## 2. Ce que le benchmark doit éviter

- Un score global opaque.
- Les tests uniquement basés sur des questions/réponses sans validation.
- Les exercices artificiels trop courts comme seul indicateur de capacité de développement.
- Les comparaisons où plusieurs variables changent sans que cela soit clairement indiqué.
- Les tests cachés visibles dans le contexte du modèle.
- Les résultats impossibles à reproduire faute de version exacte du modèle ou de configuration du serveur.

## 3. Axes de mesure

### A. Qualité de développement

Mesurer si le modèle :

- comprend un code existant ;
- identifie correctement un bug ;
- choisit les bons fichiers ;
- produit un patch compilable ;
- passe les tests fonctionnels ;
- n'introduit pas de régression ;
- sait effectuer une évolution multi-fichiers ;
- utilise correctement des frameworks peu triviaux.

### B. Capacité de réparation agentique

Mesurer :

- réussite au premier essai ;
- réussite après retour d'une erreur de compilation/test ;
- nombre d'itérations ;
- répétition éventuelle de la même erreur ;
- nombre de tokens et temps nécessaires pour atteindre une solution valide.

### C. OCR / documents

Mesurer :

- transcription ;
- extraction structurée ;
- lecture de tableaux ;
- robustesse à la qualité du scan ;
- exactitude des nombres/dates/références ;
- hallucinations.

### D. Contexte long

Mesurer l'évolution de la qualité lorsqu'on augmente progressivement la taille d'un repository ou du contexte tout en conservant le même problème à résoudre.

### E. Serving / GPU

Mesurer indépendamment :

- latence ;
- débit ;
- concurrence ;
- mémoire ;
- prefix caching ;
- comportement aux grands contextes ;
- stabilité/OOM.

## 4. Catalogue cible

### Java — 8

1. Null-safety / Stream / Optional.
2. Dates, fuseaux horaires et DST.
3. Modification concurrente de collection.
4. Synchronisation et thread-safety.
5. Refactoring d'une méthode métier complexe.
6. Race condition intermittente.
7. Optimisation sans changement fonctionnel.
8. Evolution d'API compatible avec l'existant.

### Spring — 10

1. REST + validation.
2. Gestion d'exception.
3. Transaction / rollback.
4. Dirty checking Hibernate.
5. Lost update / `@Version`.
6. `@DynamicUpdate` et concurrence.
7. N+1 JPA.
8. Reactor retry non bloquant.
9. Bearer / CSRF / sécurité.
10. Bug transactionnel multi-service.

### Axon — 10

1. Event handler.
2. Upcaster ajoutant un champ à partir d'un ancien champ.
3. Chaîne de révisions d'upcasters.
4. Ignorer uniquement les anciens snapshots ciblés.
5. Saga et associations.
6. Deux chemins `@StartSaga`.
7. Projection idempotente.
8. Replay/reconstruction de projection.
9. Optimistic locking / propagation d'erreur.
10. Diagnostic multi-aggregate.

### Angular / Ionic — 10

1. `Observable<T>` vs `T`.
2. Lifecycle des subscriptions.
3. Recherche `switchMap`.
4. HTTP interceptor.
5. Bearer + CSRF.
6. Formulaire réactif complexe.
7. Signals / RxJS.
8. Navigation Ionic.
9. OAuth / deep-link Capacitor.
10. Evolution API → service → component → template.

### COBOL — 5

1. Compréhension.
2. Correction d'un bug métier.
3. Fichier séquentiel / PIC / COMP-3.
4. Evolution sans régression.
5. Migration vers Java avec résultats équivalents.

### Delphi — 4

1. Compréhension Object Pascal.
2. Lifecycle/ressources.
3. Correction métier.
4. Migration vers Java.

### WinDev/WLanguage — 4

1. Compréhension.
2. HFSQL.
3. Correction métier.
4. Migration vers Java.

### ABAL — 4

ABAL = Advanced Business Application Language, à ne pas confondre avec ABAP.

1. Compréhension d'un programme ABAL.
2. Modification d'une règle métier.
3. Migration ABAL → Java.
4. Tâche avec documentation ABAL/Open ABAL fournie dans le contexte.

Le cas ABAL est intéressant pour mesurer deux choses distinctes : la connaissance intrinsèque du modèle et sa capacité à apprendre une technologie rare à partir d'une documentation fournie.

### Documents/OCR — 10

1. Document numérique propre.
2. Scan 300 dpi.
3. Scan 150 dpi.
4. Rotation légère.
5. Bruit/compression.
6. Tableau.
7. Formulaire.
8. Multi-page.
9. Documents mélangés.
10. Extraction JSON complexe.

### Contexte long — 6

Même problème logique, contexte croissant :

- ~10k tokens
- ~30k
- ~60k
- ~100k
- ~150k
- ~200k

### E2E — 3

1. Spring REST → DTO → Angular UI.
2. Angular → REST → Axon → Event → projection JPA.
3. Legacy → Java/Spring.

## 5. Ordre de réalisation conseillé

### Phase 1 — Fondation

Créer :

- structure du repository ;
- format `task.yaml` ;
- schémas JSON ;
- runner minimal ;
- abstraction de client OpenAI-compatible ;
- isolation des workspaces ;
- exécution des validations ;
- stockage JSON/JSONL des résultats.

Ne pas dépendre d'un GPU pendant cette phase.

### Phase 2 — Premiers tests représentatifs

Implémenter entièrement :

- 1 Java ;
- 1 Spring ;
- 1 Axon ;
- 1 Angular/Ionic ;
- 1 COBOL ou autre legacy ;
- 1 document/OCR ;
- 1 long-context.

Objectif : valider le modèle de tâche avant d'en créer des dizaines.

### Phase 3 — Boucle de réparation

Ajouter :

- retour contrôlé des logs au modèle ;
- maximum d'itérations ;
- Pass@1 / Pass@2 / Pass@3 ;
- temps/tokens jusqu'au succès ;
- détection des régressions.

### Phase 4 — Expansion du catalogue

Construire progressivement les ~74 tâches.

### Phase 5 — Serving benchmark

Intégrer des scripts autour de vLLM ou outils équivalents pour tester :

- concurrence ;
- contextes ;
- cold/shared prefix ;
- TTFT ;
- tok/s ;
- mémoire ;
- erreurs.

### Phase 6 — Location GPU / campagnes

Après stabilisation du corpus et du runner :

1. définir le fournisseur et l'image de base ;
2. documenter précisément l'installation ;
3. valider une campagne smoke ;
4. exécuter core/full ;
5. exporter tous les résultats ;
6. détruire la machine louée uniquement après vérification de la sauvegarde des résultats.

### Phase 7 — Reporting

Produire des comparaisons :

- matériel contrôlé ;
- quantification contrôlée ;
- modèle contrôlé ;
- solution opérationnelle.

## 6. Priorité de comparaison

Pour une première campagne scientifique, viser une configuration disponible sur les trois matériels et conserver autant que possible :

- même modèle ;
- même révision ;
- même dtype/quantification ;
- même moteur d'inférence ;
- même version ;
- mêmes prompts ;
- mêmes longueurs de contexte ;
- mêmes paramètres de génération.

Changer uniquement le GPU lorsque l'objectif est de comparer H200, RTX PRO 6000 et DGX Spark.

Ensuite seulement comparer quantifications puis modèles.

## 7. Répétitions

Pour les tâches de qualité, prévoir idéalement 3 runs indépendants par combinaison pertinente.

Pour les performances serving :

- warmup ;
- plusieurs runs ;
- médiane ;
- p95.

Même avec une température nulle, ne pas supposer une déterminisme parfait du système complet.

## 8. Résultats attendus

Le benchmark doit permettre de répondre à des questions comme :

- Sur le même modèle BF16, combien perd-on en débit en passant d'un H200 à un Spark ?
- Une RTX PRO 6000 peut-elle servir 5 à 10 développeurs avec 100k tokens de contexte ?
- Une quantification Q8 dégrade-t-elle réellement la réussite sur Spring/Axon ?
- Un modèle plus lent réussit-il davantage après une boucle de correction ?
- À partir de quelle taille de repository un modèle commence-t-il à perdre le fil ?
- Quel modèle lit le mieux les montants, dates et identifiants dans des scans dégradés ?
- Un modèle est-il capable de travailler sur ABAL avec documentation même s'il connaît mal le langage sans documentation ?
- Quel est le coût par tâche réussie et pas seulement le coût par million de tokens ?
