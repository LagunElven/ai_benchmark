# Plan GPU et templates de configuration

`plan.yaml` décrit les huit campagnes prévues C-003 à C-006, C-009/C-010 et
C-011/C-012.
Le benchmark cible vLLM avec les dépôts Qwen au format Safetensors.
Les profils serving Qwen déclarent également le tokenizer Hugging Face exact
utilisé pour calibrer les contextes.
Les révisions immuables des snapshots sont listées dans le plan. Les `null`
restants concernent les informations qui ne peuvent être connues qu'après
sélection du fournisseur (GPU, image, pilote, digest d'image, batch, etc.).

Les deux variantes planifiées sont :

- `bf16` : snapshot officiel `Qwen/Qwen3.8-27B` ;
- `fp8` : snapshot officiel `Qwen/Qwen3.8-27B-FP8` ;
- `nvfp4` : checkpoint distinct `nvidia/Qwen3.8-27B-NVFP4`, produit avec
  NVIDIA Model Optimizer et réservé aux campagnes Blackwell.

Les templates suivants à la racine du dépôt ne remplacent pas le plan et ne
constituent pas encore des configurations prêtes à exécuter :

- `benchmark.qwen3.8-bf16.yaml`
- `benchmark.qwen3.8-fp8.yaml`
- `benchmark.qwen3.8-nvfp4.yaml`
- `serving-qwen.yaml`
- `serving-qwen-smoke.yaml`
- `serving-qwen-smoke-no-prefix.yaml`
- `serving-qwen-rtx-pro-6000-full.yaml`
- `serving-qwen-fp8.yaml`
- `serving-qwen-nvfp4.yaml`

Copier le template choisi vers un fichier associé à la campagne. Le préflight
local contrôlera ensuite la révision, la quantification, le moteur et les autres
correspondances sans modifier les templates.

Exemple pour C-003 :

```powershell
Copy-Item benchmark.qwen3.8-bf16.yaml .tmp/benchmark-C-003.yaml
Copy-Item campaigns/gpu/serving-qwen.yaml .tmp/serving-C-003.yaml
python scripts/prepare_gpu_campaign.py `
  --campaign-id C-003 `
  --config .tmp/benchmark-C-003.yaml `
  --serving-config .tmp/serving-C-003.yaml `
  --require-clean
```

La configuration générée/dupliquée est un input de campagne ; elle doit être
conservée avec le préflight et les résultats, même si elle reste hors Git.
