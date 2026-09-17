# Checklist de location GPU

## Avant location — poste local

- [ ] Le préflight local retourne `ready` :

  ```powershell
  python scripts/prepare_gpu_campaign.py `
    --campaign-id C-003 `
    --config benchmark.qwen3.8-bf16.yaml `
    --serving-config campaigns/gpu/serving-qwen.yaml `
    --require-clean
  ```
- [ ] Le commit, la révision de tâche et les commits des snapshots de modèles
      sont figés.
- [ ] L'image et la version du moteur sont figées.
- [ ] La configuration qualité et serving pointe vers le même modèle exact.
- [ ] Le KV cache, le tensor/pipeline parallelism et la longueur de contexte
      sont identiques dans les configurations qualité et serving.
- [ ] `python -m unittest discover -s tests -v` passe.
- [ ] La commande de campagne et la destination de sauvegarde sont prêtes.
- [ ] La clé Vast.ai et les éventuels tokens sont dans l'environnement, jamais
      dans un YAML, un template ou un résultat.

## Après connexion — machine GPU

- [ ] `capture_gpu_environment.py` passe pour le modèle et le nombre de GPU attendus.
- [ ] Le dépôt, le commit du snapshot et le commit du tokenizer sont enregistrés
      dans le préflight ; pour Qwen, les poids Safetensors sont chargés depuis ce
      snapshot immuable.
- [ ] Le serveur démarre avec le moteur et la configuration prévus.
- [ ] Si le template a déjà lancé Supervisor, `entrypoint.sh` n'est pas relancé
      manuellement ; le service vLLM est démarré via Supervisor ou la commande
      directe versionnée avec `--max-num-seqs 16` et `--reasoning-parser qwen3`.
- [ ] Pour C-011/C-012, le checkpoint NVFP4 est chargé avec le backend attendu
      et sans avertissement de fallback non documenté.
- [ ] Le log de démarrage est conservé.
- [ ] Le endpoint smoke `/models` + génération courte passe.
- [ ] Le contexte 64k puis 128k puis 262k est testé avec les mêmes paramètres.

## Avant arrêt

- [ ] Les résultats qualité sont présents dans `results/raw/`.
- [ ] Le résultat serving et les logs sont présents.
- [ ] Le préflight hôte est copié avec la campagne.
- [ ] Les fichiers sont vérifiés et sauvegardés hors de l'instance.
- [ ] Les écarts et OOM sont documentés.
