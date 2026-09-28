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
| C-011 | 2026-09-25 | Qwen3.8-27B NVFP4 RTX PRO 6000 — thinking effectif xhigh | [Résultat brut](../results/raw/campaigns/20260925T080205.982250Z-c-011-f1b4da84/campaign.json) |
| C-020 | 2026-09-25 | Qwen3.8-27B NVFP4 RTX PRO 6000 — reasoning effort medium | [Résultat brut](../results/raw/campaigns/20260925T105415.271097Z-c-020-b3938e5e/campaign.json) |
| C-021 | 2026-09-28 | Qwen3.8-27B NVFP4 + DFlash2 — reasoning effort medium | [Résultat brut](../results/raw/campaigns/20260928T114254.844647Z-c-021-6dd76751/campaign.json) |
| C-016 | 2026-09-21 | Qwen3.8-27B BF16 RTX PRO 6000 — thinking medium | [Résultat brut](../results/raw/campaigns/20260921T110238.257698Z-c-016-81173711/campaign.json) |
| C-017 | 2026-09-21/22 | Qwen3.8-27B Q8/W8A16 RTX PRO 6000 — thinking medium | [Résultat brut](../results/raw/campaigns/20260921T155315.525802Z-c-017-35d4e399/campaign.json) |

Les résultats détaillés sont disponibles dans les rapports associés ou les résultats bruts liés. Les artefacts bruts restent dans `results/raw/` et sont indexés par `results/raw/runs.jsonl`.

Les campagnes matérielles contrôlées C-003 à C-006, C-009/C-010 et NVFP4 C-012 sont
décrites dans [`docs/GPU_CAMPAIGN_PLAN.md`](GPU_CAMPAIGN_PLAN.md) et restent à exécuter.
C-011 figure maintenant dans les campagnes référencées et est résumé ci-dessous.

### C-011 — qualité NVFP4 sans DFlash2

La campagne s'est terminée avec 44/74 tâches réussies : 27 échecs de protocole, 2
échecs fonctionnels et 1 rejet de capacité de contexte. Elle a produit 600 329 tokens
de sortie, dont 585 486 tokens de raisonnement, en 2 h 27 min. La configuration
n'envoyait pas `reasoning_effort` ; le défaut du template Qwen était `xhigh`.

C-020 reprend le même checkpoint, les mêmes tâches/révisions et le même seed, sur le
même GPU UUID, en transmettant `reasoning_effort: medium` pour les 74 tâches. La
configuration ne diffère de celle de C-011 que par ce paramètre et son nom/version.
C-020 a réussi 59/74 tâches, avec 2 échecs de protocole, 12 échecs fonctionnels et 1
rejet de contexte. Il a produit 132 417 tokens, dont 108 152 de raisonnement, en
35 min 23 s. Le temps et les tokens de raisonnement baissent nettement ; la réussite
totale progresse, mais les erreurs fonctionnelles augmentent. Cette paire suggère un
effet important de l'effort sur le budget de génération et le protocole, sans suffire
à généraliser au-delà de cette répétition.

CTX-06 échoue dans les deux campagnes : l'entrée plus les 6 000 tokens de sortie
réservés dépassent la limite de 262 144 d'un token. `medium` ne change pas cette
réservation. La télémétrie a identifié une RTX PRO 6000 Blackwell Workstation Edition
(pilote 595.71.05) dans les deux runs. Les bruts et les échantillons distants sont liés
depuis les résultats de campagne ci-dessus.

### C-021 — qualité NVFP4 avec DFlash2

C-021 a terminé avec 57/74 tâches réussies : 16 échecs fonctionnels, aucun échec
de protocole et un rejet de capacité de contexte. C-020 a réussi 59/74, avec
12 échecs fonctionnels, deux échecs de protocole et le même nombre de rejets de
capacité. Cette différence ne permet pas d'isoler l'effet DFlash2 : la campagne
C-021 n'a pas demandé de télémétrie GPU distante, et le manifeste de C-020 ne
reflète pas l'option de cache de préfixe fournie dans la commande effective du
template Vast.ai. Les hits du cache ne sont pas disponibles dans les deux
campagnes. Voir le [rapport DFlash2](COHORT_SESSION_NVFP4_DFLASH2_2026-09-28.md).

## Matrice qualité

Les valeurs de catégorie sont au format réussites/total. Les tokens sont ceux rapportés par l’endpoint OpenAI-compatible et le temps est le temps cumulé des runs qualité.

| Métrique | C-001 | C-002 | C-011 | C-020 | C-016 | C-017 |
|---|---:|---:|---:|---:|---:|---:|
| ABAL | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Axon | 8/10 | 9/10 | 10/10 | 9/10 | 10/10 | 10/10 |
| COBOL | 3/5 | 4/5 | 3/5 | 5/5 | 5/5 | 5/5 |
| Context | 1/6 | 3/6 | 4/6 | 5/6 | 5/6 | 5/6 |
| Delphi | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| Documents | 1/10 | 2/10 | 0/10 | 3/10 | 7/10 | 4/10 |
| E2E | 2/3 | 2/3 | 2/3 | 2/3 | 2/3 | 2/3 |
| Java | 6/8 | 6/8 | 6/8 | 6/8 | 6/8 | 6/8 |
| Spring | 8/10 | 8/10 | 6/10 | 10/10 | 9/10 | 10/10 |
| Web | 5/10 | 5/10 | 1/10 | 7/10 | 8/10 | 8/10 |
| WinDev | 3/4 | 4/4 | 4/4 | 4/4 | 4/4 | 4/4 |
| **Total réussi** | **45/74** | **51/74** | **44/74** | **59/74** | **64/74** | **62/74** |
| Pass@1 | 43/74 | 47/74 | 38/74 | 56/74 | — | — |
| Pass@2 | 45/74 | 51/74 | 43/74 | 59/74 | — | — |
| Pass@3 | 45/74 | 51/74 | 44/74 | 59/74 | — | — |
| Appels modèle | 94 | 101 | 132 | 82 | — | — |
| Tokens entrée | 83 612 | 212 558 | 593 046 | 533 322 | — | — |
| Tokens générés | 48 041 | 867 269 | 600 329 | 132 417 | — | — |
| Temps cumulé | 30 min 29 s | 2 h 50 min 31 s | 2 h 27 min 06 s | 35 min 23 s | 1 h 40 min 29 s | 1 h 00 min 04 s |

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
| NVFP4 shared-prefix | 20 cas, concurrence 1/2/5/10, contextes 8k/32k/64k/100k/200k | 1 800/1 800 requêtes réussies ; [rapport](GPU_SERVING_NVFP4_2026-09-24.md) |
| NVFP4 + DFlash2 shared-prefix | 20 cas, concurrence 1/2/5/10, contextes 8k/32k/64k/100k/200k, thinking medium | 1 800/1 800 requêtes réussies ; GPU distant et hits KV-cache non disponibles dans l'artefact |

La campagne NVFP4 + DFlash2 est référencée par le profil
[`serving-qwen-nvfp4-dflash2-shared-prefix-medium-thinking.yaml`](../campaigns/gpu/serving-qwen-nvfp4-dflash2-shared-prefix-medium-thinking.yaml)
et son résultat brut se trouve dans
[`results/raw/serving/20260928T125148.158580Z-serving-dc5fca88/campaign.json`](../results/raw/serving/20260928T125148.158580Z-serving-dc5fca88/campaign.json).
À 10 utilisateurs, le TTFT p95 est de 67,75 s à 64k tokens et 205,16 s à 100k ;
les latences longues sont à interpréter sans compteurs de cache ni télémétrie GPU distante.

Le détail de la couverture et l'analyse BF16/Q8 sont consignés dans
[`docs/GPU_SESSION_2026-09-22.md`](GPU_SESSION_2026-09-22.md). Les cellules
`cold` non exécutées en BF16 restent explicitement non testées.

## Pilote de cohorte agentique

Le 23 septembre 2026, 13 cohortes Qwen3.8-27B-FP8 + DFlash2 ont été exécutées sur 18 tâches,
avec 1/4/5/6/8/10 agents. Les données brutes restent sous `results/raw/cohort/` ; la synthèse,
les limites et les liens par campagne sont dans
[`docs/COHORT_SESSION_2026-09-23.md`](COHORT_SESSION_2026-09-23.md). Cette session est
exploratoire : elle ne comprend pas de cohorte FP8 sans DFlash2 appariée et ne mesure pas les
hits du prefix cache ni l'utilisation du GPU distant.

Le 24 septembre, 18 runs FP8 sans DFlash2 ont été retenus, trois par niveau
d'agents (1/4/5/6/8/10). Ils ont tous enregistré la télémétrie du même GPU UUID
et du pilote distant 595.71.05. Les réussites cumulées sont : 54/54 à 1 agent,
52/54 à 4 agents, 54/54 à 5 agents, 52/54 à 6 agents, puis 54/54 à 8 et 10
agents. Les quatre échecs concernent `DOC-03`. Un run initial supplémentaire à 5
agents a réussi 17/18 tâches, mais son sampler SSH s'est terminé avec le statut
255 ; il est conservé hors de la série télémétrée, et sa reprise réussie est
incluse parmi les trois runs retenus. Tous les artefacts déclarent le pilote
610.43.02 et CUDA 13.3 ; les télémétries disponibles rapportent le pilote distant
595.71.05. Sur ce même GPU UUID, trois cohortes FP8 + DFlash2 à 1 agent ont
réussi 18/18 tâches en 265,37 s, 251,55 s et 251,71 s ; à 4 agents, trois runs
ont donné 18/18 en 111,79 s, 17/18 en 68,59 s et 18/18 en 111,84 s. Leurs détails
et la comparaison exploratoire sont dans
[`docs/COHORT_SESSION_2026-09-24-DFLASH2.md`](COHORT_SESSION_2026-09-24-DFLASH2.md).
À 5 agents, trois runs DFlash2 ont réussi 17/18, 17/18 et 18/18 tâches en
110,03 s, 49,96 s et 109,75 s.
À 6 agents, les deux premiers runs DFlash2 ont réussi 17/18 tâches chacun, en
94,31 s et 109,87 s ; le troisième a réussi 18/18 en 86,98 s.
À 8 agents, trois runs DFlash2 ont réussi 18/18, 18/18 et 17/18 tâches, en
67,19 s, 104,81 s et 64,24 s.
À 10 agents, les trois runs DFlash2 ont tous réussi 17/18 tâches, en 47,67 s,
37,15 s et 83,31 s ; les trois échecs concernent `DOC-03`. La série DFlash2
compte 18 runs, trois par niveau, avec 315/324 tâches réussies et une
télémétrie GPU disponible pour chaque run ; les neuf échecs concernent
`DOC-03`.
La série sans DFlash2 fournit trois observations matérielles par niveau, mais
les conditions de prefix cache/warmup ne sont pas normalisées et la comparaison
complète avec DFlash2 reste à établir. Les résultats, les échantillons bruts et
les limites de comparaison sont dans
[`docs/COHORT_SESSION_2026-09-24.md`](COHORT_SESSION_2026-09-24.md).

Le 25 septembre, les trois runs NVFP4 sans DFlash2 en thinking medium ont réussi
54/54 tâches à 1 agent, en 446,57 s, 447,26 s et 446,44 s. À 4 agents, ils ont
réussi 53/54 tâches en 180,57 s, 166,30 s et 168,55 s ; l'échec concerne
`DOC-03`. À 5 agents, ils ont réussi 51/54 tâches en 157,61 s, 158,55 s et
162,63 s, avec `DOC-03` en échec à chaque run. À 6 agents, les trois runs ont
totalisé 52/54 tâches en 194,61 s, 156,64 s et 155,65 s. Les deux échecs
concernent `DOC-03` : le premier run a eu deux erreurs `ChangeProtocolError`, et
le troisième un échec de validation. Les trois runs à 8 agents ont totalisé
52/54 tâches en 150,87 s, 149,13 s et 146,57 s ; les deux premiers ont échoué
sur `DOC-03` à la validation. Ces quinze runs disposent de la télémétrie distante
du même GPU UUID, une RTX PRO 6000 Blackwell Workstation Edition. Le 28 septembre,
trois runs à 10 agents ont chacun réussi 17/18 tâches en 389,63 s, 260,79 s et
260,78 s ; `DOC-03` a échoué à la validation dans les trois runs. Ils ont atteint
10 requêtes modèle simultanées et partagent une télémétrie GPU, mais proviennent
d'une RTX PRO 6000 Blackwell Server Edition avec un UUID différent. Les trois
répétitions sont donc disponibles aux six niveaux 1/4/5/6/8/10, mais les durées
des cellules ne forment pas une comparaison directe entre niveaux d'agents.
Voir le [rapport NVFP4](COHORT_SESSION_NVFP4_2026-09-25.md).

Le 28 septembre, 18 cohortes NVFP4 + DFlash2 ont été exécutées, trois par niveau
de 1/4/5/6/8/10 agents. Elles totalisent 311/324 tâches réussies ; les 13 échecs
concernent `DOC-03`. Chaque run a capturé le GPU distant, une RTX PRO 6000
Blackwell Server Edition. À 10 agents, le makespan médian est de 82,21 s contre
260,79 s pour les cohortes NVFP4 sans DFlash2 du même UUID. Cette différence est
un signal opérationnel, mais les hits cache ne sont pas capturés et le manifeste
sans DFlash déclare un état de cache en contradiction avec la commande du template
Vast.ai. Les autres niveaux sans DFlash2 utilisaient la Workstation Edition.
Voir le [rapport de cohorte NVFP4 + DFlash2](COHORT_SESSION_NVFP4_DFLASH2_2026-09-28.md)
pour les campagnes brutes et les limites de comparaison.

L'analyse des défaillances qualité de C-018/C-019 et de DOC-03 est consignée dans
le [rapport d'analyse GPU du 24 septembre](GPU_FAILURE_ANALYSIS_2026-09-24.md).

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
