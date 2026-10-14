# Campagne SGLang Qwen3.8 NVFP4 + DFlash2 — DGX Spark

Ce playbook documente C-025 sur un DGX Spark / GB10 loué. C'est une campagne
opérationnelle distincte de C-023 (RTX PRO 6000) et de C-012 (vLLM / NVFP4) :
le matériel, l'image SGLang et les réglages de mémoire diffèrent. Les profils ne
modifient ni les tâches ni leurs validateurs.

La recette fixe le checkpoint NVIDIA NVFP4 à
`dbb8f445b3145f8a4c18ddc769f032d57d32867c`, le tokenizer à
`1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` et le draft
`incoai/Qwen3.8-27B-DFlash2` à `015e795645c74b1a0eeef3b570031fb62e769bc5`.
Elle emploie le KV cache FP8, le raisonnement `medium`, le contexte natif
262 144, le backend FlashInfer et `--mem-fraction-static 0.80` pour la mémoire
unifiée du GB10. L'image SGLang DFlash2 est épinglée par digest dans les profils
et le script de lancement. Le cookbook SGLang rapporte la validation de la
cellule NVFP4 + DFlash2 sur GB10 avec SGLang 0.5.19 et recommande FlashInfer et
0.80 sur Spark. Le profil épingle séparément une image upstream `dev` dont le
build DFlash2 et le chemin de tête NVFP4 sont documentés sur GB10 ; l'image
épinglée a passé le smoke séquentiel et le pilote de cohorte jusqu'à dix requêtes
simultanées. La qualité complète et le serving restent à exécuter. Voir le
[cookbook Qwen3.8 de SGLang](https://github.com/sgl-project/sglang/blob/main/docs/cookbook/autoregressive/Qwen/Qwen3.8-27B.mdx)
et le [signalement SGLang sur la reproductibilité DFlash2/GB10](https://github.com/sgl-project/sglang/issues/39597).

## Profils C-025

| Usage | Fichier |
|---|---|
| Qualité, thinking medium | [`benchmark.qwen3.8-sglang-nvfp4-dflash2-dgx-spark-medium-thinking.yaml`](../benchmark.qwen3.8-sglang-nvfp4-dflash2-dgx-spark-medium-thinking.yaml) |
| Serving shared-prefix | [`serving-qwen-sglang-nvfp4-dflash2-dgx-spark-shared-prefix.yaml`](../campaigns/gpu/serving-qwen-sglang-nvfp4-dflash2-dgx-spark-shared-prefix.yaml) |
| Cohorte complète, 18 tâches | [`qwen3.8-sglang-nvfp4-dflash2-dgx-spark-agentic-pilot.yaml`](../campaigns/cohort/qwen3.8-sglang-nvfp4-dflash2-dgx-spark-agentic-pilot.yaml) |
| Smoke d'isolation, 10 tâches | [`qwen3.8-sglang-nvfp4-dflash2-dgx-spark-smoke.yaml`](../campaigns/cohort/qwen3.8-sglang-nvfp4-dflash2-dgx-spark-smoke.yaml) |
| Lancement serveur sur le Spark | [`start_sglang_dgx_spark_dflash2.sh`](../scripts/start_sglang_dgx_spark_dflash2.sh) |

Le serving reprend la matrice commune : 20 cas `shared-prefix`, concurrents
1/2/5/10, contextes 8k/32k/64k/100k/200k, un warmup et 20 répétitions (1 800
requêtes mesurées). Elle ne démarre qu'après la validation de l'isolation DFlash2
à 1, 4 et 10 requêtes simultanées observées. Le pilote complet utilise 18 tâches,
les niveaux 1/4/5/6/8/10 agents et trois répétitions par niveau.

## Préparer le DGX Spark

Capturer d'abord l'hôte loué :

```bash
uname -a
uname -m
nvidia-smi
cat /proc/meminfo | head
docker version
docker info | grep -i -E 'cdi|nvidia'
```

Sur Spark, l'architecture attendue est `aarch64` et le GPU `NVIDIA GB10`. Sa
mémoire est unifiée ; `nvidia-smi` peut afficher `Not Supported` pour la mémoire
GPU. Conserver `/proc/meminfo` et les mesures de télémétrie distante. Ne pas
traiter les chiffres `memory.total` comme de la VRAM discrète.

Télécharger les snapshots dans le volume persistant de l'instance. Si les modèles
sont déjà en cache à ces révisions, ne pas les télécharger une seconde fois :

```bash
mkdir -p /workspace/models
export HF_HOME=/workspace/models
hf download nvidia/Qwen3.8-27B-NVFP4 \
  --revision dbb8f445b3145f8a4c18ddc769f032d57d32867c \
  --local-dir /workspace/models/Qwen3.8-27B-NVFP4
hf download Qwen/Qwen3.8-27B tokenizer.json tokenizer_config.json vocab.json merges.txt chat_template.jinja \
  --revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 \
  --local-dir /workspace/models/Qwen3.8-27B
hf download incoai/Qwen3.8-27B-DFlash2 \
  --revision 015e795645c74b1a0eeef3b570031fb62e769bc5 \
  --local-dir /workspace/models/Qwen3.8-27B-DFlash2
```

Le lanceur utilise le CDI Docker `--device nvidia.com/gpu=all`, le réseau hôte,
et lie l'API distante à `127.0.0.1:8001`. Il ne supprime pas de conteneur
existant. S'il existe déjà un serveur sur ce port, inspecter son état avant de
le remplacer. L'image par défaut est épinglée par digest ; le script affiche
l'ID d'image et les RepoDigests avant le démarrage.

```bash
bash scripts/start_sglang_dgx_spark_dflash2.sh
docker logs -f sglang-c025
```

Si les fichiers du dépôt ne sont pas présents sur le Spark, copier le script
depuis le runner avec `scp`, ou lancer la commande équivalente depuis les
arguments `launch_command` des profils. Le serveur doit annoncer READY et
accepter une requête courte avant de poursuivre.

## Tunnel et contrôle de l'endpoint

Dans PowerShell sur le poste runner, ouvrir un tunnel vers l'API du Spark :

```powershell
$gpuSshHost = "<ip-ou-nom-d-hote>"
$gpuSshUser = "<utilisateur-ssh>"
$gpuSshPort = 22
$gpuSshKey = "C:\chemin\vers\cle-privee"
ssh -i "$gpuSshKey" `
  -p $gpuSshPort `
  -L 8000:127.0.0.1:8001 `
  "$gpuSshUser@$gpuSshHost"
```

Dans une autre fenêtre du runner, contrôler les modèles puis exécuter le smoke
endpoint. La config client pointe vers le port local 8000 ; le serveur Spark
écoute sur 8001 :

```powershell
python scripts/check_openai_endpoint.py `
  --base-url http://127.0.0.1:8000/v1 `
  --model Qwen3.8-27B
```

Monter ensuite progressivement le contexte à 64k, 128k et 262k depuis l'API et
les logs serveur. Vérifier `reasoning_effort=medium`, le streaming, les appels
d'outils et les réponses `file_changes_v1`. Pour le serving et les cohortes,
confirmer aussi que l'acceptance DFlash2 est mesurée et que le cache de préfixe
est activé côté serveur.

## Smoke d'isolation DFlash2

Le smoke exécuté le 14 octobre a été lancé une fois à un agent : 9/10 tâches
réussies, avec un pic de concurrence de 1. Le pilote complet a ensuite observé
la concurrence jusqu'à 10, mais le smoke séquentiel seul ne valide pas
l'isolation multi-requête. Les commandes ci-dessous décrivent le smoke complet
à réaliser sur une nouvelle instance ou lors d'une nouvelle validation.

Ne pas lancer d'abord la matrice serving ni la cohorte complète. Le profil de
smoke prévoit dix tâches distinctes aux paliers 1, 4 et 10 agents, une fois
chacun. Il vérifie que des prompts simultanés ne mélangent pas leurs sorties et
que le palier 10 atteint réellement `max_concurrent_model_requests: 10` dans le
rapport. Examiner les réponses et erreurs de chaque tâche avant d'ouvrir le gate.

```powershell
python scripts/run_cohort_pilot.py `
  --benchmark-config benchmark.qwen3.8-sglang-nvfp4-dflash2-dgx-spark-medium-thinking.yaml `
  --plan campaigns/cohort/qwen3.8-sglang-nvfp4-dflash2-dgx-spark-smoke.yaml `
  --plan-only
```

Après le plan-only, exécuter chacun des paliers `--agents 1`, `--agents 4` et
`--agents 10` une fois, en gardant la même instance et le même processus serveur.
Fournir les options `--remote-gpu-ssh-host`, `--remote-gpu-ssh-user`,
`--remote-gpu-ssh-port` et `--remote-gpu-ssh-key` pour capturer les métriques
du Spark. Si le pic observé reste inférieur à 10, le smoke ne valide pas le
palier 10 ; diagnostiquer les limites `max_running_requests`/Mamba avant les
runs complets.

```powershell
python scripts/run_cohort_pilot.py `
  --benchmark-config benchmark.qwen3.8-sglang-nvfp4-dflash2-dgx-spark-medium-thinking.yaml `
  --plan campaigns/cohort/qwen3.8-sglang-nvfp4-dflash2-dgx-spark-smoke.yaml `
  --agents 1 `
  --remote-gpu-ssh-host $gpuSshHost `
  --remote-gpu-ssh-user $gpuSshUser `
  --remote-gpu-ssh-port $gpuSshPort `
  --remote-gpu-ssh-key "$gpuSshKey"
```

### Tableau de suivi des runs C-025

| Agents | Réussites cumulées | Durée médiane (min–max) | Runs | Pic simultané observé |
|---:|---:|---:|---:|---:|
| 1 | 51/54 | 488,61 s (475,73–896,62) | 3 | 1 |
| 4 | 52/54 | 185,38 s (167,20–278,14) | 3 | 4 |
| 5 | 52/54 | 241,15 s (231,96–533,38) | 3 | 5 |
| 6 | 52/54 | 252,84 s (216,77–306,44) | 3 | 6 |
| 8 | 52/54 | 201,65 s (197,38–266,01) | 3 | 8 |
| 10 | 52/54 | 318,06 s (187,17–404,55) | 3 | 10 |

La cohorte complète est terminée : 18 runs, 311/324 tâches réussies. Les
médianes portent sur les trois durées de chaque niveau ; les réussites sont
cumulées sur les trois runs. Les 13 échecs concernent `DOC-03`. Le [rapport de
session](COHORT_SESSION_DGX_SPARK_SGLANG_DFLASH2_2026-10-14.md) donne les
résultats et manifestes individuels. Le smoke de dix tâches reste une mesure
séparée et n'est pas inclus dans ce tableau.

### Résultat du smoke cohorte du 14 octobre 2026

Le run `20261014T141101.785201Z-cohort-a1-ac058753` a traité les dix tâches
avec un seul agent : 9/10 réussies en 860,73 s. Le pic était de
`max_concurrent_model_requests: 1` (`max_active_agents: 1`) ; ce run confirme
seulement le palier séquentiel et ne mesure pas l'isolation à 4 ou 10 requêtes.
Le manifeste brut est
[`campaign.json`](../results/raw/cohort/20261014T141101.785201Z-cohort-a1-ac058753/campaign.json).

`DOC-10` est l'unique échec. Ses trois réponses se sont terminées avec
`finish_reason: length`, 6 000 tokens de complétion et un contenu vide ; le
runner a signalé `ChangeProtocolError` (« réponse du modèle non valide JSON »).
Les 12 requêtes modèle ont réussi au niveau transport, sans erreur runner ni
rejet de capacité. Le résultat reste un échec de tâche/protocole, pas une preuve
de mélange entre requêtes. L'artefact détaillé est
[`result.json`](../results/raw/20261014T141226.643730Z-doc-10-07b075fd/result.json).

### Résultat du pilote complet

Les 18 runs du pilote sont terminés et ont atteint leur niveau de concurrence
configuré, jusqu'à dix requêtes simultanées. Les détails par répétition, la
télémétrie distante, les empreintes de configuration et les limites de
comparaison sont regroupés dans le [rapport de session](COHORT_SESSION_DGX_SPARK_SGLANG_DFLASH2_2026-10-14.md).
La cohorte n'a pas remplacé le smoke de dix tâches : celui-ci reste documenté
séparément ci-dessus.

## C-025 — préflight, qualité et serving à compléter

La cohorte C-025 est terminée. La qualité complète sur 74 tâches et le serving
shared-prefix restent à exécuter. Pour ces campagnes, figer avant le préflight
l'édition/UUID du GB10, le pilote, CUDA, l'OS, la mémoire hôte et le digest Docker
effectif. Remplacer les champs matériels `null` des profils par les valeurs
observées, garder les révisions de poids et l'image identiques entre profils,
puis committer ces entrées avant `--require-clean`. Le worktree de préparation
peut rester non committé pendant les plan-only.

```powershell
python scripts/prepare_gpu_campaign.py `
  --campaign-id C-025 `
  --config benchmark.qwen3.8-sglang-nvfp4-dflash2-dgx-spark-medium-thinking.yaml `
  --serving-config campaigns/gpu/serving-qwen-sglang-nvfp4-dflash2-dgx-spark-shared-prefix.yaml `
  --plan campaigns/gpu/plan-sglang-dgx-spark.yaml `
  --output results/raw/preflight/C-025-sglang-dgx-spark.json `
  --require-clean
```

```powershell
python scripts/run_quality_campaign.py `
  --campaign-id C-025 `
  --config benchmark.qwen3.8-sglang-nvfp4-dflash2-dgx-spark-medium-thinking.yaml `
  --plan campaigns/gpu/plan-sglang-dgx-spark.yaml `
  --mode repair `
  --suite smoke `
  --seed 42
```

Après un smoke qualité propre, remplacer `--suite smoke` par `--suite full` pour
les 74 tâches. Ajouter à chaque exécution les quatre options SSH ci-dessus pour
enregistrer la télémétrie distante. Les runs qualité, serving et cohorte gardent
des artefacts bruts distincts.

Avant le serving, capturer des snapshots Prometheus bruts :

```bash
mkdir -p /workspace/sglang-metrics
curl -fsS http://127.0.0.1:8001/metrics -o /workspace/sglang-metrics/C-025-before.prom
```

Puis lancer la matrice :

```powershell
python scripts/run_serving_benchmark.py `
  --config campaigns/gpu/serving-qwen-sglang-nvfp4-dflash2-dgx-spark-shared-prefix.yaml `
  --remote-gpu-ssh-host $gpuSshHost `
  --remote-gpu-ssh-user $gpuSshUser `
  --remote-gpu-ssh-port $gpuSshPort `
  --remote-gpu-ssh-key "$gpuSshKey"
```

Capturer juste après le même endpoint dans `C-025-after.prom`, conserver les deux
snapshots auprès du run brut et calculer les hits depuis les deltas des compteurs
`sglang:prefill_effective_tokens_total` ; le runner serving ne les scrape pas.

## Reproduire la cohorte complète

Le pilote exécuté le 14 octobre est terminé : six niveaux d'agents, trois
répétitions par niveau. Le rapport et les manifestes d'origine sont liés dans le
tableau ci-dessus. Les commandes suivantes servent à inspecter le plan ou à
reproduire la série ; toute nouvelle exécution doit garder identiques la
sélection de tâches, le seed, l'image et le processus serveur, noter chaque
redémarrage et conserver les manifestes bruts.

```powershell
python scripts/run_cohort_pilot.py `
  --benchmark-config benchmark.qwen3.8-sglang-nvfp4-dflash2-dgx-spark-medium-thinking.yaml `
  --plan campaigns/cohort/qwen3.8-sglang-nvfp4-dflash2-dgx-spark-agentic-pilot.yaml `
  --plan-only
```

Pour une nouvelle série, remplacer `--plan-only` par `--agents 1` (puis 4, 5, 6,
8 et 10) et ajouter les options de télémétrie SSH ; conserver les résultats de
cette série dans des manifestes distincts.
Le rapport doit conserver `max_concurrent_model_requests`, `max_active_agents`,
le makespan, les tâches réussies et les échecs de protocole/validation. Ne pas
interpréter dix agents applicatifs comme dix requêtes simultanées sans vérifier
la valeur mesurée.

Les campagnes qualité et serving consomment du temps GPU loué ; ces commandes
documentent la procédure et n'ont pas été exécutées dans la session de cohorte.
