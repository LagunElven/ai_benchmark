# Protocole d'exécution

## Préconditions

1. Valider `benchmark.yaml` et `task.yaml` avec leurs schémas.
2. Résoudre tous les chemins relativement à la racine du dépôt.
3. Créer un identifiant de run unique.
4. Copier `tasks/<catégorie>/<id>/workspace/` vers un nouveau workspace modèle-visible.
5. Copier seulement les includes publics explicitement déclarés par la tâche.
6. Ne jamais copier `private-tests/`, `results/` ou une autre tâche dans le workspace modèle-visible.

## Mode one-shot

1. Lire `prompt.md` et les fichiers texte du workspace dans la limite configurée.
2. Appeler une fois l'adaptateur de modèle.
3. Conserver la réponse brute avant de tenter de l'appliquer.
4. Valider et appliquer les modifications uniquement dans le workspace isolé.
5. Exécuter une seule fois chaque validateur public avec son timeout.
6. Si des validateurs cachés sont déclarés, copier le workspace modèle-visible dans un second
   workspace validator-visible et y injecter `private-tests/<task-id>/`.
7. Exécuter les validateurs cachés uniquement dans cette seconde copie, puis la supprimer.
8. Calculer le diff et les métriques disponibles.
9. Écrire un nouveau résultat JSON, puis l'ajouter à l'index JSONL.
10. Supprimer le workspace modèle-visible, sauf option explicite de diagnostic.

## Mode repair

Le mode est déclaré dans le schéma pour versionner les tâches, mais sa boucle d'exécution
appartient au milestone 4. Une demande `repair` doit échouer explicitement tant que cette
fonctionnalité n'est pas activée ; elle ne doit jamais être transformée silencieusement en
`one-shot`.

## Tests cachés

Une tâche qui déclare des validations cachées doit fournir `private-tests/<task-id>/`. Le runner
refuse les liens symboliques et les collisions entre fichiers cachés et fichiers du modèle.
Le modèle ne reçoit jamais cette arborescence ; un test automatisé vérifie à la fois son absence
des messages et sa présence uniquement dans le workspace validator-visible. Les tests cachés
ne sont pas conservés dans le workspace après le run.

## Échecs

Une erreur de modèle, de protocole de réponse, d'application des changements, de lancement
d'un validateur ou un timeout doit être enregistrée dans le résultat. Un run ayant démarré ne
doit pas écraser un résultat précédent et doit conserver les artefacts déjà produits.
