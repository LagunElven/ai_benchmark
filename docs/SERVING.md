# Serving benchmark

Le benchmark serving est séparé des tâches de qualité. Il mesure la capacité
d'un endpoint OpenAI-compatible sans dépendre des détails internes d'un moteur
spécifique.
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

## Pilote de cohorte agentique

La matrice serving ci-dessus maintient un nombre fixe de requêtes simultanées. Le pilote
`campaigns/cohort/qwen3.8-agentic-pilot.yaml` répond à une autre question : combien de temps
faut-il à un groupe fini d'agents pour terminer un même lot de vraies tâches, quand chaque
agent prend la suivante dès que sa tâche et ses validations sont finies ? La concurrence des
appels modèle varie donc naturellement ; elle est mesurée séparément de celle des agents.

Le plan comprend 18 tâches en mode `repair`, combinant les sept tâches de la smoke suite avec
des exemples supplémentaires Axon, COBOL, Delphi, ABAL, WLanguage, OCR scanné, contexte 60k
et E2E. Chaque tâche dispose de son workspace propre et passe par les mêmes validateurs
publics/cachés que le runner qualité. Le modèle ne reçoit jamais les tests cachés.

Afficher le plan sans contacter le serveur :

```powershell
python scripts/run_cohort_pilot.py --benchmark-config benchmark.qwen3.8-fp8-shared-prefix-medium-thinking.yaml --plan-only
```

Les valeurs `agent_counts` du plan sont les points de référence de la grille par défaut.
`--agents` accepte également n'importe quel entier compris entre 1 et la plus petite de
ces deux limites : le nombre de tâches du plan et `serving.max_num_seqs`. Pour ce pilote
de 18 tâches, la configuration vLLM courante autorise donc des points intermédiaires comme
6 ou 8 agents. `--plan-only` affiche aussi la limite maximale autorisée.

Exécuter un lot à 6 agents :

```powershell
python scripts/run_cohort_pilot.py `
    --benchmark-config benchmark.qwen3.8-fp8-dflash2-shared-prefix-medium-thinking.yaml `
    --agents 6
```

Pour 8 agents, remplacer `6` par `8`. Les valeurs configurées dans le plan restent
enregistrées comme points de référence ; chaque manifeste conserve séparément le nombre
effectivement utilisé (`agent_count`).

Chaque commande est une campagne indépendante. Pour des points comparables, redémarrer le
moteur (ou vider explicitement son cache) avant chaque campagne afin de repartir du même état
de cache ; appliquer le même protocole de warmup, utiliser le même endpoint et éviter toute
autre charge pendant le lot. Chaque run
persiste sous `results/raw/cohort/`, tandis que les résultats détaillés des tâches restent
dans le stockage brut standard. En cas d'interruption, les runs déjà achevés restent
conservés, mais la cohorte incomplète n'a pas de `campaign.json` final.

La configuration déclare le prefix caching, mais ce pilote ne vérifie pas les hits du cache.
En particulier, pour DFlash2, les hits doivent rester considérés comme inconnus tant que le
serveur ne les expose pas explicitement.

Le rapport distingue makespan, durée des tâches, réussite, tâches réussies/heure, appels et
tokens, temps agrégé de requête, nombre moyen/maximal de requêtes modèle simultanées et nombre
maximal d'agents occupés. Les validations locales font partie du temps tâche mais ne sont pas
des requêtes modèle. Aucune mesure GPU n'est prélevée sur le poste local ni extrapolée vers le
serveur ; les métriques GPU distantes non exposées restent indisponibles.

Ce protocole est une cohorte finie à boucle fermée, sans délai de réflexion artificiel ni
arrivées externes. Il mesure l'effet d'un travail qui se termine et libère ses agents ; il ne
prédit pas à lui seul le débit sous un flux constant saturant. La session du 23 septembre a
exécuté 13 cohortes DFlash2 aux niveaux 1/4/5/6/8/10 ; la synthèse des répétitions et de leurs
limites est dans [`docs/COHORT_SESSION_2026-09-23.md`](COHORT_SESSION_2026-09-23.md). Les
résultats favorisent provisoirement 5–6 agents pour cette charge, sans établir un optimum :
la sortie et les reprises varient, les essais par cellule restent peu nombreux, et les hits
du prefix cache comme les métriques GPU distantes ne sont pas enregistrés.

Le client du runner qualité utilise une réponse non-streamée : le pilote mesure la durée
complète de chaque requête modèle, mais ne mesure pas la TTFT. Il ne la reconstitue pas à
partir de la latence totale.

## Configuration et comparabilité

Le fichier est validé par `schemas/serving-config.schema.json`, le résultat par
`schemas/serving-campaign-result.schema.json`. Le modèle exact, la révision, le
dtype/quantification, le matériel et la configuration de serving doivent être
conservés dans les métadonnées de campagne. Une comparaison contrôlée ne change
qu'une dimension à la fois ; une matrice où plusieurs champs diffèrent doit être
étiquetée comme comparaison opérationnelle.

## Comparaison vLLM / SGLang pour Qwen3.8-27B

Le client du benchmark utilise l'API OpenAI-compatible ; les profils SGLang peuvent
donc réutiliser le protocole HTTP et la matrice de requêtes. Les options de lancement,
versions et réglages internes au moteur restent spécifiques et doivent être enregistrés
dans chaque profil. La matrice et son ordre de reprise sont décrits dans
[`docs/GPU_CAMPAIGN_PLAN.md`](GPU_CAMPAIGN_PLAN.md).

Pour les comparaisons partagées, le seul mode de préfixe visé est `shared-prefix`.
L'option de cache activée n'est pas une preuve que des tokens ont été réutilisés :
confirmer les hits par les métriques du serveur. SGLang expose ses métriques Prometheus
avec `--enable-metrics`; relever des compteurs/cache hits côté serveur avant et après la
campagne. Le client actuel ne scrape pas automatiquement les métriques Prometheus propres
à SGLang. Les statistiques GPU prélevées sur le poste de benchmark demeurent des métriques
locales et ne doivent jamais être présentées comme une utilisation du serveur distant.

Les cohortes sont bruitées par la longueur des sorties et les reprises : exécuter au moins
trois répétitions par cellule de concurrence utilisée dans une comparaison. Garder la même
sélection et révision de tâches, le même seed, les mêmes prompts, réglages de raisonnement,
limites de contexte/sortie, matériel et conditions de warmup. Comparer les moteurs par paires
équivalentes ; toute différence nécessaire de paramètre propre à un moteur doit être
consignée.

Pour Qwen3.8 + DFlash2, conserver le KV cache FP8 même avec une cible dont les poids sont
NVFP4 : poids NVFP4 et KV cache NVFP4 ne sont pas synonymes. SGLang documente une
incompatibilité signalée entre DFlash et le KV cache NVFP4 ; voir l'issue référencée dans le
plan GPU. Avant les campagnes SGLang complètes, le smoke doit vérifier l'API, le raisonnement
medium, les appels d'outils/protocole, les contextes, les hits cache et l'acceptance DFlash2
le cas échéant.
