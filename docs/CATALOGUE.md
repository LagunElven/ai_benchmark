# Catalogue qualité

`catalogue.yaml` est la source de vérité de la cible de la milestone 9 : 74 tâches
réparties entre Java, Spring, Axon, Web, legacy, documents, long-context et E2E. Chaque
entrée porte un statut :

- `implemented` : un dossier `tasks/**/<id>` est découvert et possède une validation
  publique et cachée déterministe ;
- `planned` : le scénario est réservé dans le catalogue mais n'est pas encore exécutable ;
- `generated` : réservé aux variantes produites par un générateur, sans masquer une tâche
  qualité manquante.

La commande suivante vérifie que les tâches implémentées existent, possèdent leurs
validateurs public/caché et qu'aucune tâche exécutée n'est absente de l'inventaire :

~~~powershell
python scripts/check_catalogue.py
~~~

La milestone 9 fournit 74 tâches exécutables (les sept smoke historiques, les
variantes long-context matérialisées, les scénarios E2E et les tâches core/full déjà
présentes). Les 74 scénarios restent listés comme inventaire complet. Une campagne
complète ne doit utiliser que les entrées
`implemented` et publier la révision de chaque `task.yaml`.
