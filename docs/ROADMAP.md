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

- [ ] JAVA-03 ou JAVA-04
- [ ] SPRING-05
- [ ] AXON-02 ou AXON-04
- [ ] WEB-01 ou WEB-03
- [ ] COBOL-02/05
- [ ] DOC-02/10
- [ ] CTX-01

Le smoke doit être suffisamment petit pour valider rapidement une nouvelle machine louée.

## Milestone 6 — Documents/OCR framework

- [ ] générateur de document source
- [ ] vérité terrain JSON
- [ ] génération de variantes 300/150 dpi
- [ ] rotation
- [ ] bruit/compression
- [ ] extraction JSON
- [ ] calcul CER/WER
- [ ] précision par champ

## Milestone 7 — Legacy

- [ ] COBOL automatisé avec GnuCOBOL si possible
- [ ] Delphi fixtures
- [ ] WLanguage fixtures
- [ ] ABAL fixtures validés
- [ ] ABAL avec documentation fournie
- [ ] migrations legacy → Java avec tests d'équivalence

## Milestone 8 — Long context

- [ ] générer plusieurs tailles de même projet
- [ ] mesurer tokens exacts avec tokenizer du modèle lorsque possible
- [ ] contrôler le niveau de distraction
- [ ] mesurer fichiers pertinents vs fichiers modifiés

## Milestone 9 — Suite complète

Atteindre progressivement environ 74 tâches qualité.

- [ ] Java 8
- [ ] Spring 10
- [ ] Axon 10
- [ ] Web 10
- [ ] COBOL 5
- [ ] Delphi 4
- [ ] WinDev 4
- [ ] ABAL 4
- [ ] Documents 10
- [ ] Context 6
- [ ] E2E 3

## Milestone 10 — Serving

- [ ] adapter vLLM benchmark / API generic
- [ ] 1/2/5/10 utilisateurs
- [ ] 8k/32k/64k/100k/200k contextes
- [ ] cold prefixes
- [ ] shared prefixes
- [ ] TTFT
- [ ] throughput
- [ ] TPOT
- [ ] mémoire GPU
- [ ] KV cache
- [ ] OOM/timeout

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
