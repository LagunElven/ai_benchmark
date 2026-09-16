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

## Milestone 11 — GPU campaigns

Préparer des playbooks reproductibles pour :

- [ ] H200
- [ ] RTX PRO 6000 Blackwell
- [ ] DGX Spark

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

## Milestone 12 — Reporting

- [ ] export CSV
- [ ] tableaux contrôlés par variable
- [ ] courbes contexte vs réussite
- [ ] concurrence vs TTFT/tok/s
- [ ] quantification vs qualité
- [ ] coût par tâche réussie
- [ ] génération d'un rapport HTML statique si utile
