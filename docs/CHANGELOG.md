# Changelog sémantique du benchmark

Ce fichier recense uniquement les changements susceptibles d'affecter la comparabilité.

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
