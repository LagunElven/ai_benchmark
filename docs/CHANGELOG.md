# Changelog sémantique du benchmark

Ce fichier recense uniquement les changements susceptibles d'affecter la comparabilité.

## 0.25.19 — Future baseline Qwen FP8 en profil opérationnel

- Ajout de C-018 avec le checkpoint officiel Qwen3.8-27B-FP8 épinglé, la suite
  qualité `full` de 74 tâches, `reasoning_effort: medium` et prefix caching.
- Ajout de profils serving Q8/FP8 appariés sur RTX PRO 6000 : `shared-prefix`
  uniquement, cache activé, thinking medium et 20 répétitions. Chaque profil
  contient 20 cas et 1 800 requêtes mesurées.
- C-017 et C-018 sont groupés comme comparaison opérationnelle ; le checkpoint Q8
  tiers ne permet pas d'attribuer causalement les différences à la seule quantification.
- Les profils historiques et leurs résultats bruts restent inchangés.

## 0.25.18 — Intégrité des contextes et mesures de campagne

- Les tâches CTX-01 à CTX-06 retirent des prompts les chemins de réponse et
  gardent les manifestes de scoring hors workspace visible ; leurs révisions
  passent à 2. Le runner effectue un préflight tokenizer local avec réserve de
  sortie et marge de sécurité.
- Les reprises de campagnes sont liées à une empreinte SHA-256 du runner, des
  schémas, du plan, de la configuration, des tâches et des validateurs. Les
  anciens checkpoints sans empreinte ne sont plus repris. Les résultats
  conservent le type/groupe de comparaison, l'artefact, les révisions et le seed.
- Les résumés distinguent échecs fonctionnels/protocole, refus de capacité et
  erreurs d'infrastructure ; `--seed` permet des répétitions appariées.
- Le serving produit un schéma résultat 1.1 : TTFT absent pour le JSON non
  streamé, flux SSE incomplets signalés, origine des tokens conservée, warmup
  concurrent, 20 lots sur les profils complets et échantillonnage des ressources
  côté runner.
- DOC-10 passe en révision 2 et stocke les métriques de champs structurés dans
  le résultat brut sans rendre la vérité terrain visible.
- C-017 est classé comme comparaison opérationnelle et C-016 comme campagne
  terminée dans le plan GPU.

## 0.25.17 — Consolidation des campagnes Q8 et du reporting d'erreurs

- Les résultats de campagne qualité conservent maintenant les types d'erreur
  remontés par chaque run et leur agrégation (`error_counts`), notamment les
  erreurs de protocole et de client modèle.
- Ajout du profil serving Q8 complet pour la RTX PRO 6000, avec la même matrice
  de concurrence/contexte que le profil BF16.
- Les résultats BF16/Q8 du 22 septembre sont documentés comme comparaison
  opérationnelle ; le checkpoint Q8 tiers ne permet pas d'isoler la seule
  quantification.

## 0.25.16 — Campagne Q8 INT8 W8A16 avec vLLM

- Ajout de la campagne exploratoire `C-017` avec le checkpoint Safetensors
  `GotoAI-Inc/Qwen3.8-27B-W8A16`, épinglé à sa révision immuable.
- Le profil conserve le thinking `medium`, le KV cache FP8 et le prefix caching
  de C-016 ; seul l'artefact de poids change.
- Le checkpoint tiers reste identifié comme une solution opérationnelle tant
  que sa validation comparative n'est pas terminée.

## 0.25.15 — Profil qualité BF16 avec thinking medium

- Ajout du profil diagnostique Qwen3.8 BF16 `C-016`, identique à `C-015`
  mais avec `reasoning_effort: medium`.
- La campagne est limitée aux 11 tâches ayant servi à comparer le profil
  `no-thinking` ; elle reste une comparaison opérationnelle.

## 0.25.14 — Reprise des campagnes qualité interrompues

- `scripts/run_quality_campaign.py` checkpoint désormais la progression après
  chaque tâche et accepte `--resume` pour reprendre la dernière campagne
  incomplète compatible.
- Une reprise crée un nouvel artefact et conserve les résultats précédents ;
  les anciens `campaign.json` partiels restent repris lorsque leur sélection est
  identifiable. Les campagnes interrompues avant la finalisation de leur index
  peuvent être reconstruites depuis `results/raw/runs.jsonl` lorsque leur
  préfixe et leur configuration sont vérifiables.

## 0.25.13 — Profil qualité BF16 avec thinking low

- Ajout du profil qualité Qwen3.8 BF16 `C-015` avec prefix caching et
  `reasoning_effort: low` transmis dans `chat_template_kwargs`.
- Cette campagne est opérationnelle et doit être comparée à `C-014` pour
  mesurer le compromis vitesse/qualité du niveau de raisonnement.

## 0.25.12 — Profil qualité BF16 avec prefix caching

- Ajout d'un profil qualité Qwen3.8 BF16 pour la RTX PRO 6000 avec prefix
  caching activé.
- Cette campagne est explicitement opérationnelle (`C-014`) et ne remplace pas
  la baseline qualité contrôlée sans cache.

## 0.25.11 — Profil serving shared-prefix ciblé

- Ajout d'un profil serving BF16 RTX PRO 6000 limité au mode `shared-prefix`.
- Les contextes, concurrences et répétitions restent identiques à la matrice
  complète ; les modes `cold` et sans cache restent disponibles comme contrôles
  séparés et ne sont pas inclus dans cette campagne opérationnelle.

## 0.25.10 — Profil serving sans prefix caching

- Ajout d'un profil serving Qwen smoke sans cache de préfixe.
- La matrice est identique au profil cache activé et utilise explicitement
  `--no-enable-prefix-caching` pour permettre une comparaison contrôlée.
- Ajout de la matrice serving complète BF16 liée à la RTX PRO 6000.

## 0.25.9 — Calibrage tokenizer du serving

- Le générateur de contexte serving peut maintenant charger le tokenizer Hugging Face exact et compter le prompt après application du chat template.
- Les profils Qwen serving déclarent explicitement le dépôt et la révision de leur tokenizer ; le profil générique conserve un fallback regex explicite.
- La campagne serving affiche désormais le cas en cours et son résultat immédiatement dans le terminal.
- Les profils Qwen rendent explicite l'activation du prefix caching vLLM au lieu de dépendre de la valeur par défaut.

## 0.25.8 — Profil serving smoke Qwen3.8

- Ajout d'un profil serving court pour mesurer séparément la performance vLLM.
- Matrice initiale limitée à 1 et 5 utilisateurs, contextes 8k/32k/64k,
  modes cold/shared-prefix et une répétition.
- Profil explicitement configuré sans thinking afin de ne pas confondre la
  performance de serving avec une longueur variable de raisonnement.

## 0.25.7 — Tolérer une clôture manquante du bloc JSON

- Le protocole file_changes_v1 accepte désormais un bloc JSON précédé d'un
  marqueur de code JSON même si le marqueur de clôture manque.
- Le JSON reste validé strictement après retrait de cette enveloppe ; aucune
  explication ou donnée non JSON n'est acceptée.

## 0.25.6 — Ajouter le profil Qwen sans thinking

- Ajout du profil BF16 `C-013` sur RTX PRO 6000 avec `enable_thinking: false`.
- C-013 est marqué `operational_solution` et ne doit pas être mélangé aux
  comparaisons contrôlées de C-004.
- Le serveur vLLM reste inchangé : le paramètre est transmis au niveau de la
  requête via `chat_template_kwargs`.

## 0.25.5 — Donner à WEB-03 un budget de raisonnement suffisant

- `WEB-03` passe en révision 2 avec un plafond de 12000 tokens pour inclure le
  raisonnement Qwen et la réponse `file_changes_v1`.
- Le plafond est une limite maximale, pas une quantité obligatoire à générer.
- Le runner enregistre désormais le budget effectif de la tâche dans les
  métadonnées de génération.

## 0.25.4 — Respecter les budgets de sortie des tâches qualité

- Les profils qualité Qwen3.8 n'écrasent plus `runtime.max_output_tokens` avec un
  budget global de 32768 tokens.
- Chaque tâche utilise désormais son propre plafond de sortie, qui couvre le
  raisonnement et la réponse finale.
- Les plafonds globaux de réparation restent inchangés ; les résultats précédents
  restent conservés et ne sont pas réécrits.

## 0.25.3 — Séparer le raisonnement Qwen du contenu de réponse

- Ajout de `--reasoning-parser qwen3` aux profils Qwen3.8 vLLM.
- Le premier smoke qualité a confirmé que, sans parser, le bloc `<think>` était
  mélangé au JSON `file_changes_v1` et rendait la réponse inexploitable.
- La correction conserve le thinking pour la qualité et le désactive toujours
  explicitement pour le serving de débit.

## 0.25.2 — Stabiliser le nombre de séquences vLLM sur RTX PRO 6000

- Ajout de `--max-num-seqs 16` aux profils Qwen3.8 BF16, FP8 et NVFP4.
- Le défaut vLLM de 1024 provoquait l’échec de l’initialisation du cache Mamba
  sur la RTX PRO 6000 Blackwell Server Edition ; 16 couvre la matrice de
  concurrence jusqu’à 10 tout en conservant une marge.
- Ajout de `max_num_seqs` aux schémas, au plan GPU et aux métadonnées de serving.

## 0.25.1 — Figer la variante RTX PRO Server Edition

- Les campagnes C-004, C-006 et C-011 ciblent désormais explicitement la
  `NVIDIA RTX PRO 6000 Blackwell Server Edition`.
- Les variantes Workstation et Max-Q ne sont pas mélangées aux groupes de
  comparaison actuels.

## 0.25.0 — Ajouter les campagnes NVFP4 Blackwell

- Ajout de la variante `NVFP4-MIXED` basée sur le checkpoint
  `nvidia/Qwen3.8-27B-NVFP4`, produit avec NVIDIA Model Optimizer et épinglé à
  la révision `dbb8f445b3145f8a4c18ddc769f032d57d32867c`.
- Ajout des campagnes exploratoires de comparaison de quantification C-011 sur
  RTX PRO 6000 Blackwell et C-012 sur DGX Spark/GB10.
- Ajout des configurations qualité/serving NVFP4 ; le KV cache reste en FP8 et
  le tokenizer reste celui du checkpoint Qwen BF16.
- Le support du checkpoint doit réussir le smoke vLLM avant les campagnes
  qualité et serving ; les changements de backend ou de version sont conservés
  dans les métadonnées et peuvent faire basculer la comparaison en
  `operational_solution`.

## 0.24.0 — Basculer les campagnes Qwen vers vLLM

- Remplacement du dépôt GGUF Unsloth par les dépôts officiels Safetensors
  `Qwen/Qwen3.8-27B` et `Qwen/Qwen3.8-27B-FP8`.
- Suppression des campagnes Q8_0 et UD-Q8_K_XL, qui nécessiteraient le support
  GGUF expérimental de vLLM.
- Sélection de vLLM `0.29.0` comme moteur de référence et ajout du template FP8.
- Le plan conserve une révision immuable par variante et une révision commune du
  tokenizer officiel.

## 0.23.0 — Ajout du DGX Spark / GB10

- Ajout des campagnes C-009 BF16, C-010 Q8_0 et C-011 UD-Q8_K_XL pour le
  matériel NVIDIA DGX Spark / GB10.
- Extension des groupes contrôlés BF16/Q8_0 à trois plateformes.
- Ajout des précautions de mesure liées à la mémoire unifiée du GB10.

## 0.22.0 — Préparation des campagnes GPU distantes

- Ajout d'un plan versionné C-003 à C-008 avec variantes BF16, Q8_0 et UD-Q8_K_XL.
- Ajout du préflight local qui empreinte les configurations et tous les fichiers
  model-visible sans inclure les tests cachés.
- Ajout du préflight hôte GPU, du smoke endpoint et du runner de campagne qualité
  avec manifeste JSON/JSONL append-only.
- Ajout du runbook Vast.ai ; la configuration concrète du moteur reste à figer
  avant de déclarer une campagne prête.

## 0.21.0 — Protocole des campagnes GPU

- Ajout du plan reproductible des campagnes H200 et RTX PRO 6000 Blackwell.
- Définition des comparaisons contrôlées BF16/Q8_0, de la piste exploratoire
  UD-Q8_K_XL et de la séparation entre qualité contrôlée et profils serving
  optimisés par matériel.
- Ajout d'un préflight de capacité 64k/128k/262k et de critères explicites
  pour conserver les OOM, refus de contexte et écarts de configuration.

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
