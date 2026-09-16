# Variantes long-context

La milestone 8 conserve un seul workspace fonctionnel et génère à la demande
des distracteurs contrôlés. Le générateur ne modifie jamais les fichiers source
et refuse un dossier de sortie non vide.

~~~powershell
python scripts/generate_context_variants.py tasks/context/CTX-01/workspace .tmp/context-ctx01 --relevant-file src/billing.py
~~~

Les tailles par défaut sont 10k, 30k, 60k, 100k, 150k et 200k tokens. Pour
chaque variante, context-manifest.json enregistre :

- la cible et le nombre réel de tokens ;
- le tokenizer utilisé, ou fallback:regex lorsque aucun tokenizer optionnel
  n'est installé ;
- le seed ;
- la liste et l'empreinte SHA-256 de chaque fichier ;
- les fichiers pertinents attendus et le répertoire de distracteurs.

Si tiktoken est installé, le script peut recevoir un encodage avec
--tokenizer. Pour une comparaison scientifique, il faut utiliser le tokenizer
exact du modèle évalué et conserver sa révision dans les métadonnées de run.
L'estimation regex est utile pour préparer une campagne, mais ne doit pas être
confondue avec un compte exact de tokens modèle.

~~~powershell
python scripts/score_context.py --manifest .tmp/context-ctx01/ctx-10k/context-manifest.json --modified-file src/billing.py
~~~

Le scorer sépare précision des fichiers pertinents, rappel et fichiers inutiles.
Un patch rapide qui touche de nombreux distracteurs reste donc mesurable comme
une perte de précision, indépendamment de la réussite fonctionnelle.

## Tâches de la milestone 9

CTX-01 reste la source du scénario à environ 10k tokens. CTX-02 à CTX-06
matérialisent le même workspace et le même bug à environ 30k, 60k, 100k, 150k et
200k tokens. Chaque workspace conserve `src/billing.py` comme unique fichier
pertinent et contient uniquement des distracteurs générés avec le seed
`20260915`, ainsi qu'un `context-manifest.json` versionné.

Les cinq variantes ont des validateurs publics et cachés propres. La réussite
fonctionnelle, le nombre de tokens, la précision et le rappel des fichiers
modifiés restent des métriques distinctes ; les valeurs réelles sont celles du
manifeste et dépendent du tokenizer choisi pour la campagne.
