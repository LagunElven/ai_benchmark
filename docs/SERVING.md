# Serving benchmark

Le benchmark serving est séparé des tâches de qualité. Il mesure la capacité
d'un endpoint OpenAI-compatible sans dépendre des détails internes de vLLM.
Les profils qui déclarent un tokenizer Hugging Face utilisent ce tokenizer exact
pour construire les tailles de contexte ; le résultat conserve la révision et la
méthode de comptage.
L'adaptateur utilise `POST /chat/completions` en streaming SSE ; vLLM, un autre
serveur compatible ou un faux endpoint local peuvent donc être comparés avec le
même protocole.

## Matrice reproductible

La matrice par défaut se trouve dans `serving/config.yaml` :

- concurrence : 1, 2, 5 et 10 requêtes simultanées ;
- contexte : 8k, 32k, 64k, 100k et 200k tokens estimés ;
- préfixes : `cold` et `shared-prefix` ;
- une requête de warmup, puis trois répétitions par cas.

Afficher les 40 cas sans contacter le serveur :

```powershell
python scripts/run_serving_benchmark.py --plan-only
```

Exécuter une campagne contre le endpoint configuré :

```powershell
python scripts/run_serving_benchmark.py
```

Pour les profils Qwen, installer d'abord le support tokenizer :

```powershell
python -m pip install -e ".[serving]"
```

Pendant l'exécution, le script affiche le cas courant et son état de fin. Une
campagne interrompue avant sa fin ne produit pas de résultat complet.

Le résultat est écrit dans `results/raw/serving/<run-id>/campaign.json` et ajouté
à `results/raw/serving/campaigns.jsonl`. Chaque résultat conserve la configuration,
le commit Git, les cas et chaque requête ; les warmups ne sont pas inclus dans les
mesures de latence et de débit.

## Métriques

Par cas, le résultat sépare :

- TTFT, latence totale, durée de génération et TPOT/inter-token en p50/p95 ;
- tokens/s par utilisateur, débit agrégé et requêtes/s ;
- tokens d'entrée/sortie, échecs, taux d'échec, timeouts et OOM ;
- métriques KV-cache lorsqu'elles sont exposées par les headers
  `X-KV-Cache-*` ;
- échantillons avant/après pour mémoire GPU, utilisation GPU et mémoire hôte.

Les métriques absentes sont représentées par `null`, une liste vide ou
`available: false`. Le runner ne déduit pas une consommation GPU et ne transforme
pas une absence de métrique en zéro. `nvidia-smi` et `psutil` sont utilisés lorsqu'ils
sont disponibles ; le benchmark reste exécutable sans eux.

Les percentiles utilisent une règle nearest-rank déterministe. Les requêtes
échouées restent dans le dénominateur du taux d'échec, mais pas dans les
distributions de latence ou de débit réussi.

## Profils serving BF16 et Q8 exécutés

La campagne Q8 complète a été exécutée le 22 septembre 2026 avec
`campaigns/gpu/serving-qwen-rtx-pro-6000-q8-full.yaml`. Elle reprend la matrice
BF16 : 1/2/5/10 utilisateurs, contextes 8k/32k/64k/100k/200k, modes `cold` et
`shared-prefix`, un warmup et trois répétitions. Les 40 cas et 540 requêtes Q8
ont abouti sans échec.

La campagne BF16 disponible comprend une campagne complète de 20 cas en
`shared-prefix` et un smoke séparé de 12 cas couvrant `cold` et `shared-prefix`
uniquement pour les concurrences 1/5 et les contextes 8k/32k/64k. Les cellules
BF16 `cold` manquantes ne doivent pas être extrapolées ; les futurs rapports
doivent les afficher comme « non testées ».

Le profil conserve `enable_thinking: false` afin de mesurer le moteur et le
cache plutôt que la longueur variable du raisonnement. Le détail des résultats
et de la comparaison se trouve dans
[`docs/GPU_SESSION_2026-09-22.md`](GPU_SESSION_2026-09-22.md).

Les métriques de ressource capturées par le runner sont celles de la machine
qui exécute le benchmark. Pour ces campagnes distantes, elles décrivent donc
le poste local lorsque `nvidia-smi` est lancé côté runner, pas le GPU distant.
Les métriques `server_metrics` et KV-cache distantes n'étaient pas exposées par
l'endpoint ; elles restent absentes plutôt que d'être déduites.

Sur l'instance utilisée le portail Caddy occupe le port distant `8000` ; vLLM
Q8 écoute sur `8001` et le tunnel SSH mappe le port local `8000` vers ce port.

## Configuration et comparabilité

Le fichier est validé par `schemas/serving-config.schema.json`, le résultat par
`schemas/serving-campaign-result.schema.json`. Le modèle exact, la révision, le
dtype/quantification, le matériel et la configuration de serving doivent être
conservés dans les métadonnées de campagne. Une comparaison contrôlée ne change
qu'une dimension à la fois ; une matrice où plusieurs champs diffèrent doit être
étiquetée comme comparaison opérationnelle.
