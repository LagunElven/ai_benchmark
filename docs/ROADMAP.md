# Roadmap d'implémentation

## Milestone 0 — Bootstrap

- [x] Créer l'arborescence du dépôt.
- [x] Installer les documents de cadrage.
- [x] Choisir Python et une version minimale supportée.
- [x] Ajouter formatage/lint/tests du runner.
- [x] Définir un mode local sans GPU.

## Milestone 1 — Schémas et découverte des tâches

- [x] `task.schema.json`
- [x] `run-result.schema.json`
- [x] `benchmark-config.schema.json`
- [x] parseur et validation de `task.yaml`
- [x] découverte des tâches par suite/tag/catégorie
- [x] commande `list-tasks`

## Milestone 2 — Runner minimal

- [x] workspace propre par run
- [x] client OpenAI-compatible
- [x] exécution one-shot
- [x] capture réponse
- [x] exécution des validateurs
- [x] stockage JSON/JSONL
- [x] logs de run
- [x] timeouts

## Milestone 3 — Isolation et hidden tests

- [x] le modèle ne voit jamais `private-tests/`
- [x] injection/montage seulement lors de la validation
- [x] test automatique prouvant l'isolation
- [x] séparation des artefacts model-visible / validator-visible

## Milestone 4 — Repair loop

- [x] retour contrôlé des erreurs publiques
- [x] 3 itérations maximum par défaut
- [x] Pass@1/2/3
- [x] arrêt immédiat en cas de succès
- [x] budget tokens/temps

## Milestone 5 — Smoke suite

Implémenter au moins :

- [x] JAVA-03 (concurrence de collection)
- [x] SPRING-05 (contrat d'optimistic locking, harnais Java hors dépendance)
- [x] AXON-02 (upcaster de révision, harnais Java hors dépendance)
- [x] WEB-03 (sémantique `switchMap`, harnais Node hors dépendance)
- [x] COBOL-05 (migration avec référence COBOL, validation Java de substitution)
- [x] DOC-10 (extraction JSON structurée sur rendu texte)
- [x] CTX-01 (réparation avec distracteurs de contexte)

La commande `python scripts/run_smoke.py` exécute ces sept tâches avec un adaptateur
fake déterministe. Les résultats produits restent dans `results/raw/` et ne sont
pas inclus dans Git. `cobc` et Tesseract n'étant pas installés sur la machine de
développement, les tâches COBOL/OCR natives restent explicitement à compléter.

Le smoke doit être suffisamment petit pour valider rapidement une nouvelle machine louée.

## Milestone 6 — Documents/OCR framework

- [x] générateur de document source (`runner.document_dataset`)
- [x] vérité terrain JSON versionnée et contrôlée par schéma
- [x] génération de variantes 300/150 dpi
- [x] rotation déterministe
- [x] bruit et compression grayscale reproductibles
- [x] extraction JSON (scoring d'une sortie candidate)
- [x] calcul CER/WER
- [x] précision par champ, champs manquants/hallucinés et schéma

Le framework fonctionne sans Tesseract : l'adaptateur OCR d'une campagne peut
consommer les PGM générés et transmettre le texte/JSON candidat au scorer.

## Milestone 7 — Legacy

- [x] détection et exécution conditionnelle GnuCOBOL si disponible
- [x] Delphi fixture avec statut de syntaxe explicite
- [x] WLanguage fixture synthétique documenté
- [x] ABAL fixture synthétique validé par schéma
- [x] ABAL avec documentation fournie et distinction ABAL/ABAP
- [x] migrations legacy → Java avec tests d'équivalence cachés

Les compilateurs propriétaires ou rares ne sont pas supposés présents. La
commande `python scripts/check_legacy_toolchains.py --json` capture leur état ;
`python scripts/run_legacy_equivalence.py` exécute les cibles Java et les
validations cachées des quatre migrations disponibles.

## Milestone 8 — Long context

- [x] générer plusieurs tailles d'un même projet (10k à 200k)
- [x] mesurer les tokens via tokenizer optionnel, avec fallback explicite
- [x] contrôler le niveau de distraction par génération déterministe
- [x] mesurer fichiers pertinents vs fichiers modifiés

Le générateur écrit un manifeste par variante, conserve les mêmes fichiers
fonctionnels et ajoute seulement generated-distractors/. Les variantes sont
produites à la demande afin de ne pas alourdir le dépôt ; leurs manifestes
enregistrent seed, tokenizer, nombre réel de tokens et SHA-256.

## Milestone 9 — Suite complète

Atteindre progressivement environ 74 tâches qualité.

- [x] Java 8 (8 tâches implémentées)
- [x] Spring 10 (10 tâches implémentées)
- [x] Axon 10 (10 tâches implémentées)
- [x] Web 10 (10 tâches implémentées)
- [x] COBOL 5 (5 tâches implémentées)
- [x] Delphi 4 (4 tâches implémentées)
- [x] WinDev 4 (4 tâches implémentées)
- [x] ABAL 4 (4 tâches implémentées)
- [x] Documents 10 (10 tâches implémentées)
- [x] Context 6 (6 variantes exécutables de 10k à 200k)
- [x] E2E 3 (3 tâches implémentées)

La milestone 9 porte l'inventaire complet dans `catalogue.yaml` et fournit 74
tâches exécutables, sans transformer les scénarios en stubs trompeurs.
`python scripts/check_catalogue.py` contrôle la cohérence entre l'inventaire et les
dossiers découverts. Les tâches E2E couvrent désormais les contrats Angular/Axon/JPA
et la modernisation d'une règle COBOL vers Java avec validation déterministe.

## Milestone 10 — Serving

- [x] adapter vLLM benchmark / API generic
- [x] 1/2/5/10 utilisateurs
- [x] 8k/32k/64k/100k/200k contextes
- [x] cold prefixes
- [x] shared prefixes
- [x] TTFT
- [x] throughput
- [x] TPOT
- [x] mémoire GPU
- [x] KV cache
- [x] OOM/timeout

Le benchmark serving est indépendant des résultats de qualité. Sa matrice par défaut
contient 40 cas et ses résultats bruts sont versionnés par run dans `results/raw/serving/`.
Les métriques matérielles et KV-cache restent explicitement indisponibles lorsque le
serveur ou la machine ne les expose pas.

Un pilote applicatif distinct complète maintenant cette matrice : 18 tâches qualité dans
une cohorte finie. Les points de référence sont 1/5/10 agents, avec possibilité d'explorer
tout nombre d'agents jusqu'à la limite la plus basse entre les tâches sélectionnées et
`serving.max_num_seqs` ; la concurrence des appels modèle dépend de la boucle de réparation
et des validations.

- [x] créer l'orchestrateur de cohorte fermée, son plan et son schéma de résultat
- [x] exécuter le pilote FP8 + DFlash2 à 1/4/5/6/8/10 agents et documenter les résultats
- [x] exécuter et documenter trois runs FP8 sans DFlash2 avec télémétrie pour chacun
  des niveaux 1/4/5/6/8/10 agents (18 runs retenus ; 320/324 tâches réussies ; le
  run initial à 5 agents sans télémétrie reste archivé à part)
- [ ] réaliser la comparaison appariée FP8 sans DFlash2 / FP8 + DFlash2 sur la même
  instance, avec état de prefix cache et warmup contrôlés ou documentés, charge
  serveur distante relevée et écart entre pilote déclaré et pilote distant résolu
- [x] réaliser et documenter trois répétitions FP8 + DFlash2 avec télémétrie GPU
  pour chaque niveau de 1/4/5/6/8/10 agents sur le même serveur (18 runs ;
  315/324 tâches réussies ; les neuf échecs concernent `DOC-03`). Détails et
  limites de comparaison dans `docs/COHORT_SESSION_2026-09-24-DFLASH2.md`.
- [x] analyser les échecs récurrents de DOC-03 dans les deux séries de cohortes FP8 ;
  voir [le rapport d'analyse](GPU_FAILURE_ANALYSIS_2026-09-24.md)
- [ ] clarifier les formats de date acceptés par DOC-03 ; versionner toute modification
  de prompt, de données ou de tests avant de réutiliser cette tâche comme référence

## Milestone 11 — GPU campaigns

Le protocole des campagnes et l'ordre de reprise sont définis dans
[`docs/GPU_CAMPAIGN_PLAN.md`](GPU_CAMPAIGN_PLAN.md). Les campagnes réelles restent
à exécuter pour les comparaisons contrôlées H200, RTX PRO et DGX Spark, ainsi que pour
NVFP4. Les profils opérationnels C-016 (BF16) et C-017 (Q8) ont déjà été exécutés sur
RTX PRO 6000 ; leurs résultats ne remplacent pas ces campagnes contrôlées.

- [x] protocole de comparaison contrôlée BF16/FP8 avec vLLM
- [x] matrice initiale C-003 à C-006 et C-009/C-010
- [x] campagnes NVFP4 distinctes C-011/C-012 pour RTX PRO et DGX Spark
- [x] plan versionné, préflight local et manifeste de campagne
- [x] playbook distant générique avec tunnel SSH et préflight hôte
- [ ] playbook reproductible H200 spécifique au moteur retenu
- [ ] playbook reproductible RTX PRO 6000 Blackwell spécifique au moteur retenu
- [x] campagnes DGX Spark / GB10 ajoutées au plan contrôlé
- [ ] playbook reproductible DGX Spark / GB10 spécifique au moteur retenu
- [x] exécuter C-018 : Qwen FP8 officiel, suite qualité full (terminée avec
  échecs) et serving shared-prefix en thinking medium
- [x] analyser les échecs qualité de C-018/C-019 avant d'en faire une base de référence ;
  voir [le rapport d'analyse](GPU_FAILURE_ANALYSIS_2026-09-24.md)
- [x] exécuter C-019 : cible FP8 + draft DFlash2, qualité terminée avec échecs,
  serving exécuté et cohorte agentique explorée
- [ ] réaliser la matrice opérationnelle RTX PRO 6000 ci-dessous ; C-018/C-019
  restent les cellules vLLM/FP8 déjà mesurées, et les plans ayant servi à ces runs
  sont conservés comme entrées historiques immuables

Ordre de reprise opérationnelle (la comparaison appariée FP8 reste différée) :

Le serving vLLM NVFP4 sans DFlash2 a été exécuté sur la RTX PRO 6000 en
`shared-prefix` uniquement ; les 20 cas et 1 800 requêtes ont réussi. Voir le
[rapport serving NVFP4](GPU_SERVING_NVFP4_2026-09-24.md). La qualité et la cohorte
de cette cellule restent à exécuter.

1. vLLM + NVFP4 sans DFlash2 : campagne qualité, serving et cohorte.
2. vLLM + NVFP4 avec DFlash2 : campagne qualité, serving et cohorte.
3. SGLang + FP8 sans DFlash2 : campagne qualité, serving et cohorte.
4. SGLang + FP8 avec DFlash2 : campagne qualité, serving et cohorte.
5. SGLang + NVFP4 sans DFlash2 : campagne qualité, serving et cohorte.
6. SGLang + NVFP4 avec DFlash2 : campagne qualité, serving et cohorte.

Garde-fous de cette matrice : smoke SGLang avant toute campagne complète (API,
raisonnement medium, appels d'outils/protocole, contexte, cache et acceptance DFlash2 si
activé) ; KV cache FP8 pour toutes les variantes DFlash2, y compris avec poids NVFP4 ;
confirmation de vrais hits cache avant d'interpréter les cas shared-prefix ; au moins
trois cohortes par cellule de concurrence comparée. Les comparaisons doivent être appariées
sur les mêmes tâches/révisions, prompts, seed, matériel, limites de contexte/sortie et
réglages de raisonnement. Toute différence nécessaire propre au moteur doit être enregistrée.
Les métriques d'utilisation GPU doivent provenir du serveur distant, jamais être déduites
des mesures du poste runner. Le protocole détaillé est dans
[`docs/GPU_CAMPAIGN_PLAN.md`](GPU_CAMPAIGN_PLAN.md).

Chaque playbook doit documenter :

- OS/image
- drivers
- CUDA
- Docker
- moteur d'inférence
- versions
- téléchargement modèle
- lancement serveur
- commande smoke
- commande full
- collecte résultats

### Suivi de la session GPU du 22 septembre 2026

- [x] Répéter trois fois avec Q8 les tâches documentaires `DOC-02`, `DOC-03`,
  `DOC-05`, `DOC-06`, `DOC-07` et `DOC-08`. Chaque répétition a réussi 1/6
  après réparation ; voir le [compte rendu](GPU_SESSION_2026-09-22.md).
- [x] Créer et exécuter le profil serving Q8 complet : 40 cas et 540 requêtes,
  sans échec.
- [x] Documenter la comparaison BF16/Q8. Elle reste opérationnelle : le checkpoint
  Q8 est tiers, le serving BF16 `cold` n'a que six cellules communes et les
  métriques du GPU distant n'étaient pas exposées.
- [x] Agréger dans les rapports les erreurs de protocole et les erreurs client
  présentes dans les résultats de run.
- [ ] Recalibrer ou documenter définitivement `CTX-06`, dont le prompt réel
  dépasse la fenêtre effective de 262144 tokens.

## Milestone 12 — Reporting

- [ ] export CSV
- [ ] tableaux contrôlés par variable
- [ ] courbes contexte vs réussite
- [ ] concurrence vs TTFT/tok/s
- [ ] quantification vs qualité
- [ ] coût par tâche réussie
- [ ] génération d'un rapport HTML statique si utile
