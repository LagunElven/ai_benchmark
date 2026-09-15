# Changelog sémantique du benchmark

Ce fichier recense uniquement les changements susceptibles d'affecter la comparabilité.

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
