# Architecture

## Périmètre initial

La fondation sépare quatre dimensions : qualité de code, capacité de réparation,
documents/OCR et performances de serving. Le runner de Phase 1 implémente la découverte,
le mode `one-shot`, un client OpenAI-compatible, des workspaces propres, la validation
publique et la persistance des résultats. La boucle de réparation, l'injection des tests
cachés et le serving GPU sont des extensions distinctes.

## Composants

- `runner/config.py` charge et valide `benchmark.yaml`.
- `runner/discovery.py` découvre et valide les fichiers `task.yaml`.
- `runner/workspace.py` copie uniquement le workspace visible de la tâche dans un dossier neuf.
- `runner/prompting.py` construit un contexte textuel à partir du prompt et du workspace.
- `runner/client.py` isole l'accès au modèle derrière une interface commune.
- `runner/changes.py` applique les modifications structurées en empêchant toute sortie du workspace.
- `runner/validation.py` exécute des commandes sans passer par un shell.
- `runner/execution.py` orchestre un run et calcule les métriques brutes.
- `runner/results.py` écrit un résultat immuable par run et un index JSONL append-only.

## Protocole de réponse `file_changes_v1`

Le modèle reçoit les fichiers texte visibles et retourne un objet JSON :

```json
{
  "changes": [
    {"path": "src/example.py", "content": "contenu complet du fichier"}
  ]
}
```

Les chemins absolus, les traversées `..` et les liens symboliques sortant du workspace sont
refusés. Ce protocole initial privilégie une application déterministe et sûre. D'autres
protocoles pourront être ajoutés sans modifier les tâches.

## Frontières de sécurité

Le modèle ne reçoit que `prompt.md` et le contenu de `workspace/`. Le dossier
`private-tests/`, les résultats historiques et les autres tâches ne sont jamais sérialisés
dans le contexte. Les commandes de validation proviennent de la définition versionnée de la
tâche et sont lancées directement, avec une liste d'arguments, un répertoire de travail borné
et un timeout. L'isolation forte par conteneur appartient au milestone 3.

## Résultats

Chaque run produit `results/raw/<run-id>/result.json`, la réponse brute du modèle et les logs
de validation. `results/raw/runs.jsonl` est un index append-only. Les rapports placés dans
`results/reports/` sont toujours dérivables de ces données brutes.

Les valeurs de matériel, modèle exact, quantification et configuration de serving sont
déclarées dans `benchmark.yaml`. Les valeurs inconnues restent explicitement `null`; elles ne
sont ni devinées ni remplacées par des valeurs implicites.
