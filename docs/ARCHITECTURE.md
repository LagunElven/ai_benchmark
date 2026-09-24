# Architecture

## Périmètre actuel

Le benchmark sépare quatre dimensions : qualité de code, capacité de réparation,
documents/OCR et performances de serving. Le runner couvre la découverte et la validation
des tâches, les modes `one-shot` et `repair`, les workspaces propres, l'isolation des tests
cachés et la persistance des résultats. Le serving reste un parcours indépendant des runs
de qualité afin que leurs métriques ne soient pas confondues.

## Composants

- `runner/config.py` charge et valide `benchmark.yaml`.
- `runner/discovery.py` découvre et valide les fichiers `task.yaml`.
- `runner/workspace.py` copie uniquement le workspace visible de la tâche dans un dossier neuf.
- `runner/prompting.py` construit un contexte textuel à partir du prompt et du workspace.
- `runner/context_budget.py` compte le chat template local quand disponible et vérifie
  fenêtre, sortie réservée et marge sans traiter une estimation comme exacte.
- `runner/client.py` isole l'accès au modèle derrière une interface commune.
- `runner/changes.py` applique les modifications structurées en empêchant toute sortie du workspace.
- `runner/validation.py` exécute des commandes sans passer par un shell.
- `runner/execution.py` orchestre un run et calcule les métriques brutes.
- `runner/document_dataset.py` génère les sources documentaires, rendus PGM et variantes
  reproductibles sans dépendance OCR native.
- `runner/document_metrics.py` calcule CER/WER et les métriques de sortie structurée sans
  les réduire à un score unique.
- `runner/metric_extractors.py` exécute le scoring structuré après le feedback du modèle,
  en gardant les vérités terrain sous `private-tests/`.
- `runner/legacy.py` valide les manifestes legacy, compare des vecteurs d'équivalence et
  détecte les compilateurs natifs sans les exécuter implicitement.
- `runner/context_dataset.py` génère les variantes de contexte, conserve un manifeste de
  tokenisation et calcule la précision/rappel des fichiers pertinents.
- `runner/catalogue.py` vérifie la couverture entre l'inventaire des scénarios et les
  définitions de tâches réellement découvrables.
- `runner/gpu_preflight.py` fige les configurations, les révisions de tâches et les
  empreintes des seuls fichiers model-visible avant une campagne distante.
- `runner/remote_gpu.py` échantillonne `nvidia-smi` sur la machine d'inférence par une
  connexion SSH séparée et écrit les observations JSONL près du résultat de campagne.
- `runner/results.py` écrit un résultat immuable par run et un index JSONL append-only.
- `scripts/run_quality_campaign.py` orchestre les campagnes qualité, conserve leur
  progression et permet de reprendre seulement une campagne dont l'empreinte complète
  des entrées correspond.
- `runner/cohort.py` réutilise les exécutions qualité pour faire travailler un groupe fini
  d'agents sur une file de tâches FIFO ; il mesure séparément l'activité des agents et le
  chevauchement réel des appels modèle.
- `scripts/run_cohort_pilot.py` valide un plan de cohorte, choisit le profil modèle/serving,
  lance un seul niveau de concurrence et persiste un résultat dédié sans modifier les
  artefacts des anciennes campagnes.
- `serving/client.py` appelle un endpoint OpenAI-compatible en streaming SSE et capture
  TTFT, usage, erreurs OOM/timeout et métriques serveur exposées par headers.
- `serving/benchmark.py` construit la matrice concurrence/contexte/préfixe, exécute les
  lots concurrents et persiste une campagne serving indépendante des runs qualité.
- `serving/metrics.py` calcule les distributions p50/p95, TPOT, tok/s par utilisateur et
  débit agrégé sans réduire les dimensions à un score opaque.
- `serving/resources.py` échantillonne `nvidia-smi` et la mémoire hôte si disponibles ;
  ces séries locales restent attribuées au poste runner. Le collecteur SSH distant est
  facultatif et conserve une source distincte.

Le pilote de cohorte complète ces dimensions sans les fusionner : les validations qualité
restent les résultats de chaque tâche, tandis que la durée de cohorte et le débit décrivent
la performance applicative. Les métriques GPU distantes sont échantillonnées en parallèle
uniquement si une cible SSH est fournie ; elles ne remplacent jamais les ressources locales.

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

Le modèle ne reçoit que `prompt.md` et le contenu de son workspace modèle-visible. Le dossier
`private-tests/`, les résultats historiques et les autres tâches ne sont jamais sérialisés
dans le contexte. Les validations publiques s'exécutent dans ce workspace. Les validations
cachées travaillent sur une copie séparée, dans laquelle `private-tests/<task-id>/` est injecté
après le patch du modèle ; cette copie est supprimée à la fin de la validation. Les commandes
proviennent de la définition versionnée de la tâche et sont lancées directement, avec une
liste d'arguments, un répertoire de travail borné et un timeout. L'isolation forte par
conteneur, notamment contre un code de test malveillant, reste une évolution ultérieure.

## Résultats

Chaque run produit `results/raw/<run-id>/result.json`, la réponse brute du modèle et les logs
de validation. `results/raw/runs.jsonl` est un index append-only. Les rapports placés dans
`results/reports/` sont toujours dérivables de ces données brutes.

Les valeurs de matériel, modèle exact, quantification et configuration de serving sont
déclarées dans `benchmark.yaml`. Les valeurs inconnues restent explicitement `null`; elles ne
sont ni devinées ni remplacées par des valeurs implicites.

Pour une campagne distante, le runner et les tests cachés restent sur le poste de contrôle.
La machine louée expose l'endpoint d'inférence au runner ; `scripts/capture_gpu_environment.py`
enregistre son empreinte avant le smoke et `scripts/run_quality_campaign.py` conserve l'index
des runs qualité associés à l'identifiant de campagne. Les ressources du poste runner et
celles du GPU distant restent identifiées par des sources séparées ; le collecteur SSH
optionnel écrit ses observations brutes près du résultat de chaque campagne.
