# Playbook de campagne SGLang — Qwen3.8 NVFP4 sur RTX PRO 6000

Ce playbook prépare trois cellules indépendantes. L'ordre prioritaire est C-022
(NVFP4 sans décodage spéculatif), puis C-023 (NVFP4 + DFlash2). C-024 (NVFP4 +
MTP/EAGLE, sans DFlash2) reste facultative. Les fichiers SGLang sont distincts
des plans vLLM ; aucun résultat historique n'est remplacé.

La matrice opérationnelle vLLM RTX PRO 6000 a déjà couvert FP8 et NVFP4 avec et
sans DFlash2. Cela suffit pour commencer une comparaison opérationnelle avec
SGLang. Les comparaisons GPU contrôlées et la paire de cohortes FP8 mentionnées
dans le [plan GPU](GPU_CAMPAIGN_PLAN.md) restent à faire : la transition
n'affirme donc pas que tout le programme vLLM est terminé.

## Profils préparés

| Cellule | Qualité | Serving | Cohorte |
|---|---|---|---|
| C-022 — NVFP4 sans spéculation | [`benchmark.qwen3.8-sglang-nvfp4-medium-thinking.yaml`](../benchmark.qwen3.8-sglang-nvfp4-medium-thinking.yaml) | [`serving-qwen-sglang-nvfp4-shared-prefix.yaml`](../campaigns/gpu/serving-qwen-sglang-nvfp4-shared-prefix.yaml) | [`qwen3.8-sglang-nvfp4-agentic-pilot.yaml`](../campaigns/cohort/qwen3.8-sglang-nvfp4-agentic-pilot.yaml) |
| C-023 — NVFP4 + DFlash2 | [`benchmark.qwen3.8-sglang-nvfp4-dflash2-medium-thinking.yaml`](../benchmark.qwen3.8-sglang-nvfp4-dflash2-medium-thinking.yaml) | [`serving-qwen-sglang-nvfp4-dflash2-shared-prefix.yaml`](../campaigns/gpu/serving-qwen-sglang-nvfp4-dflash2-shared-prefix.yaml) | [`qwen3.8-sglang-nvfp4-dflash2-agentic-pilot.yaml`](../campaigns/cohort/qwen3.8-sglang-nvfp4-dflash2-agentic-pilot.yaml) après la smoke d'isolation ; [`qwen3.8-sglang-nvfp4-dflash2-smoke.yaml`](../campaigns/cohort/qwen3.8-sglang-nvfp4-dflash2-smoke.yaml) pour cette smoke |
| C-024 — NVFP4 + MTP/EAGLE, facultatif | [`benchmark.qwen3.8-sglang-nvfp4-mtp-medium-thinking.yaml`](../benchmark.qwen3.8-sglang-nvfp4-mtp-medium-thinking.yaml) | [`serving-qwen-sglang-nvfp4-mtp-shared-prefix.yaml`](../campaigns/gpu/serving-qwen-sglang-nvfp4-mtp-shared-prefix.yaml) | [`qwen3.8-sglang-nvfp4-mtp-agentic-pilot.yaml`](../campaigns/cohort/qwen3.8-sglang-nvfp4-mtp-agentic-pilot.yaml) |

Le checkpoint cible NVFP4 et le tokenizer sont épinglés à leurs révisions
Hugging Face dans chaque profil. DFlash2 pointe vers
`incoai/Qwen3.8-27B-DFlash2` à la révision
`015e795645c74b1a0eeef3b570031fb62e769bc5`. Les poids restent NVFP4 et le KV
cache reste `fp8_e4m3` dans les trois cellules.

## Image et artefacts sur l'hôte GPU

La recette de départ reprend le [cookbook Qwen3.8 de SGLang, version v0.5.19](https://github.com/sgl-project/sglang/blob/v0.5.19/docs/cookbook/autoregressive/Qwen/Qwen3.8-27B.mdx),
testé sur RTX PRO 6000. Pour la première campagne SGLang C-022, le template Vast.ai
retenu utilise `vastai/sglang:v0.5.20-cuda-13.0`. Cette version est un nouveau
build opérationnel, pas une reproduction du cookbook 0.5.19 : le smoke doit
confirmer les options, le chargement NVFP4 et les comportements avant tout run
qualité complet. Relever l'ID/digest exact de l'image sur l'instance ; le tag seul
ne suffit pas à identifier le build utilisé.

Sur l'hôte GPU, prévoir Docker avec le support NVIDIA et un volume monté au même
chemin dans le conteneur. Télécharger les snapshots dans des répertoires locaux
explicites :

```bash
mkdir -p /workspace/models
hf download nvidia/Qwen3.8-27B-NVFP4 \
  --revision dbb8f445b3145f8a4c18ddc769f032d57d32867c \
  --local-dir /workspace/models/Qwen3.8-27B-NVFP4
hf download Qwen/Qwen3.8-27B \
  --revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 \
  --local-dir /workspace/models/Qwen3.8-27B
hf download incoai/Qwen3.8-27B-DFlash2 \
  --revision 015e795645c74b1a0eeef3b570031fb62e769bc5 \
  --local-dir /workspace/models/Qwen3.8-27B-DFlash2
```

Pour une nouvelle instance seulement, télécharger l'image avant de lancer le
template. Pour l'instance déjà lancée, ne pas refaire `docker pull` sous le même
tag : relever l'ID de l'image du conteneur actif depuis les détails Vast.ai ou,
si le démon Docker de l'hôte est accessible, avec :

```bash
docker inspect <container-id> --format '{{.Image}}'
```

Les deux premières commandes suffisent pour C-022 et C-024. Le troisième
snapshot est nécessaire uniquement pour C-023. Reporter le digest retourné et
les versions effectives de CUDA, du pilote et des dépendances dans les artefacts
de campagne. Pour que le préflight vérifie le même build partout, remplacer
ensuite `serving.engine_version` par la même valeur dans `campaigns/gpu/plan-sglang.yaml`,
les trois profils qualité et les trois profils serving, par exemple
`0.5.20-cuda-13.0 (vastai/sglang@sha256:<digest>)`. Si Vast ne fournit pas de
`RepoDigest`, conserver l'ID d'image Docker (`.Id`) avec le tag dans le manifeste.
Utiliser la référence immuable obtenue pour les prochaines instances lorsque
Vast l'autorise. Ne pas déduire la mémoire ou l'utilisation du GPU à partir du
poste runner.

### Valeurs du template Vast.ai

Le disque persistant de 100 Go est monté sur `/workspace/models`. Les snapshots
NVFP4 et tokenizer doivent déjà s'y trouver aux chemins ci-dessous. Dans le
template, remplacer `SGLANG_MODEL`, `SGLANG_ARGS` et `AUTO_PARALLEL`, ajouter
`HF_HOME`, et faire pointer l'entrée API du `PORTAL_CONFIG` du port interne
`18000` vers `8001` :

```text
SGLANG_MODEL=/workspace/models/Qwen3.8-27B-NVFP4
HF_HOME=/workspace/models
AUTO_PARALLEL=false
SGLANG_ARGS=--attention-backend flashinfer --reasoning-parser qwen3 --tool-call-parser qwen3_coder --download-dir /workspace/models --tokenizer-path /workspace/models/Qwen3.8-27B --served-model-name Qwen3.8-27B --trust-remote-code --tp-size 1 --context-length 262144 --kv-cache-dtype fp8_e4m3 --mem-fraction-static 0.85 --chunked-prefill-size 2048 --mamba-ssm-dtype float32 --mamba-radix-cache-strategy extra_buffer --max-mamba-cache-size 50 --max-running-requests 10 --enable-metrics --host 127.0.0.1 --port 8001
PORTAL_CONFIG=localhost:1111:11111:/:Instance Portal|localhost:7860:17860:/:Model UI|localhost:8000:8001:/docs:SGLang API|localhost:8080:18080:/:Jupyter|localhost:8080:8080:/terminals/1:Jupyter Terminal
```

Conserver les autres ports publiés par le template. Le service SGLang reste lié
à `127.0.0.1:8001` dans l'instance ; le tunnel ci-dessous expose ce port comme
`127.0.0.1:8000` au runner local. Ne pas confondre le port API SGLang distant
8001 avec le port local du runner 8000.

## Démarrer le serveur

Chaque fichier qualité/serving contient le `launch_command` complet de sa
cellule. Lancer ce contenu dans l'image SGLang en montant
`/workspace/models:/workspace/models`, avec accès GPU et mémoire partagée du
conteneur. Utiliser le réseau hôte Linux : le serveur reste lié à
`127.0.0.1:8001` sur l'instance distante et n'est pas publié directement sur
Internet.
Exemple du wrapper de lancement pour C-022 :

```bash
docker run --name sglang-c022 --gpus all --ipc=host --network=host \
  -v /workspace/models:/workspace/models \
  -e HF_HOME=/workspace/models \
  vastai/sglang:v0.5.20-cuda-13.0 \
  sglang serve \
  --model-path /workspace/models/Qwen3.8-27B-NVFP4 \
  --tokenizer-path /workspace/models/Qwen3.8-27B \
  --served-model-name Qwen3.8-27B \
  --trust-remote-code --tp-size 1 --context-length 262144 \
  --kv-cache-dtype fp8_e4m3 --mem-fraction-static 0.85 \
  --attention-backend flashinfer --chunked-prefill-size 2048 \
  --mamba-ssm-dtype float32 --mamba-radix-cache-strategy extra_buffer \
  --max-mamba-cache-size 50 --max-running-requests 10 \
  --reasoning-parser qwen3 --tool-call-parser qwen3_coder \
  --enable-metrics --host 127.0.0.1 --port 8001
```

Pour une exécution Docker manuelle, remplacer le tag par la référence immuable
relevée avant la campagne. Avec le template Vast déjà lancé, ne pas lancer un
second conteneur : appliquer les variables du tableau précédent au template.

Le `max-mamba-cache-size` de 50 correspond au point de départ `10` requêtes ×
`5` états pour la stratégie `extra_buffer`. Au démarrage, vérifier dans les logs
que le serveur accepte la capacité visée au lieu de plafonner
`max_running_requests` à une valeur plus basse. Si le smoke révèle un plafond
ou une erreur mémoire, documenter le changement avant toute campagne ; ne pas
modifier silencieusement un seul profil.

Pour C-023, reprendre la commande du profil DFlash2 puis ajouter les trois
options déjà présentes dans son `launch_command` :
`--speculative-algorithm DFLASH`,
`--speculative-draft-model-path /workspace/models/Qwen3.8-27B-DFlash2` et
`--speculative-num-draft-tokens 8`. Pour C-024, le profil MTP ajoute
`--speculative-algorithm EAGLE --speculative-num-steps 3
--speculative-eagle-topk 1 --speculative-num-draft-tokens 4` et
`--enable-linear-replayssm-spec`. Ne pas mélanger les options DFlash2 et MTP.

Depuis le poste benchmark, ouvrir un tunnel SSH vers le port distant 8001 :

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

Les trois configurations client ciblent alors
`http://127.0.0.1:8000/v1`. Dans une autre fenêtre PowerShell, définir les
mêmes variables SSH pour joindre aussi la télémétrie distante du runner :

```powershell
$gpuSshHost = "<ip-ou-nom-d-hote>"
$gpuSshUser = "<utilisateur-ssh>"
$gpuSshPort = 22
$gpuSshKey = "C:\chemin\vers\cle-privee"
```

## Ordre de passage

### C-022 — NVFP4 sans décodage spéculatif

1. Vérifier le GPU, le digest de l'image, le chargement du checkpoint NVFP4 et
   la capacité contextuelle par paliers jusqu'à 262 144 tokens.
2. Vérifier l'API OpenAI, `reasoning_effort=medium`, le streaming, les appels
   d'outils et le format de réponse `file_changes_v1`.
3. Faire une passe qualité `smoke`, puis la suite `full` seulement si les
   sorties et le protocole sont valides.
4. Faire la matrice serving (20 cas, 1 800 requêtes mesurées), puis les
   cohortes aux niveaux 1/4/5/6/8/10 avec trois répétitions par niveau.

### C-023 — NVFP4 + DFlash2

D'abord vérifier le chargement du draft et l'acceptance des propositions à une
requête. Ensuite lancer la cohorte d'isolation de 10 tâches aux niveaux 1, 4 et
10 agents, une répétition par niveau. Les prompts et workspaces sont distincts ;
inspecter les résultats de tâches et les erreurs pour détecter toute sortie
croisée entre requêtes. Pour valider le palier 10, le rapport doit indiquer
`max_concurrent_model_requests: 10` ; si la cohorte n'atteint pas ce pic, le smoke
ne valide pas encore ce niveau de concurrence. Un [signalement SGLang ouvert](https://github.com/sgl-project/sglang/issues/36548)
décrit un possible mélange de contexte DFlash2 sous concurrence sur RTX PRO 6000 ;
tant que ce smoke n'est pas propre, ne pas lancer la matrice serving complète ni
les cohortes au-delà de 1 agent. Après réussite, utiliser les profils de 18 tâches,
trois répétitions par niveau, et la matrice serving complète.

### C-024 — candidat MTP/EAGLE

N'exécuter que si cette cellule est retenue. Valider d'abord le chargement, les
réponses spéculatives et la compatibilité FlashInfer du build épinglé. Le
Le [cookbook SGLang](https://github.com/sgl-project/sglang/blob/v0.5.19/docs/cookbook/autoregressive/Qwen/Qwen3.8-27B.mdx)
signale qu'EAGLE/MTP avec FlashInfer exige une version dont le `plan` de prefill
accepte `uniform_q_len`; en cas d'incompatibilité, ne pas basculer
implicitement le backend dans les campagnes déjà définies : corriger et versionner
le profil après le smoke.

## Commandes locales sans exécuter la campagne

Les commandes `--plan-only` affichent les tâches/cas choisis et ne joignent pas
le serveur. Elles sont également utilisées pour valider le chargement des
configurations.

```powershell
python scripts/run_quality_campaign.py `
  --campaign-id C-022 `
  --config benchmark.qwen3.8-sglang-nvfp4-medium-thinking.yaml `
  --plan campaigns/gpu/plan-sglang.yaml `
  --mode repair `
  --suite full `
  --seed 42 `
  --plan-only
```

Reprendre la même commande avec les paires `C-023` / profil qualité DFlash2 ou
`C-024` / profil qualité MTP pour prévisualiser ces campagnes.

```powershell
python scripts/run_serving_benchmark.py `
  --config campaigns/gpu/serving-qwen-sglang-nvfp4-shared-prefix.yaml `
  --plan-only
```

Faire de même avec les deux profils serving spéculatifs pour afficher leur
matrice de 20 cas, sans tokenizer téléchargé ni requête HTTP.

```powershell
python scripts/run_cohort_pilot.py `
  --benchmark-config benchmark.qwen3.8-sglang-nvfp4-medium-thinking.yaml `
  --plan campaigns/cohort/qwen3.8-sglang-nvfp4-agentic-pilot.yaml `
  --plan-only
```

Faire de même pour les plans DFlash2 (smoke puis 18 tâches) et MTP. `--plan-only`
ne démarre pas de cohorte et ne contacte pas le modèle.

## Préflight et exécution réelle

Après le smoke, relever l'édition et l'UUID du GPU réel, le pilote, CUDA,
la mémoire hôte/GPU, le digest de l'image et les révisions de modèles. Remplir
les champs matériels `null` du profil qualité et propager le digest aux profils
et au plan comme indiqué plus haut. Committer ces entrées figées avant le
préflight : `--require-clean` vérifie que les fichiers de la campagne sont
immuables pendant son exécution. Enregistrer un manifeste séparé par cellule,
par exemple :

Dans un checkout où les profils viennent d'être modifiés, `--require-clean`
échouera tant que ces modifications ne sont pas commitées. Le smoke endpoint
peut être exécuté immédiatement ; avant la suite complète, figer le digest/ID
de l'image et les métadonnées matérielles, puis committer les profils et relancer
le préflight sans `--allow-pending`.

```powershell
$runStamp = Get-Date -Format "yyyyMMdd-HHmmss"
python scripts/prepare_gpu_campaign.py `
  --campaign-id C-022 `
  --config benchmark.qwen3.8-sglang-nvfp4-medium-thinking.yaml `
  --serving-config campaigns/gpu/serving-qwen-sglang-nvfp4-shared-prefix.yaml `
  --plan campaigns/gpu/plan-sglang.yaml `
  --output "results/raw/preflight/C-022-sglang-preflight-$runStamp.json" `
  --require-clean
```

Pour C-023 et C-024, remplacer ensemble l'ID, le profil qualité et le profil
serving correspondants ; conserver le même plan SGLang. Ajouter les options
`--remote-gpu-ssh-*` des exemples suivants à chaque exécution complète afin que
la télémétrie provienne de l'hôte GPU.

Passe qualité smoke de C-022, puis campagne complète après validation :

Avant la suite qualité, ouvrir le tunnel SSH indiqué plus haut puis vérifier
`/v1/models` et une complétion streamée courte depuis le runner :

```powershell
python scripts/check_openai_endpoint.py `
  --base-url http://127.0.0.1:8000/v1 `
  --model Qwen3.8-27B
```

Ce contrôle ne valide qu'une requête courte. Il ne prouve pas la capacité de
contexte 262k ni tous les appels d'outils : vérifier les logs du serveur et faire
la montée de contexte 64k, 128k puis 262k avant la suite `full`. La suite
`smoke` teste ensuite les tâches qualité avec les paramètres de raisonnement
`medium` du profil.

```powershell
python scripts/run_quality_campaign.py `
  --campaign-id C-022 `
  --config benchmark.qwen3.8-sglang-nvfp4-medium-thinking.yaml `
  --plan campaigns/gpu/plan-sglang.yaml `
  --mode repair `
  --suite smoke `
  --seed 42 `
  --remote-gpu-ssh-host $gpuSshHost `
  --remote-gpu-ssh-user $gpuSshUser `
  --remote-gpu-ssh-port $gpuSshPort `
  --remote-gpu-ssh-key "$gpuSshKey"
```

```powershell
python scripts/run_quality_campaign.py `
  --campaign-id C-022 `
  --config benchmark.qwen3.8-sglang-nvfp4-medium-thinking.yaml `
  --plan campaigns/gpu/plan-sglang.yaml `
  --mode repair `
  --suite full `
  --seed 42 `
  --remote-gpu-ssh-host $gpuSshHost `
  --remote-gpu-ssh-user $gpuSshUser `
  --remote-gpu-ssh-port $gpuSshPort `
  --remote-gpu-ssh-key "$gpuSshKey"
```

La matrice serving C-022 :

```powershell
python scripts/run_serving_benchmark.py `
  --config campaigns/gpu/serving-qwen-sglang-nvfp4-shared-prefix.yaml `
  --remote-gpu-ssh-host $gpuSshHost `
  --remote-gpu-ssh-user $gpuSshUser `
  --remote-gpu-ssh-port $gpuSshPort `
  --remote-gpu-ssh-key "$gpuSshKey"
```

Pour une cohorte C-022, faire un lancement distinct par valeur et répéter trois
fois chaque valeur. Exemple à cinq agents :

```powershell
python scripts/run_cohort_pilot.py `
  --benchmark-config benchmark.qwen3.8-sglang-nvfp4-medium-thinking.yaml `
  --plan campaigns/cohort/qwen3.8-sglang-nvfp4-agentic-pilot.yaml `
  --agents 5 `
  --remote-gpu-ssh-host $gpuSshHost `
  --remote-gpu-ssh-user $gpuSshUser `
  --remote-gpu-ssh-port $gpuSshPort `
  --remote-gpu-ssh-key "$gpuSshKey"
```

Réutiliser ces commandes pour C-023 après l'isolation avec le profil et le plan
DFlash2 ; pour la smoke DFlash2, le plan porte 10 tâches et la commande de
cohorte utilise `--agents 1`, `--agents 4`, puis `--agents 10`, une fois
chacun. Pour C-024, remplacer par le profil/plan MTP et ne lancer la campagne
qu'après décision explicite de retenir cette variante.

## Mesure du prefix cache

Le runner serving ne scrape pas les métriques propres à SGLang. Le serveur est
configuré avec `--enable-metrics` ; capturer `/metrics` sur l'instance juste avant et
après chaque matrice `shared-prefix`, et conserver les deux snapshots à côté du
run brut. Sur le build SGLang 0.5.20, vérifier d'abord la présence et la sémantique
des compteurs ; s'ils sont disponibles, préférer les deltas du compteur
`sglang:prefill_effective_tokens_total` : additionner `device_hit`, `host_hit`
et `storage_hit`, puis calculer `hits / (hits + input)`. Conserver aussi les
deltas de `sglang:realtime_tokens_total` (`prefill_cache` et `prefill_compute`)
comme contrôle secondaire. Ne pas conclure depuis le seul gauge
`sglang:cache_hit_rate`, qui peut refléter un batch récent plutôt que l'ensemble
du run. Si le build ne fournit pas les compteurs attendus, garder les snapshots
et déclarer le taux de hits indisponible.

Sur l'hôte GPU, capturer les deux réponses Prometheus sans les transformer :

```bash
mkdir -p /workspace/sglang-metrics
curl -fsS http://127.0.0.1:8001/metrics \
  -o /workspace/sglang-metrics/C-022-before.prom
```

Après la matrice, refaire la commande avec le suffixe `after`, puis copier les
deux fichiers bruts dans le dossier de l'exécution serving correspondante sous
`results/raw/serving/`. Utiliser un nom distinct pour chaque cellule et chaque
répétition ; le serveur doit rester le même entre les deux snapshots.

## Limites d'interprétation

Ces cellules comparent deux moteurs en configuration opérationnelle. Le profil
NVFP4 reste basé sur le checkpoint `nvidia/Qwen3.8-27B-NVFP4`; le cookbook SGLang
sert de référence de démarrage, mais le smoke doit établir que ce checkpoint,
son head quantifié, les parsers et le protocole du benchmark fonctionnent sur
l'image retenue. La matrice serving est `shared-prefix` uniquement, avec
concurrences 1/2/5/10, contextes 8k/32k/64k/100k/200k, un warmup et 20
répétitions par cas. Elle ne constitue pas une comparaison matérielle contrôlée
ni un résultat GPU avant exécution et archivage des artefacts bruts.
