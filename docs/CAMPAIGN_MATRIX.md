# Matrice des campagnes

Document de suivi des campagnes qualité et serving exécutées. Les colonnes correspondent
aux campagnes ; les lignes gardent les mêmes catégories et métriques pour faciliter les
comparaisons.

La matrice conserve les métriques brutes par campagne. Les analyses comparatives et les
exports prévus au milestone 12 restent à développer. Les liens vers `results/raw/` et
`results/reports/` pointent vers des artefacts locaux ignorés par Git ; ils sont accessibles
sur les postes où ces résultats ont été conservés.

## Campagnes référencées

| ID | Date | Campagne | Rapport |
|---|---|---|---|
| C-001 | 2026-09-16 | Gemma 4 local — baseline, thinking désactivé | [Synthèse](../results/reports/gemma4-local-20260916.md) |
| C-002 | 2026-09-16 | Gemma 4 local — thinking / contexte 100k | [Synthèse](../results/reports/gemma4-thinking-100k-20260916.md) |
| C-016 | 2026-09-21 | Qwen3.8-27B BF16 RTX PRO 6000 — thinking medium | [Résultat brut](../results/raw/campaigns/20260921T110238.257698Z-c-016-81173711/campaign.json) |
| C-017 | 2026-09-21/22 | Qwen3.8-27B Q8/W8A16 RTX PRO 6000 — thinking medium | [Résultat brut](../results/raw/campaigns/20260921T155315.525802Z-c-017-35d4e399/campaign.json) |

Les résultats détaillés sont disponibles dans les rapports associés. Les résultats bruts restent dans results/raw et sont indexés par results/raw/runs.jsonl.

Les campagnes matérielles contrôlées C-003 à C-006, C-009/C-010 et exploratoires NVFP4
C-011/C-012 sont décrites dans [`docs/GPU_CAMPAIGN_PLAN.md`](GPU_CAMPAIGN_PLAN.md). Elles
ne sont pas ajoutées à la matrice de résultats avant leur exécution effective.

## Matrice qualité

Les valeurs de catégorie sont au format réussites/total. Les tokens sont ceux rapportés par l’endpoint OpenAI-compatible et le temps est le temps cumulé des runs qualité.

| Métrique | C-001 | C-002 | C-016 | C-017 |
|---|---:|---:|---:|---:|
| ABAL | 4/4 | 4/4 | 4/4 | 4/4 |
| Axon | 8/10 | 9/10 | 10/10 | 10/10 |
| COBOL | 3/5 | 4/5 | 5/5 | 5/5 |
| Context | 1/6 | 3/6 | 5/6 | 5/6 |
| Delphi | 4/4 | 4/4 | 4/4 | 4/4 |
| Documents | 1/10 | 2/10 | 7/10 | 4/10 |
| E2E | 2/3 | 2/3 | 2/3 | 2/3 |
| Java | 6/8 | 6/8 | 6/8 | 6/8 |
| Spring | 8/10 | 8/10 | 9/10 | 10/10 |
| Web | 5/10 | 5/10 | 8/10 | 8/10 |
| WinDev | 3/4 | 4/4 | 4/4 | 4/4 |
| **Total réussi** | **45/74** | **51/74** | **64/74** | **62/74** |
| Pass@1 | 43/74 | 47/74 | — | — |
| Pass@2 | 45/74 | 51/74 | — | — |
| Pass@3 | 45/74 | 51/74 | — | — |
| Appels modèle | 94 | 101 | — | — |
| Tokens entrée | 83 612 | 212 558 | — | — |
| Tokens générés | 48 041 | 867 269 | — | — |
| Temps cumulé | 30 min 29 s | 2 h 50 min 31 s | 1 h 40 min 29 s | 1 h 00 min 04 s |

C-016 et C-017 sont des profils opérationnels, pas une comparaison contrôlée
de quantification : C-017 utilise le checkpoint tiers
`GotoAI-Inc/Qwen3.8-27B-W8A16`, tandis que C-016 utilise le checkpoint officiel
BF16 Qwen.

## Serving exécuté

| Profil | Couverture | Résultat |
|---|---|---|
| BF16 smoke | 12 cas, concurrence 1/5, contextes 8k/32k/64k, `cold` et `shared-prefix` | Campagne de contrôle partielle |
| BF16 complet | 20 cas, toutes les concurrences et contextes, `shared-prefix` | Terminée |
| Q8 complet | 40 cas, concurrence 1/2/5/10, contextes 8k/32k/64k/100k/200k, `cold` et `shared-prefix` | 540/540 requêtes réussies |

Le détail de la couverture et l'analyse BF16/Q8 sont consignés dans
[`docs/GPU_SESSION_2026-09-22.md`](GPU_SESSION_2026-09-22.md). Les cellules
`cold` non exécutées en BF16 restent explicitement non testées.

## Paramètres des campagnes

### C-001 — Gemma 4 local baseline

- Modèle : unsloth/gemma-4-12B-it-qat-GGUF.
- Quantification : UD-Q4_K_XL ; type GGUF/QAT.
- Révision du modèle : non capturée dans le résultat de cette campagne.
- Endpoint : http://127.0.0.1:8888/v1.
- Matériel : NVIDIA GeForce RTX 5070 Ti Laptop GPU, 12 227 MiB, pilote 582.05.
- Thinking : désactivé.
- Température : 0 ; top-p : 1 ; top-k : non défini ; seed : 42.
- Maximum de sortie configuré : 12 000 tokens.
- Mode : repair, maximum 3 itérations.
- Protocole de sortie : file_changes_v1.
- La configuration serving détaillée n’a pas été capturée dans les résultats de cette campagne.

Cette campagne sert de référence fonctionnelle. Les échecs CTX-02 à CTX-06 étaient déjà des refus de contexte côté serveur ; les autres échecs concernaient principalement la qualité du correctif ou le protocole JSON.

### C-002 — Gemma 4 thinking / contexte 100k

- Modèle : unsloth/gemma-4-12B-it-qat-GGUF, révision 980b060c40a8539ac159e0501a3e0f66a6365af3.
- Quantification : UD-Q4_K_XL ; type GGUF/QAT.
- Endpoint : http://127.0.0.1:8888/v1.
- Matériel : NVIDIA GeForce RTX 5070 Ti Laptop GPU, 12 227 MiB, pilote 582.05.
- Thinking : activé ; preserve_thinking désactivé.
- Température : 1 ; top-p : 0.95 ; top-k : 64 ; min-p effectif : 0 ; seed : 42.
- Maximum de sortie : 12 032 tokens.
- Contexte demandé : 100 000 tokens ; capacité effective annoncée par Unsloth : environ 58 000 tokens.
- KV cache : q8_0 pour K et V.
- Speculative decoding : auto, résolu en draft MTP ; maximum de tokens draft : 2.
- Slots parallèles : 1.
- Batch effectif : 4. Un batch 1/2 provoquait un crash llama.cpp avec MTP ; le batch 4 a permis la campagne complète.
- Mode : repair, maximum 3 itérations.
- Protocole de sortie : file_changes_v1.

CTX-04, CTX-05 et CTX-06 ont été refusés en HTTP 400 à cause de la fenêtre effective. Aucun crash serveur n’a interrompu la campagne après le réglage du batch.

## Règle d’ajout des prochaines campagnes

Pour chaque nouvelle campagne qualité :

1. attribuer l’identifiant suivant, par exemple C-003 ;
2. ajouter la campagne à la liste ci-dessus ;
3. ajouter une colonne dans la matrice qualité ;
4. ajouter un chapitre de paramètres ;
5. conserver le lien vers la synthèse et les résultats bruts ;
6. ne pas modifier les colonnes des campagnes précédentes.
