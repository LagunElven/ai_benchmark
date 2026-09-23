# Plan des campagnes GPU — Milestone 11

Ce document prépare les campagnes réelles sur une NVIDIA H200, une NVIDIA
RTX PRO 6000 Blackwell Server Edition et un NVIDIA DGX Spark / GB10. Il sépare les comparaisons contrôlées, destinées à
mesurer l'effet du matériel ou de la quantification, des profils opérationnels
qui cherchent le meilleur service possible sur chaque carte.

Les campagnes contrôlées et NVFP4 du tableau ci-dessous sont planifiées et restent
à exécuter. Les profils opérationnels C-016 et C-017 ont déjà été évalués sur la RTX
PRO 6000 ; leurs résultats figurent dans la matrice et le compte rendu de session.
C-018, profil qualité FP8 officiel et future base opérationnelle, a été exécuté :
la campagne qualité est terminée avec des échecs et le serving est terminé. C-019
prépare le même checkpoint FP8 avec le draft DFlash2 ; son plan est
isolé dans `campaigns/gpu/plan-c019-dflash2.yaml` afin de ne pas modifier les entrées
de C-018 pendant son exécution ni empêcher une éventuelle reprise.
Les résultats ne doivent être ajoutés à `docs/CAMPAIGN_MATRIX.md` qu'après la
conservation des artefacts bruts et la génération des rapports.

La préparation opérationnelle et le parcours de location sont décrits dans
[`docs/GPU_REMOTE_RUNBOOK.md`](GPU_REMOTE_RUNBOOK.md). Le plan machine-readable
se trouve dans [`campaigns/gpu/plan.yaml`](../campaigns/gpu/plan.yaml) ; les
champs `null` restants indiquent les décisions qui doivent être figées avant de
louer la machine ou de déclarer une campagne prête.

## Artefacts Qwen figés

Nous utilisons les dépôts officiels Qwen au format Safetensors, recommandé par
Qwen pour vLLM :

| Variante | Dépôt | Révision | Taille publiée |
|---|---|---|---:|
| BF16 | [`Qwen/Qwen3.8-27B`](https://huggingface.co/Qwen/Qwen3.8-27B/tree/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0) | `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` | 55,6 GB |
| FP8 | [`Qwen/Qwen3.8-27B-FP8`](https://huggingface.co/Qwen/Qwen3.8-27B-FP8/tree/017b9c7af6b5689d5dd426a76e0bc077eb5ca20a) | `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a` | 30,9 GB |

Les deux dépôts contiennent les fichiers de configuration, tokenizer et poids
shardés nécessaires à vLLM. La révision immuable du dépôt est l'ancrage de
reproductibilité ; le runner conservera en plus le manifeste des fichiers et
les empreintes retournées par l'environnement de téléchargement.

Le dépôt GGUF Unsloth et sa variante `UD-Q8_K_XL` ne font plus partie des
campagnes planifiées. Cela évite de dépendre du support GGUF expérimental de
vLLM et de son plugin externe.

## Artefact INT8/W8A16 tiers pour vLLM

Le checkpoint Q8 retenu pour l'exploration vLLM est distinct des GGUF et utilise
le format Safetensors `compressed-tensors` :

| Variante | Dépôt | Révision | Format |
|---|---|---|---|
| INT8 W8A16 | [`GotoAI-Inc/Qwen3.8-27B-W8A16`](https://huggingface.co/GotoAI-Inc/Qwen3.8-27B-W8A16/tree/e349969d1d27552c755c992ae64a2ea56007f3e4) | `e349969d1d27552c755c992ae64a2ea56007f3e4` | poids INT8, activations BF16 |

Il est servi sous vLLM avec le tokenizer officiel Qwen BF16. Ce dépôt est tiers
et non affilié à Qwen. La réplication documentaire de C-017 et sa matrice serving
complète ont été exécutées le 22 septembre 2026. C-017 reste une comparaison
opérationnelle/exploratoire : le checkpoint tiers ne permet pas d'isoler l'effet
de la quantification par rapport au checkpoint Qwen BF16. Les résultats et limites
sont décrits dans [`docs/GPU_SESSION_2026-09-22.md`](GPU_SESSION_2026-09-22.md).

## Artefact NVFP4 distinct

La variante NVFP4 est traitée comme un checkpoint séparé, publié sous le
namespace NVIDIA et produit avec Model Optimizer. Il ne s'agit pas d'une option
à appliquer à la volée au checkpoint BF16 ou FP8 :

| Variante | Dépôt | Révision | Format interne |
|---|---|---|---|
| NVFP4 mixed | [`nvidia/Qwen3.8-27B-NVFP4`](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/dbb8f445b3145f8a4c18ddc769f032d57d32867c) | `dbb8f445b3145f8a4c18ddc769f032d57d32867c` | NVFP4 pour MLP/LM head, FP8 pour les attentions |

Le tokenizer reste celui du dépôt Qwen BF16 déjà utilisé par les autres
campagnes. Le KV cache reste en `fp8`. Le checkpoint sera d'abord validé sur
vLLM avant toute mesure de qualité ou de débit.

## Campagnes planifiées

| ID | Statut | Matériel | Format | Type de comparaison | Objectif |
|---|---|---|---|---|---|
| C-003 | planifiée | 1x H200 | BF16 | contrôlée matériel | qualité de référence BF16 |
| C-004 | planifiée | 1x RTX PRO 6000 Blackwell Server Edition | BF16 | contrôlée matériel | qualité de référence BF16 |
| C-009 | planifiée | 1x DGX Spark / GB10 | BF16 | contrôlée matériel | qualité de référence BF16 |
| C-005 | planifiée | 1x H200 | FP8 | contrôlée matériel | qualité de référence FP8 |
| C-006 | planifiée | 1x RTX PRO 6000 Blackwell Server Edition | FP8 | contrôlée matériel | qualité de référence FP8 |
| C-010 | planifiée | 1x DGX Spark / GB10 | FP8 | contrôlée matériel | qualité de référence FP8 |
| C-011 | exploratoire | 1x RTX PRO 6000 Blackwell Server Edition | NVFP4 mixed | contrôlée quantification | NVFP4 sur RTX PRO Server Edition, après smoke vLLM |
| C-012 | exploratoire | 1x DGX Spark / GB10 | NVFP4 mixed | contrôlée quantification | NVFP4 sur GB10, après smoke vLLM |
| C-018 | qualité terminée avec échecs / serving terminé | 1x RTX PRO 6000 Blackwell Server Edition | FP8 officiel | opérationnelle | future base qualité, thinking medium et shared-prefix, 74 tâches |
| C-019 | exploratoire | 1x RTX PRO 6000 Blackwell Server Edition | FP8 + draft DFlash2 BF16 | opérationnelle | même cible FP8 que C-018 ; vérifier qualité, acceptance, prefix-cache hits et serving |

C-003/C-004/C-009 forment la comparaison matérielle BF16 et C-005/C-006/C-010 la
comparaison matérielle FP8. C-003/C-005, C-004/C-006 et C-009/C-010 permettent
ensuite une comparaison de quantification sur chaque plateforme. C-011 se
compare à C-004/C-006 et C-012 à C-009/C-010, en conservant la distinction entre
la série contrôlée et le statut exploratoire du support NVFP4.

Les profils opérationnels ajoutés pour la RTX PRO 6000 sont `C-013` (BF16
no-thinking), `C-014` (BF16 avec prefix caching), `C-015` (thinking low), `C-016`
(thinking medium), `C-017` (INT8/W8A16 thinking medium) et `C-018` (FP8 officiel,
thinking medium). C-017/C-018 partagent le même groupe opérationnel et les mêmes
74 tâches ; le checkpoint Q8 tiers empêche toutefois de qualifier leur résultat
de comparaison contrôlée de quantification. C-018 ne remplace pas C-006, qui garde
la sémantique de la série FP8 contrôlée.

Les profils serving associés à C-017/C-018 ne mesurent que `shared-prefix`, avec
prefix caching activé, `enable_thinking: true` et `reasoning_effort: medium`.
Chaque variante couvre 20 cas (4 concurrences × 5 contextes), 20 répétitions par
cas, plus un warmup : 1 800 requêtes mesurées par variante. Les profils historiques
et leurs résultats ne sont pas modifiés. Avant la matrice complète, faire un smoke
de chargement et de contexte jusqu'à 200k tokens, puis conserver les logs du kernel
FP8 effectivement sélectionné.

Préflight local du profil qualité FP8 (n'exécute pas le modèle) :

```powershell
python scripts/prepare_gpu_campaign.py `
  --campaign-id C-018 `
  --config benchmark.qwen3.8-fp8-shared-prefix-medium-thinking.yaml `
  --serving-config campaigns/gpu/serving-qwen-rtx-pro-6000-fp8-shared-prefix-medium-thinking.yaml `
  --require-clean
```

Une fois le préflight prêt et le smoke serveur validé, lancer la qualité sur la
suite `full` (74 tâches) en mode réparation, seed 42 :

```powershell
python scripts/run_quality_campaign.py `
  --campaign-id C-018 `
  --config benchmark.qwen3.8-fp8-shared-prefix-medium-thinking.yaml `
  --mode repair --suite full --seed 42
```

Le serving Q8 et FP8 se lance séparément avec le profil dédié correspondant ; la
matrice des deux variantes est identique.

### C-019 — validation DFlash2 sur la cible FP8

C-019 conserve exactement la cible officielle `Qwen/Qwen3.8-27B-FP8`, son tokenizer,
les paramètres medium/shared-prefix et vLLM 0.29.0. La seule différence opérationnelle
est l'ajout du draft BF16 DFlash2, `incoai/Qwen3.8-27B-DFlash2`, révision
`015e795645c74b1a0eeef3b570031fb62e769bc5`. La fiche z-lab indique que son dépôt est
un miroir du checkpoint IncoAI, et la recette vLLM utilise le dépôt IncoAI. Le plan
séparé de C-019 fige cette révision sans altérer le plan de C-018.

Télécharger uniquement le draft (le modèle FP8 et le tokenizer Qwen sont déjà en cache) :

```bash
export HF_HOME=/workspace/models
hf download incoai/Qwen3.8-27B-DFlash2 \
  --revision 015e795645c74b1a0eeef3b570031fb62e769bc5 \
  --local-dir /workspace/models/Qwen3.8-27B-DFlash2-015e795645c74b1a0eeef3b570031fb62e769bc5
```

Après la fin des campagnes qualité et serving C-018, arrêter le vLLM FP8 courant puis
lancer le serveur DFlash2 sur le port `8001` (le tunnel existant continue d'exposer
le port local `8000`) :

```bash
nohup env HF_HOME=/workspace/models vllm serve Qwen/Qwen3.8-27B-FP8 \
  --revision 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a \
  --tokenizer Qwen/Qwen3.8-27B \
  --tokenizer-revision 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0 \
  --served-model-name Qwen3.8-27B \
  --tensor-parallel-size 1 --pipeline-parallel-size 1 \
  --max-model-len 262144 --max-num-seqs 16 --reasoning-parser qwen3 \
  --kv-cache-dtype fp8 --enable-prefix-caching \
  --speculative-config '{"method":"dflash","model":"/workspace/models/Qwen3.8-27B-DFlash2-015e795645c74b1a0eeef3b570031fb62e769bc5","num_speculative_tokens":7}' \
  --port 8001 \
  > /workspace/vllm-qwen38-fp8-dflash2.log 2>&1 &
echo $!
```

La recette vLLM demande v0.28.0 ou plus et `num_speculative_tokens=7` ; le vLLM
0.29.0 déjà prévu convient sans installation depuis une PR/nightly. Avant les campagnes,
valider le chargement, une requête courte, les contextes jusqu'à 200k, les appels de
fonctions/protocole utilisés, ainsi que le taux d'acceptation DFlash2. Vérifier aussi
que les requêtes répétées partagent effectivement leur préfixe : une
[régression vLLM](https://github.com/vllm-project/vllm/issues/54360) a été signalée
sur des modèles Qwen3.8 hybrides où le prefix cache restait à zéro avec la spéculation
active. Si les hits ne progressent pas, ne pas lancer la matrice en la présentant comme
un test shared-prefix.

Préflight puis lancement qualité C-019 après validation du smoke :

```powershell
python scripts/prepare_gpu_campaign.py `
  --campaign-id C-019 `
  --plan campaigns/gpu/plan-c019-dflash2.yaml `
  --config benchmark.qwen3.8-fp8-dflash2-shared-prefix-medium-thinking.yaml `
  --serving-config campaigns/gpu/serving-qwen-rtx-pro-6000-fp8-dflash2-shared-prefix-medium-thinking.yaml `
  --require-clean

python scripts/run_quality_campaign.py `
  --campaign-id C-019 `
  --plan campaigns/gpu/plan-c019-dflash2.yaml `
  --config benchmark.qwen3.8-fp8-dflash2-shared-prefix-medium-thinking.yaml `
  --mode repair --suite full --seed 42

python scripts/run_serving_benchmark.py `
  --config campaigns/gpu/serving-qwen-rtx-pro-6000-fp8-dflash2-shared-prefix-medium-thinking.yaml
```

La qualité C-019 sert de contrôle de non-régression du même modèle cible ; la comparaison
de performance est opérationnelle (décodage spéculatif activé). Le rapport devra inclure
le coût mémoire du draft, les tokens acceptés par étape, les échecs éventuels et les
observations de cache, sans attribuer au draft une différence de qualité comme s'il
s'agissait d'un modèle cible distinct.

## Configuration contrôlée de départ

Les six campagnes contrôlées C-003 à C-006 et C-009/C-010 doivent partager les
paramètres ci-dessous. Seuls le GPU et le format BF16/FP8 changent dans chaque
comparaison annoncée.

- Modèle : `Qwen3.8-27B`, checkpoints officiels Qwen, tokenizer du dépôt BF16
  épinglé à la révision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`.
- Moteur : vLLM `0.29.0`, même image et même build CUDA lorsque l'architecture
  le permet ; l'image et son digest doivent être consignés dans le run.
- Parser de raisonnement : `qwen3`, afin que le thinking activé en qualité soit
  séparé du contenu final transmis au protocole `file_changes_v1`.
- GPU : un seul accélérateur, tensor parallelism 1, pipeline parallelism 1.
- KV cache : `fp8`, K et V ; aucune modification silencieuse entre les cartes.
- Nombre maximal de séquences vLLM : `16`, supérieur à la concurrence maximale
  initiale de 10 ; cette valeur évite le défaut `1024` incompatible avec les
  blocs Mamba disponibles sur la RTX PRO 6000 et reste commune aux variantes.
- Contexte : cible native 262 144 tokens, validée par une montée progressive
  `64k -> 128k -> 262k`. Une limite inférieure effectivement imposée par le
  moteur doit être enregistrée comme un résultat de capacité, pas masquée.
- Concurrence qualité : 1, slots 1 et prefix caching désactivé.
- Batch qualité : valeur commune conservatrice, à fixer après le smoke mémoire
  et à conserver pour C-003 à C-006, C-009/C-010 et les campagnes NVFP4.
- Thinking : activé ; `reasoning_effort=xhigh` lorsque le serveur et le
  template Qwen le supportent.
- Échantillonnage thinking : température 1.0, `top_p=0.95`, `top_k=20`,
  `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`.
- Seed : 42 lorsque supporté.
- Sortie : plafond initial 32 768 tokens, identique entre les campagnes.
- Flash attention : activée si disponible sur les deux builds ; le nom exact
  de l'option et son état effectif doivent être conservés dans les métadonnées.
- Speculative decoding : désactivé pour la première série qualité afin de ne
  pas ajouter un second modèle ou un backend MTP comme variable expérimentale.

Le contexte 262k est un objectif de validation, pas une promesse de capacité
à pleine charge. Le poids du modèle, le KV cache, les buffers CUDA, les graphes
et les sorties simultanées doivent tous tenir dans la mémoire disponible.

## Pourquoi les paramètres ne seront pas toujours identiques

Pour une comparaison scientifique du matériel, les paramètres doivent être
identiques autant que possible. Sinon, une différence de débit ou de latence
peut venir du batch, du nombre de slots ou du cache et non du GPU.

Pour choisir une configuration exploitable en production, il est au contraire
pertinent d'optimiser chaque carte séparément. Ces résultats seront alors
étiquetés `operational solution comparison` et ne serviront pas à conclure
qu'un GPU est intrinsèquement plus rapide qu'un autre.

La séquence retenue est donc :

1. six campagnes qualité contrôlées C-003 à C-006, C-009 et C-010 ;
2. smoke de compatibilité du checkpoint NVFP4 sur C-011 et C-012 ;
3. deux campagnes qualité/quantification NVFP4, puis leur serving ;
4. profils serving optimisés séparément par carte ;
5. comparaison vLLM de paramètres optimisés par carte, après la série contrôlée.

### Configuration NVFP4

C-011 et C-012 gardent les mêmes entrées, tokenizer, contexte, KV cache et
paramètres de génération que la série BF16/FP8. Leur objectif est de mesurer
l'effet de la quantification sur une carte donnée, pas de comparer directement
le RTX PRO au GB10. Elles restent `exploratory` jusqu'à validation du chargement
et du backend de calcul effectif.

- Checkpoint : `nvidia/Qwen3.8-27B-NVFP4`, révision
  `dbb8f445b3145f8a4c18ddc769f032d57d32867c`.
- Quantification : `NVFP4-MIXED` ; les couches exactes sont celles déclarées
  par le fichier de quantification du checkpoint.
- Moteur : vLLM, avec version et digest d'image enregistrés. Le backend linéaire
  effectivement sélectionné doit être conservé dans les logs.
- KV cache : `fp8`, identique aux campagnes BF16/FP8.
- Première passe : speculative decoding/MTP désactivé ; une campagne MTP
  séparée pourra mesurer le bénéfice opérationnel après la baseline.
- Contexte et concurrence : mêmes paliers `64k -> 128k -> 262k`, puis la même
  matrice serving 1/2/5/10 utilisateurs.

## Pistes de serving opérationnel par plateforme

Les profils C-016 et C-017 ont servi de diagnostics RTX PRO avant la série
contrôlée ; ils ne remplacent pas celle-ci. Les valeurs ci-dessous sont des points
de départ pour de futures campagnes opérationnelles, pas des valeurs garanties.
Chaque changement doit être précédé d'un smoke court et consigné dans la
configuration du run.

### H200

- Commencer par BF16 puis FP8 avec contexte 262k.
- Tester ensuite un contexte supérieur uniquement si la montée de capacité
  précédente est stable.
- Augmenter progressivement `batch_size` et le nombre de slots ; la H200 peut
  être testée avec une enveloppe plus agressive grâce à sa mémoire HBM, mais la
  capacité réelle doit être mesurée avec KV `fp8`, comme dans la série
  contrôlée ; un autre format de KV ferait l'objet d'une campagne distincte.
- Activer le speculative decoding/MTP seulement dans une campagne dédiée,
  après avoir établi le débit sans spéculation.

### RTX PRO 6000 Blackwell Server Edition

- Commencer par BF16 avec contexte 128k puis 262k, et par FP8 avec le même
  protocole de montée.
- Garder un seul slot au smoke initial ; tester 2 puis 4 slots seulement après
  validation de la mémoire et de la stabilité.
- Augmenter le batch par paliers plus prudents que sur H200.
- Tester MTP dans une campagne séparée, car son coût mémoire peut modifier la
  capacité de contexte disponible.

### DGX Spark / GB10

- Identifier le périphérique comme `GB10` et enregistrer l'architecture Arm,
  l'OS/image et le driver réellement visibles dans le conteneur.
- Traiter les 128 Go comme mémoire système unifiée ; ne pas comparer une valeur
  `memory.total` de `nvidia-smi` à de la VRAM discrète sans préciser sa
  signification.
- Commencer par un seul slot, batch conservateur et contexte 64k, puis monter à
  128k et 262k uniquement si le serveur reste stable.
- Conserver séparément les observations de bande passante, pression mémoire
  CPU/GPU et éventuel partage avec l'OS ; ces caractéristiques font partie de
  la comparaison opérationnelle du Spark.

Ces profils ne remplacent pas C-003 à C-006, C-009/C-010 ni C-011/C-012 : ils
répondent à une question d'exploitation et non à une comparaison contrôlée.

## Procédure pour chaque campagne GPU

### 1. Préflight logiciel et matériel

Capturer et conserver :

- commit Git du benchmark ;
- modèle, dépôt, révision, tokenizer et snapshot de poids Safetensors ;
- version du moteur, build CUDA, pilote et OS/image ;
- modèle exact du GPU, mémoire, température et mémoire hôte ;
- commande de lancement complète, paramètres effectifs et logs serveur.

Vérifier également que le checkpoint BF16, FP8 ou NVFP4 provient bien du dépôt
planifié et de la révision planifiée. Pour chaque machine, capturer l'image vLLM exacte,
son digest, la version CUDA et le résultat du chargement avant de lancer la
suite qualité.

### 2. Smoke et montée mémoire

Pour chaque format et chaque carte concernée :

1. démarrer le serveur avec slots 1, batch conservateur et KV `fp8` ;
2. exécuter une requête courte de validation du template et du thinking ;
3. tester environ 64k, 128k puis 262k tokens ;
4. noter la mémoire utilisée, le temps de démarrage, les erreurs HTTP, OOM,
   crash et limite de contexte effective ;
5. arrêter la campagne si le serveur devient instable et conserver le log.

Une capacité refusée par le moteur ou un OOM est un résultat exploitable. Il ne
faut pas relancer silencieusement avec des paramètres différents en conservant
le même identifiant de campagne.

### 3. Qualité

Lancer la suite complète des 74 tâches en mode `repair`, avec le même ordre et
les mêmes budgets pour C-003 à C-006, C-009/C-010 et C-011/C-012. Produire
pour chaque campagne :

- résultats bruts JSON/JSONL non écrasés ;
- synthèse par catégorie ;
- détail tâche par tâche avec commentaire d'échec ;
- Pass@1/2/3, appels, tokens entrée/sortie et temps ;
- état des tâches CTX-01 à CTX-06 et taille de contexte réellement acceptée.

### 4. Serving

Lancer séparément la matrice serving définie dans
`campaigns/gpu/serving-qwen.yaml`, `campaigns/gpu/serving-qwen-fp8.yaml` ou
`campaigns/gpu/serving-qwen-nvfp4.yaml`.
Conserver
la séparation entre `cold` et `shared-prefix`, et ne pas mélanger les mesures
avec les résultats qualité.

### 5. Mise à jour et arrêt propre

Après chaque campagne terminée :

1. générer les rapports ;
2. ajouter la colonne correspondante à `docs/CAMPAIGN_MATRIX.md` seulement si
   les résultats bruts sont présents ;
3. vérifier les tests et la validation de configuration ;
4. commit et push avec l'identifiant de campagne dans le message ;
5. noter tout écart au protocole dans le rapport, sans réécrire les résultats.

## Critères de comparabilité

Une campagne est `controlled hardware comparison` uniquement si le modèle, la
révision, le tokenizer, le format, le moteur, les paramètres de génération, le
contexte, le batch, les slots, le KV cache et les entrées sont identiques. Le
GPU est alors la variable étudiée.

Une campagne est `controlled quantization comparison` si le GPU, le moteur,
l'image, le tokenizer, les paramètres de service et les entrées sont maintenus
constants, tandis que seul le checkpoint/format de quantification change. Pour
NVFP4, cette qualification dépendra du smoke : un changement de version vLLM ou
de backend imposé par la carte doit être signalé comme une comparaison
opérationnelle.

Une campagne devient `operational solution comparison` dès qu'un ou plusieurs
de ces éléments sont adaptés à la carte. Les rapports doivent le dire
explicitement et conserver les paramètres complets de chaque run.

## Références techniques

- [Qwen3.8-27B — fiche modèle](https://huggingface.co/Qwen/Qwen3.8-27B)
- [Qwen3.8-27B — configuration officielle](https://huggingface.co/Qwen/Qwen3.8-27B/tree/main)
- [Qwen3.8-27B-FP8 — dépôt officiel](https://huggingface.co/Qwen/Qwen3.8-27B-FP8/tree/main)
- [Qwen3.8-27B-NVFP4 — checkpoint NVIDIA ModelOpt](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/dbb8f445b3145f8a4c18ddc769f032d57d32867c)
- [vLLM — support Qwen3.8](https://docs.vllm.ai/en/latest/models/supported_models.html)
- [vLLM — support NVIDIA Model Optimizer/NVFP4](https://docs.vllm.ai/en/latest/features/quantization/modelopt/)
- [NVIDIA H200](https://www.nvidia.com/en-gb/data-center/h200/)
- [NVIDIA RTX PRO 6000 Blackwell](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/)
- [NVIDIA DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)
