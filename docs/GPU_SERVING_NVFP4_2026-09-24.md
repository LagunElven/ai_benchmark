# Serving NVFP4 — 24 septembre 2026

## Campagne

- Résultat brut : [`campaign.json`](../results/raw/serving/20260924T162232.458742Z-serving-f53158b6/campaign.json)
- Télémétrie distante : [`remote-gpu-samples.jsonl`](../results/raw/serving/20260924T162232.458742Z-serving-f53158b6/remote-gpu-samples.jsonl)
- Run : `20260924T162232.458742Z-serving-f53158b6`, statut `completed`
- Profil : `enterprise-serving-qwen3.8-nvfp4-vllm-shared-prefix`, version `0.25.20`
- Commit du runner : `bef22d570254ba263ddc1863a57a0903a90e647b`
- Durée : 18 min 54,6 s, du 16:22:32 au 16:41:27 UTC

## Configuration exécutée

- Modèle : `nvidia/Qwen3.8-27B-NVFP4`, révision `dbb8f445b3145f8a4c18ddc769f032d57d32867c`
- Tokenizer : `Qwen/Qwen3.8-27B`, révision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`
- Quantification : `NVFP4-MIXED`; cache KV `fp8`
- Moteur : vLLM 0.29.0, TP=1, PP=1, longueur maximale configurée 262 144, 16 séquences
- Prefix caching activé ; mode de requête `shared-prefix` uniquement
- Concurrences : 1/2/5/10 ; contextes : 8k/32k/64k/100k/200k
- 20 répétitions et un warmup par cas ; thinking désactivé ; sortie plafonnée à 256 tokens

## Résultats

| Mesure | Résultat |
|---|---:|
| Cas terminés | 20/20 |
| Requêtes mesurées réussies | 1 800/1 800 |
| Échecs, timeouts, flux incomplets, OOM | 0 |
| Tokens d'entrée rapportés par l'endpoint | 145 442 220 |
| Tokens de sortie rapportés par l'endpoint | 15 185 |
| GPU distant | RTX PRO 6000 Blackwell Server Edition, 96 GiB |
| Mémoire GPU maximale utilisée | 90 987 / 97 887 MiB |
| Utilisation GPU moyenne / maximale | 49,8 % / 100 % |
| Puissance maximale / limite observée | 554,14 / 600 W |
| Température maximale | 65 °C |
| Échantillons GPU distants | 1 134, environ une mesure par seconde |

TTFT médian aux deux extrêmes de contexte :

| Concurrence | 8k | 200k | TPOT médian à 200k | Débit de sortie agrégé à 200k |
|---:|---:|---:|---:|---:|
| 1 | 0,217 s | 1,551 s | 12,7 ms/token | 2,8 tokens/s |
| 2 | 0,348 s | 1,805 s | 15,5 ms/token | 4,4 tokens/s |
| 5 | 0,326 s | 3,250 s | 42,8 ms/token | 6,8 tokens/s |
| 10 | 0,440 s | 6,072 s | 69,7 ms/token | 8,5 tokens/s |

À 10 requêtes simultanées et 200k tokens, le p95 TTFT est de 8,471 s et la latence
totale médiane de 7,184 s. Les appels ont généré en moyenne environ 8,4 tokens chacun ;
ce run caractérise donc surtout le préfill et la montée de latence avec le contexte,
pas un long décodage continu à 256 tokens par requête.

## Limites d'interprétation

- Les 1 800 requêtes ont utilisé `shared-prefix`, mais aucune métrique de hit/miss KV
  n'a été exposée par le serveur (`kv_cache.reported: false`). Le run ne quantifie donc
  pas le bénéfice réel du prefix caching.
- Les métriques locales du runner concernent sa RTX 5070 Ti et ne décrivent pas le
  serveur. Les chiffres GPU ci-dessus proviennent du sampler SSH distant.
- La mesure atteint 200k tokens d'entrée, tandis que 262 144 est la limite maximale
  configurée dans vLLM ; le run ne teste pas une entrée complète à 262 144 tokens.
- Il s'agit d'une matrice de débit courte et bornée, avec thinking désactivé et sorties
  courtes. Elle ne représente pas une charge interactive soutenue de plusieurs heures.

La campagne est répertoriée dans [`CAMPAIGN_MATRIX.md`](CAMPAIGN_MATRIX.md). Le profil
reproductible est [`serving-qwen-nvfp4-shared-prefix.yaml`](../campaigns/gpu/serving-qwen-nvfp4-shared-prefix.yaml).
