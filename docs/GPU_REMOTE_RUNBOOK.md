# Runbook de campagne GPU distante

## Décision d'architecture

Le poste local reste le plan de contrôle : il possède le dépôt, le runner, les
tests cachés, les résultats et la logique de validation. La machine louée ne
fait que servir le modèle derrière une API OpenAI-compatible.

```text
poste local                         machine GPU louée
runner + private-tests              serveur d'inférence + modèle
tasks/workspaces                    GPU / VRAM / logs serveur
        ─────── SSH tunnel ───────►  127.0.0.1:<port>/v1
```

Ainsi, le dépôt complet n'a pas besoin d'être copié sur la machine GPU et
`private-tests/` n'est jamais placé dans le contexte du modèle. Seuls les
prompts et les workspaces visibles transitent dans les requêtes vers le serveur.

Sur les instances équipées du portail `portal-aio`, Caddy peut déjà occuper le
port distant `8000`. Dans ce cas, ne pas arrêter Caddy : lancer vLLM sur `8001`
et créer le tunnel SSH avec `-L 8000:127.0.0.1:8001` afin de conserver le
`base_url` local du benchmark.

Vast.ai fournit des instances conteneurisées avec un GPU dédié, une image Docker
choisie par l'utilisateur et une facturation à la seconde. Les templates
définissent notamment l'image, le mode SSH/Jupyter, les ports et l'initialisation.
Voir la [vue d'ensemble des instances Vast.ai](https://docs.vast.ai/guides/instances/overview)
et le [guide de choix d'un template](https://docs.vast.ai/guides/instances/choosing/templates).

## Ce qui doit être préparé avant de louer

Depuis le poste local :

1. Choisir et figer le dépôt, la révision, le tokenizer et le snapshot de poids
   dans [`campaigns/gpu/plan.yaml`](../campaigns/gpu/plan.yaml).
2. Choisir une même image/build du moteur pour les comparaisons contrôlées.
3. Commit la version du benchmark et vérifier que le dépôt est propre.
4. Valider la campagne et générer son manifeste :

   ```powershell
   python scripts/prepare_gpu_campaign.py `
     --campaign-id C-003 `
     --config benchmark.qwen3.8-bf16.yaml `
     --serving-config campaigns/gpu/serving-qwen.yaml `
     --require-clean
   ```

   Avec les configurations Qwen fournies, le manifeste doit être `ready` : les
   dépôts, commits, tokenizer, variante et moteur sont déjà figés. Les seules
   informations laissées à `null` sont celles qui dépendent de l'offre louée
   (GPU, driver, CUDA, image et digest).

5. Vérifier le plan sans contacter de serveur :

   ```powershell
   python scripts/run_quality_campaign.py --campaign-id C-003 --plan-only
   python scripts/run_serving_benchmark.py --plan-only
   python -m unittest discover -s tests -v
   ```

Le préflight local ne loue aucune ressource et ne téléverse pas les tests cachés.

## Choix de l'instance Vast.ai

Pour la première campagne, choisir une instance on-demand et un template/image
avec accès SSH direct. La documentation Vast recommande le mode SSH avec
`ssh_direct` pour une connexion fiable ; la création d'une instance se fait en
deux étapes : rechercher une offre, puis accepter l'offre. Voir [création par
l'API/CLI](https://docs.vast.ai/api-reference/creating-instances-with-api).

Contrôler avant de cliquer sur Rent :

- modèle GPU exact, nombre de GPU et VRAM réellement disponible ;
- disque local suffisant pour le modèle, les caches et les logs ;
- connectivité réseau et ports SSH/direct disponibles ;
- région, prix, type on-demand/interruptible et politique d'interruption ;
- image Docker et version CUDA compatibles avec le moteur retenu ;
- possibilité d'attacher un volume persistant si le modèle doit être réutilisé.

Le prix et la disponibilité sont ceux de l'offre au moment de la location. Le
script de recherche doit donc rester une aide de sélection, jamais une preuve de
comparabilité : le matériel effectivement démarré sera enregistré par le
préflight distant.

## Démarrage court sur la machine louée

La location ne doit pas servir à construire une image à la main. Préférer, dans
l'ordre :

1. une image Docker préparée et versionnée avant la location ;
2. un volume persistant contenant déjà les poids validés ;
3. à défaut, le téléchargement du snapshot et l'installation du moteur dès le
   démarrage, avec leurs versions et empreintes consignées.

Les templates Vast peuvent lancer un script de provisioning, mais celui-ci
reste une étape d'installation distante. Pour les campagnes comparables, son
contenu doit être versionné et son résultat doit apparaître dans les logs. Voir
le [guide de provisioning avancé](https://docs.vast.ai/guides/templates/advanced-setup).

Si l'instance a déjà démarré `supervisord`, ne pas relancer `entrypoint.sh` à la
main : cela tente de démarrer un second Supervisor et provoque un conflit de
ports. Vérifier d'abord `supervisorctl status`; si le service vLLM est arrêté,
le démarrer avec `supervisorctl start vllm`. Pour un diagnostic ou une
configuration temporaire, arrêter le processus vLLM existant puis lancer
directement la commande versionnée avec `nohup`, en conservant son journal.
Les paramètres `--max-num-seqs 16` et `--reasoning-parser qwen3` sont requis par
les profils Qwen3.8 actuels.

### Préparer le cache du modèle

Le template Vast.ai crée déjà `/workspace` et utilise `/workspace/models` pour
le téléchargement du modèle. Ce chemin est un répertoire du disque de
l'instance, pas un volume persistant séparé. Deux stratégies sont possibles :

- utiliser le disque de l'instance avec `--disk` ; les poids seront perdus avec
  la destruction de l'instance. Avec le template fourni, passer `--disk 24` à
  `--disk 200` suffit pour stocker les trois variantes et leurs caches ;
- créer ou réutiliser un volume local Vast.ai, puis le monter sur
  `/workspace/models` ; le cache sera conservé entre les instances attachées à
  cette même machine.

Les volumes Vast.ai sont locaux à la machine physique et ne peuvent pas être
attachés directement à une autre machine. Il est donc préférable de choisir
d'abord l'offre GPU, puis de créer le volume. Pour une première campagne courte,
le disque de l'instance peut suffire ; pour plusieurs campagnes sur le même
hôte, un volume local de 180 à 200 GB est recommandé. Exemple CLI :

```bash
vastai search volumes
vastai create volume <VOLUME_OFFER_ID> --size 200 --name qwen38-models
vastai create instance <OFFER_ID> \
  --image vastai/vllm:v0.29.0-cuda-13.0 \
  --link-volume <VOLUME_ID> --mount-path /workspace/models
```

Pour éviter de payer le téléchargement pendant chaque campagne, monter un
volume persistant sur `/workspace/models`, puis le remplir une seule fois avec les trois
snapshots nécessaires. Les dépôts sont publics ; aucun token Hugging Face n'est
nécessaire sauf restriction ultérieure du fournisseur :

```bash
mkdir -p /workspace/models
export HF_HOME=/workspace/models
if ! command -v hf >/dev/null; then
  python3 -m pip install --user huggingface_hub
  export PATH="$(python3 -m site --user-base)/bin:$PATH"
fi
hf download Qwen/Qwen3.8-27B \
  --revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
hf download Qwen/Qwen3.8-27B-FP8 \
  --revision 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a
hf download nvidia/Qwen3.8-27B-NVFP4 \
  --revision dbb8f445b3145f8a4c18ddc769f032d57d32867c
```

Prévoir au minimum l'espace cumulé des trois snapshots (environ 105 GB
publiés) plus une marge pour les caches et les logs ; 180 à 200 GB est une base
plus confortable. Si le volume est déjà préparé dans une image ou attaché à une
autre instance, cette étape ne doit pas être répétée sur la machine GPU.

Une fois connecté en SSH, ne copier que les deux fichiers nécessaires au
préflight (ou une image qui les contient). Il n'est pas nécessaire de cloner le
dépôt complet sur l'instance louée :

```powershell
scp -P <ssh-port> scripts/capture_gpu_environment.py <user>@<remote-host>:/tmp/
scp -P <ssh-port> serving/resources.py <user>@<remote-host>:/tmp/
```

Sur la machine distante, placer `resources.py` dans un sous-dossier `serving/`,
ou utiliser le checkout local uniquement si cela est compatible avec votre
politique de confidentialité, puis exécuter :

```bash
mkdir -p /tmp/gpu-preflight/serving /tmp/gpu-preflight/scripts
mv /tmp/capture_gpu_environment.py /tmp/gpu-preflight/scripts/
mv /tmp/resources.py /tmp/gpu-preflight/serving/
cd /tmp/gpu-preflight
python3 scripts/capture_gpu_environment.py \
  --output remote-gpu-preflight.json \
  --expected-gpu "NVIDIA H200" \
  --expected-gpu-count 1 \
  --min-memory-gb 130 \
  --model-repository https://huggingface.co/Qwen/Qwen3.8-27B \
  --model-revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 \
  --tokenizer-repository https://huggingface.co/Qwen/Qwen3.8-27B \
  --tokenizer-revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
```

Pour une RTX PRO 6000 Blackwell Server Edition, remplacer l'option `--expected-gpu`. Le script
enregistre `nvidia-smi`, le driver, CUDA/nvcc, Docker, l'OS, le stockage, la
mémoire hôte, les ressources GPU, la version vLLM et l'identité du snapshot. Il échoue
si aucun GPU n'est visible, si le nombre ou le modèle ne correspondent pas à
l'attendu. Les options `--model-file` et `--expected-sha256` restent disponibles
pour un artefact monolithique utilisé par un autre moteur, mais ne sont pas le
contrôle de référence pour les snapshots Safetensors Qwen.

Pour C-011, utiliser `NVIDIA RTX PRO 6000 Blackwell Server Edition` et l'identité
`nvidia/Qwen3.8-27B-NVFP4`. Pour C-012, utiliser `NVIDIA GB10` (le nom exposé
par `nvidia-smi`) et
la même identité de checkpoint. Ces deux campagnes restent exploratoires tant
que le backend NVFP4 et la stabilité du serveur n'ont pas été confirmés.

Le serveur d'inférence est ensuite lancé avec la commande exacte de la
configuration. Pour Qwen3.8-27B :

```bash
# Variante BF16
HF_HOME=/workspace/models vllm serve Qwen/Qwen3.8-27B \
  --revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 \
  --tokenizer Qwen/Qwen3.8-27B --tokenizer-revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 \
  --served-model-name Qwen3.8-27B \
  --tensor-parallel-size 1 --pipeline-parallel-size 1 \
  --max-model-len 262144 --max-num-seqs 16 --reasoning-parser qwen3 --kv-cache-dtype fp8

# Variante FP8 officielle
HF_HOME=/workspace/models vllm serve Qwen/Qwen3.8-27B-FP8 \
  --revision 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a \
  --tokenizer Qwen/Qwen3.8-27B --tokenizer-revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 \
  --served-model-name Qwen3.8-27B \
  --tensor-parallel-size 1 --pipeline-parallel-size 1 \
  --max-model-len 262144 --max-num-seqs 16 --reasoning-parser qwen3 --kv-cache-dtype fp8

# Variante NVFP4 mixed NVIDIA
HF_HOME=/workspace/models vllm serve nvidia/Qwen3.8-27B-NVFP4 \
  --revision dbb8f445b3145f8a4c18ddc769f032d57d32867c \
  --tokenizer Qwen/Qwen3.8-27B --tokenizer-revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 \
  --served-model-name Qwen3.8-27B \
  --tensor-parallel-size 1 --pipeline-parallel-size 1 \
  --max-model-len 262144 --max-num-seqs 16 --reasoning-parser qwen3 --kv-cache-dtype fp8
```

Le premier démarrage télécharge le snapshot dans le cache Hugging Face de
l'image. Pour minimiser le temps facturé, préparer ce cache dans un volume
persistant ou une image dérivée avant la campagne, puis conserver dans un log :
commande complète, image/tag ou digest,
version du moteur, modèle chargé, quantification, KV cache, contexte maximum,
batch, slots, prefix caching et état de flash attention/speculative decoding.

## Connexion sans exposer le serveur

Ne pas rendre l'API publique si un tunnel SSH suffit. Depuis le poste local :

```powershell
ssh -p <ssh-port> <user>@<remote-host> `
  -L 8000:127.0.0.1:<server-port>
```

Puis vérifier immédiatement le modèle annoncé et une génération courte :

```powershell
python scripts/check_openai_endpoint.py `
  --base-url http://127.0.0.1:8000/v1 `
  --model <model-id-exact>
```

Le smoke doit réussir avant tout test long. Un échec de `/models`, de template,
de thinking ou de contexte est un échec de préflight, pas un résultat qualité.

## Collecte distante des métriques GPU pendant un benchmark

Les runners qualité, cohorte et serving peuvent échantillonner le GPU distant
pendant leur exécution. La collecte utilise une connexion SSH indépendante du
tunnel API : elle n'a pas besoin de `-L`. Le poste local doit avoir OpenSSH,
et l'empreinte de l'hôte doit déjà être acceptée dans `known_hosts`, car la
connexion est non interactive. `nvidia-smi` doit être disponible sur l'hôte GPU.

Définir une fois les paramètres de l'instance courante dans PowerShell. Ces
valeurs peuvent changer à chaque location :

```powershell
$gpuSshHost = "<ip-ou-nom-d-hote>"
$gpuSshUser = "<utilisateur-ssh>"
$gpuSshPort = 22
$gpuSshKey = "C:\chemin\vers\cle-privee"
```

Puis passer les mêmes options à chacun des runners :

```powershell
python scripts/run_quality_campaign.py `
  --campaign-id C-018 `
  --config benchmark.qwen3.8-fp8-shared-prefix-medium-thinking.yaml `
  --remote-gpu-ssh-host $gpuSshHost `
  --remote-gpu-ssh-user $gpuSshUser `
  --remote-gpu-ssh-port $gpuSshPort `
  --remote-gpu-ssh-key "$gpuSshKey"
```

```powershell
python scripts/run_cohort_pilot.py `
  --benchmark-config benchmark.qwen3.8-fp8-shared-prefix-medium-thinking.yaml `
  --agents 5 `
  --remote-gpu-ssh-host $gpuSshHost `
  --remote-gpu-ssh-user $gpuSshUser `
  --remote-gpu-ssh-port $gpuSshPort `
  --remote-gpu-ssh-key "$gpuSshKey"
```

```powershell
python scripts/run_serving_benchmark.py `
  --config campaigns/gpu/serving-qwen-rtx-pro-6000-fp8-shared-prefix-medium-thinking.yaml `
  --remote-gpu-ssh-host $gpuSshHost `
  --remote-gpu-ssh-user $gpuSshUser `
  --remote-gpu-ssh-port $gpuSshPort `
  --remote-gpu-ssh-key "$gpuSshKey"
```

La clé est facultative si OpenSSH trouve déjà l'identité via son agent ou sa
configuration. L'intervalle d'échantillonnage vaut une seconde par défaut et
peut être changé avec `--remote-gpu-sample-interval-seconds`. Les valeurs
`host`, `user` et `port` sont enregistrées pour identifier l'instance ; le
chemin et le contenu de la clé ne le sont pas. Chaque dossier de résultat
contient `remote-gpu-samples.jsonl` et un résumé lié au même identifiant de run.
Le JSONL garde les échantillons horodatés ; le résumé fournit les informations
GPU et les pics observés. Ces mesures couvrent l'invocation du runner, pas
chaque tâche ou requête séparément. Après une reprise qualité avec `--resume`,
le nouveau sidecar couvre la reprise ; l'artefact précédent et ses échantillons
restent conservés et référencés par `campaign.resumed_from`.

Sans ces options, aucune connexion SSH n'est ouverte. Si SSH ou `nvidia-smi`
échoue, le benchmark continue et le résultat marque les mesures distantes comme
indisponibles avec le motif d'erreur. Les snapshots de progression peuvent
indiquer `connecting` avant le premier échantillon. Pour comparer les mesures
de serving, garder la collecte activée de façon cohérente entre les runs ; le
runner conserve séparément ses mesures de ressources locales.

Le tunnel API reste celui établi séparément, par exemple avec `-L 8000:127.0.0.1:8001`.

## Ordre pendant la location

Pour chaque campagne :

1. démarrer l'instance et capturer le préflight hôte ;
2. vérifier le commit du snapshot utilisé et le modèle retourné par `/models` ;
3. lancer le serveur avec la configuration figée ;
4. faire le smoke endpoint ;
5. faire la montée mémoire 64k → 128k → 262k ;
6. lancer la qualité depuis le poste local :

   ```powershell
   python scripts/run_quality_campaign.py --campaign-id C-003 --config <config-campagne.yaml>
   ```

   Si le processus est interrompu après une ou plusieurs tâches, reprendre la
   campagne avec les mêmes options et `--resume` :

   ```powershell
   python scripts/run_quality_campaign.py --campaign-id C-003 --config <config-campagne.yaml> --resume
   ```

   Le runner réutilise les résultats de tâches déjà persistés et crée un nouvel
   artefact de campagne ; il ne relance pas ces tâches et n'écrase pas l'ancien
   résultat.

7. lancer séparément le serving :

   ```powershell
   python scripts/run_serving_benchmark.py `
     --config <serving-config-campagne.yaml>
   ```

8. attendre la présence des fichiers `result.json`, `campaign.json`, des logs
   et du préflight dans une copie locale avant d'arrêter l'instance.

Le runner local crée les workspaces propres et injecte les tests cachés
uniquement dans sa copie de validation. La machine distante n'a donc aucune
raison de recevoir `private-tests/`.

## Arrêt et récupération

Avant de stopper ou détruire l'instance :

- copier les préflights et logs serveur vers `results/raw/<campagne>/` ou un
  stockage externe versionné ;
- vérifier les empreintes des fichiers copiés ;
- vérifier que `results/raw/runs.jsonl` et les index de campagnes ont été
  sauvegardés ;
- noter tout écart : GPU différent, fichier remplacé, OOM, contexte refusé,
  crash ou paramètre modifié ;
- seulement ensuite arrêter/détruire l'instance et le volume temporaire.

Une interruption, un OOM ou une limite de contexte reste une observation utile.
Il ne faut pas relancer silencieusement avec un autre paramètre sous le même ID.
