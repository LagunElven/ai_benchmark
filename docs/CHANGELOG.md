# Changelog sémantique du benchmark

Ce fichier recense uniquement les changements susceptibles d'affecter la comparabilité.

## 0.20.0 — Socle serving reproductible

- Ajout d'un client OpenAI-compatible générique en streaming SSE avec mesure du TTFT,
  usage d'entrée/sortie, TPOT, erreurs HTTP, OOM et timeout.
- Ajout de `serving/config.yaml` et d'une matrice 40 cas couvrant 1/2/5/10 utilisateurs,
  8k/32k/64k/100k/200k tokens, warmup, répétitions, préfixes cold et shared-prefix.
- Ajout de la persistance brute de campagnes serving et du schéma associé ; les métriques
  serving restent séparées des résultats qualité et les comparaisons sont reproductibles.
- Ajout de l'échantillonnage best-effort `nvidia-smi`/mémoire hôte et de la capture des
  métriques KV-cache exposées par headers, avec valeurs d'indisponibilité explicites.
- La milestone 10 couvre désormais toutes ses dimensions initiales sans exiger de GPU
  ni de dépendance serveur spécifique pour exécuter les tests locaux.

## 0.19.0 — Milestone 9 complète

- Ajout de E2E-02 avec un contrat multi-couches Angular → commande → événement Axon
  → projection JPA, incluant accumulation, versions contiguës et validation cachée.
- Ajout de E2E-03 avec une règle COBOL fournie, un service Java de modernisation et
  un adaptateur API, avec équivalences décimales, opérations ordonnées et erreurs.
- Les contrats de couches restent indépendants des frameworks natifs afin de rendre
  les validations reproductibles sur une machine de développement standard.
- Les 74 tâches du catalogue sont désormais exécutables et validées publiquement et
  secrètement ; la milestone 9 est complète.

## 0.18.0 — Couverture Context complète

- Ajout de CTX-02 à CTX-06 comme variantes matérialisées du même scénario de
  réparation, à environ 30k, 60k, 100k, 150k et 200k tokens.
- Chaque variante conserve le même workspace fonctionnel, les mêmes distracteurs
  déterministes, le même fichier pertinent `src/billing.py` et un manifeste avec
  seed, méthode de comptage, tailles réelles et empreintes SHA-256.
- Ajout de validations publiques et cachées indépendantes pour les cinq niveaux ;
  la précision/rappel des fichiers modifiés et le contexte sont conservés comme
  métriques séparées.
- La catégorie Context atteint 6 tâches exécutables et le catalogue global 72 tâches
  sur 74 scénarios réservés.

## 0.17.0 — Couverture Documents complète

- Ajout de DOC-01 à DOC-05 et DOC-08/DOC-09 avec transcriptions déterministes pour
  document numérique, scans 300/150 DPI, rotation, bruit, multi-pages et types mélangés.
- Les validateurs mesurent des champs critiques, nombres, dates, identifiants, cellules de
  tableaux, validité JSON et erreurs de parsing sans dépendance OCR native.
- Correction du bootstrap d'import des checks publics DOC-06/DOC-07 pour qu'ils s'exécutent
  correctement dans le workspace isolé du runner.
- La catégorie Documents atteint 10 tâches exécutables et le catalogue global 67 tâches
  sur 74 scénarios réservés.

## 0.16.0 — Couverture WinDev et ABAL complète

- Ajout de WL-01/WL-03 et ABAL-01/ABAL-03 avec pseudo-sources explicitement marquées
  `synthetic_pseudocode`, contrats documentés et validations Java publiques/cachées.
- Les catégories WinDev et ABAL atteignent chacune 4 tâches exécutables ; le catalogue
  global atteint 60 tâches sur 74 scénarios réservés.
- Les scénarios ABAL-01/ABAL-03 restent des évaluations sans documentation propriétaire
  fournie, tandis qu'ABAL-04 conserve le scénario assisté par documentation.

## 0.15.0 — Couverture Delphi complète

- Ajout de DELPHI-01 (compréhension d'une règle de stock) et DELPHI-02 (cycle de vie
  d'un propriétaire de ressources), avec sources Object Pascal standard marquées
  `verified_syntax` et validations Java publiques/cachées.
- La catégorie Delphi atteint 4 tâches exécutables et le catalogue global 56 tâches sur
  74 scénarios réservés.

## 0.14.0 — Couverture COBOL complète

- Ajout de COBOL-01, COBOL-03 et COBOL-04 avec sources fixed-format, manifestes
  `verified_syntax`, cibles Java portables et validations déterministes.
- La catégorie COBOL atteint 5 tâches exécutables et le catalogue global 54 tâches sur
  74 scénarios réservés.
- Le harness d'équivalence sélectionne explicitement les quatre migrations Java munies
  d'un adaptateur fake via le tag `java-equivalence`.

## 0.13.0 — Couverture Web complète

- Ajout de WEB-07 à WEB-10 : état Signals/RxJS, navigation Ionic avec garde asynchrone,
  callback OAuth via deep link Capacitor et fonctionnalité Web multi-couches.
- Le catalogue Web atteint ses 10 tâches exécutables et le catalogue global 51 tâches
  sur 74 scénarios réservés.

## 0.12.0 — Spring complète et nouvelle tranche Web

- SPRING-10 complète la couverture Spring avec une orchestration multi-service et
  compensation en cas d'échec.
- Ajout de WEB-02, WEB-05 et WEB-06 pour le cycle de vie RxJS, la propagation sûre des
  credentials HTTP et la validation d'un formulaire réactif complexe.
- Le catalogue compte désormais 47 tâches exécutables sur 74 scénarios réservés.

## 0.11.0 — Couverture Java/Spring/Axon renforcée

- Java atteint ses 8 scénarios avec JAVA-07 (optimisation) et JAVA-08 (évolution API).
- Axon atteint ses 10 scénarios avec AXON-06 et AXON-08 à AXON-10.
- Spring ajoute SPRING-04, SPRING-06, SPRING-07 et SPRING-09 ; seul SPRING-10 reste
  planifié dans cette famille.
- Le catalogue compte désormais 43 tâches exécutables sur 74 scénarios réservés.

## 0.10.0 — Tranche Java/Spring/Axon

- Ajout de sept tâches déterministes : JAVA-05/06, SPRING-03/08 et AXON-01/04/05.
- Les validations couvrent refactoring avec invariants, races concurrentes, rollback
  transactionnel, retry asynchrone, handlers d'événements, snapshots et sagas.
- Le catalogue compte désormais 33 tâches exécutables sur 74 scénarios réservés.

## 0.9.0 — Deuxième tranche de la suite complète

- Ajout de huit tâches déterministes : JAVA-04, SPRING-02, AXON-07, WEB-04,
  DELPHI-03, WL-02, ABAL-02 et DOC-07.
- Les validations couvrent concurrence, mapping d'erreurs, idempotence, sécurité HTTP,
  règles legacy, requêtes HFSQL, éligibilité ABAL et formulaires OCR.
- Le catalogue compte désormais 26 tâches exécutables sur 74 scénarios réservés.

## 0.8.0 — Première tranche de la suite complète

- Ajout de l'inventaire versionné `catalogue.yaml` couvrant les 74 tâches cibles.
- Ajout du contrôle de couverture `runner.catalogue` et de `scripts/check_catalogue.py`.
- Ajout de huit tâches déterministes : JAVA-01/02, SPRING-01, AXON-03, WEB-01,
  COBOL-02, DOC-06 et E2E-01.
- Les tâches restantes restent explicitement `planned` ; aucun placeholder n'est
  présenté comme une validation qualité.

## 0.7.0 — Variantes long-context contrôlées

- Ajout de `runner.context_dataset` et du schéma de manifeste de variante.
- Ajout de la génération déterministe des tailles 10k/30k/60k/100k/150k/200k
  avec distracteurs séparés et fichiers pertinents déclarés.
- Ajout du comptage tokenizer optionnel (`tiktoken`) et du fallback regex
  explicitement identifié lorsque le tokenizer du modèle n'est pas disponible.
- Ajout des scripts de génération et de scoring précision/rappel des fichiers.

## 0.6.0 — Fixtures legacy et équivalence

- Ajout du manifeste `legacy-fixture` avec statut `verified_syntax` ou
  `synthetic_pseudocode`, documentation fournie et vecteurs d'équivalence.
- Ajout des tâches DELPHI-04, WL-04 et ABAL-04 avec migrations Java et tests
  cachés ; COBOL-05 rejoint le catalogue de vecteurs.
- Ajout de la détection non destructive des toolchains GnuCOBOL, Delphi,
  WinDev et ABAL et du script d'exécution des équivalences Java.
- Les syntaxes WLanguage et ABAL non vérifiables sont explicitement marquées
  synthétiques ; ABAL signifie Advanced Business Application Language, pas ABAP.

## 0.5.0 — Framework documents/OCR

- Ajout d'un schéma de source documentaire et d'un générateur hors ligne avec
  texte canonique, vérité terrain et manifeste SHA-256.
- Ajout de variantes raster PGM déterministes : 300/150 DPI, rotation, bruit et
  quantification grayscale servant de substitut de compression sans codec externe.
- Ajout des métriques CER/WER et du scoring structuré par champ (numérique, date,
  identifiant, cellules, champs manquants/hallucinés et validité JSON/schéma).
- Ajout des commandes `scripts/generate_document_dataset.py` et
  `scripts/score_document.py`, avec fixture invoice reproductible.

## 0.4.0 — Smoke suite représentative

- Ajout de sept tâches `smoke` exécutables hors ligne : JAVA-03, SPRING-05,
  AXON-02, WEB-03, COBOL-05, DOC-10 et CTX-01.
- Ajout de validateurs publics/cachés et de fixtures déterministes pour les
  contrats Java, Node et Python ; les tests cachés restent hors du workspace modèle.
- Ajout de `scripts/run_smoke.py`, adaptateur fake reproductible pour vérifier le
  packaging et le runner sans endpoint LLM.
- Les harnais COBOL/Spring/Axon/OCR qui substituent une dépendance native sont
  signalés explicitement dans la documentation.

## 0.3.0 — Boucle de réparation

- Ajout du mode `repair` avec retour des seuls logs publics.
- Limite de trois itérations et budgets globaux de temps/tokens.
- Conservation des réponses par tentative et calcul Pass@1/2/3.
- Arrêt immédiat après succès public et validation cachée.

## 0.2.0 — Isolation des tests cachés

- Ajout d'un workspace validator-visible distinct.
- Injection de `private-tests/<task-id>/` uniquement après le patch du modèle.
- Suppression systématique du workspace contenant les tests cachés.
- Tests automatisés de non-divulgation et d'injection contrôlée.

## 0.1.0 — Fondation

- Définition initiale des schémas de configuration, de tâche et de résultat.
- Définition du protocole de réponse `file_changes_v1`.
- Mode `one-shot` avec validation publique ; tests cachés et boucle `repair` non encore actifs.
