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
- un lot de warmup à la concurrence du cas, puis 20 lots mesurés par cas dans
  les profils complets (les profils smoke restent courts).

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
- tokens d'entrée/sortie avec leur provenance (`provider_usage`, tokenizer ou
  `fallback:regex`), échecs, flux SSE incomplets, timeouts et OOM ;
- métriques KV-cache lorsqu'elles sont exposées par les headers
  `X-KV-Cache-*` ;
- échantillons de ressources chaque seconde et maxima observés pour GPU, CPU et
  mémoire hôte. Les échantillons décrivent explicitement le poste du runner,
  pas un serveur d'inférence distant.

Les métriques absentes sont représentées par `null`, une liste vide ou
`available: false`. Le runner ne déduit pas une consommation GPU et ne transforme
pas une absence de métrique en zéro. `nvidia-smi` et `psutil` sont utilisés lorsqu'ils
sont disponibles ; le benchmark reste exécutable sans eux.

Les percentiles utilisent une règle nearest-rank déterministe. Chaque mesure
indique son nombre d'échantillons et marque le p95 comme exploratoire sous 100
requêtes. Les requêtes échouées ou tronquées restent dans le dénominateur du
taux d'échec, mais pas dans les distributions de latence ou débit réussi. Une
réponse JSON non-streamée ne fournit pas de TTFT observable : cette valeur reste
`null` au lieu d'être remplacée par la latence totale.

## Profils serving BF16 et Q8 exécutés

La campagne Q8 historique a été exécutée le 22 septembre 2026 avec
`campaigns/gpu/serving-qwen-rtx-pro-6000-q8-full.yaml`. Elle reprend la matrice
BF16 : 1/2/5/10 utilisateurs, contextes 8k/32k/64k/100k/200k, modes `cold` et
`shared-prefix`, un lot de warmup et trois répétitions. Les 40 cas et 540
requêtes Q8 ont abouti sans échec. Les nouveaux profils complets utilisent 20
lots mesurés ; les artefacts passés conservent leur configuration d'origine.

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

## Profils prévus Q8/FP8 — shared-prefix, thinking medium

Les nouveaux profils dédiés sont :

- `campaigns/gpu/serving-qwen-rtx-pro-6000-q8-shared-prefix-medium-thinking.yaml`
- `campaigns/gpu/serving-qwen-rtx-pro-6000-fp8-shared-prefix-medium-thinking.yaml`

Ils utilisent la même RTX PRO 6000, vLLM 0.29.0, le tokenizer officiel Qwen, le
KV cache FP8, les concurrences 1/2/5/10, les contextes 8k/32k/64k/100k/200k et
20 répétitions. Seuls les artefacts de poids/dtypes diffèrent ; le checkpoint Q8
reste tiers, donc l'analyse est opérationnelle et non une comparaison contrôlée de
quantification. Chaque profil ne contient que `shared-prefix`, active le prefix
caching, et envoie `enable_thinking: true` avec `reasoning_effort: medium`.
Cela représente 20 cas et 1 800 requêtes mesurées par variante. Le plafond de
sortie reste à 256 tokens pour cette matrice de débit ; ces mesures ne remplacent
pas les évaluations qualité.

Exécuter après le smoke serveur, en sélectionnant explicitement le fichier voulu :

```powershell
python scripts/run_serving_benchmark.py `
  --config campaigns/gpu/serving-qwen-rtx-pro-6000-fp8-shared-prefix-medium-thinking.yaml
python scripts/run_serving_benchmark.py `
  --config campaigns/gpu/serving-qwen-rtx-pro-6000-q8-shared-prefix-medium-thinking.yaml
```

Ces profils futurs ne changent pas les résultats du 22 septembre : Q8 historique
reste mesuré avec deux modes de préfixe, trois répétitions et thinking désactivé.
Le profil Q8 dédié permettra une comparaison serving appariée au FP8 sous les
nouveaux réglages.

## Profil préparé DFlash2 — cible FP8, shared-prefix

`campaigns/gpu/serving-qwen-rtx-pro-6000-fp8-dflash2-shared-prefix-medium-thinking.yaml`
reprend la matrice FP8 (20 cas, 20 répétitions par cas) et ajoute le draft BF16
DFlash2 à la même cible FP8. Le checkpoint draft est épinglé à la révision
`015e795645c74b1a0eeef3b570031fb62e769bc5` dans le plan C-019 ; le profil ne mesure
donc pas un autre modèle cible ni une nouvelle quantification.

Avant la matrice complète, smoke de chargement/génération, vérification de l'acceptance
DFlash2 et des hits prefix-cache. Un ticket vLLM a documenté zéro hit de prefix cache
avec speculative decoding sur certains déploiements Qwen3.8 hybrides ; tant que les hits
ne sont pas confirmés sur vLLM 0.29.0 et cette RTX PRO, les mesures ne sont pas à
interpréter comme une comparaison shared-prefix valide. Le détail d'exécution et les
commandes sont dans [`docs/GPU_CAMPAIGN_PLAN.md`](GPU_CAMPAIGN_PLAN.md).

## Configuration et comparabilité

Le fichier est validé par `schemas/serving-config.schema.json`, le résultat par
`schemas/serving-campaign-result.schema.json`. Le modèle exact, la révision, le
dtype/quantification, le matériel et la configuration de serving doivent être
conservés dans les métadonnées de campagne. Une comparaison contrôlée ne change
qu'une dimension à la fois ; une matrice où plusieurs champs diffèrent doit être
étiquetée comme comparaison opérationnelle.
