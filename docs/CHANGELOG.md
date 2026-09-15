# Changelog sémantique du benchmark

Ce fichier recense uniquement les changements susceptibles d'affecter la comparabilité.

## 0.2.0 — Isolation des tests cachés

- Ajout d'un workspace validator-visible distinct.
- Injection de `private-tests/<task-id>/` uniquement après le patch du modèle.
- Suppression systématique du workspace contenant les tests cachés.
- Tests automatisés de non-divulgation et d'injection contrôlée.

## 0.1.0 — Fondation

- Définition initiale des schémas de configuration, de tâche et de résultat.
- Définition du protocole de réponse `file_changes_v1`.
- Mode `one-shot` avec validation publique ; tests cachés et boucle `repair` non encore actifs.
