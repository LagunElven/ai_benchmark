# Protocole d'exécution

## Préconditions

1. Valider `benchmark.yaml` et `task.yaml` avec leurs schémas.
2. Résoudre tous les chemins relativement à la racine du dépôt.
3. Créer un identifiant de run unique.
4. Copier `tasks/<catégorie>/<id>/workspace/` vers un nouveau workspace temporaire.
5. Ne jamais copier `private-tests/`, `results/` ou une autre tâche dans ce workspace.

## Mode one-shot

1. Lire `prompt.md` et les fichiers texte du workspace dans la limite configurée.
2. Appeler une fois l'adaptateur de modèle.
3. Conserver la réponse brute avant de tenter de l'appliquer.
4. Valider et appliquer les modifications uniquement dans le workspace isolé.
5. Exécuter une seule fois chaque validateur public avec son timeout.
6. Calculer le diff et les métriques disponibles.
7. Écrire un nouveau résultat JSON, puis l'ajouter à l'index JSONL.
8. Supprimer le workspace temporaire, sauf option explicite de diagnostic.

## Mode repair

Le mode est déclaré dans le schéma pour versionner les tâches, mais sa boucle d'exécution
appartient au milestone 4. Une demande `repair` doit échouer explicitement tant que cette
fonctionnalité n'est pas activée ; elle ne doit jamais être transformée silencieusement en
`one-shot`.

## Tests cachés

Le milestone 2 n'injecte aucun test caché. Si une tâche en déclare, le résultat final reste
`incomplete` après la validation publique. Le milestone 3 introduira un espace
validator-visible distinct et un test automatisé prouvant que le modèle ne peut pas lire les
tests cachés.

## Échecs

Une erreur de modèle, de protocole de réponse, d'application des changements, de lancement
d'un validateur ou un timeout doit être enregistrée dans le résultat. Un run ayant démarré ne
doit pas écraser un résultat précédent et doit conserver les artefacts déjà produits.

