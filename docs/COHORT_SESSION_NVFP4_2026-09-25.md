# Session cohorte agentique NVFP4 — 25 et 28 septembre 2026

## Objet et état

Série de mesures de cohorte du profil Qwen3.8-27B NVFP4 sans DFlash2, avec
`reasoning_effort: medium`, seed 42 et le pilote fermé de 18 tâches. Le profil
utilise le checkpoint NVIDIA NVFP4 et le tokenizer Qwen épinglés dans la
configuration de qualité C-020. Trois répétitions ont été réalisées à chacun des
niveaux 1, 4, 5, 6, 8 et 10. Les runs à 1–8 agents du 25 septembre utilisent une
RTX PRO 6000 Blackwell Workstation Edition ; les trois runs à 10 agents du
28 septembre utilisent une RTX PRO 6000 Blackwell Server Edition et un autre GPU
UUID. La cellule 10 agents est complète, mais ses durées ne prolongent pas une
courbe directement comparable aux cellules précédentes.

## Runs conservés

| Agents | Run | Campagne brute / télémétrie | Tâches | Makespan | Requêtes / concurrence max. | Tokens entrée / sortie / raisonnement | GPU-Util moyenne / max. | Temp. max. | Puissance pic |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | [campagne](../results/raw/cohort/20260925T114655.349801Z-cohort-a1-64c82a93/campaign.json), [GPU](../results/raw/cohort/20260925T114655.349801Z-cohort-a1-64c82a93/remote-gpu-samples.jsonl) | 18/18 | 446,57 s | 19 / 1 | 104 427 / 29 537 / 24 280 | 93,83 % / 100 % | 74 °C | 420,23 W |
| 1 | 2 | [campagne](../results/raw/cohort/20260925T115458.830078Z-cohort-a1-492dd7d8/campaign.json), [GPU](../results/raw/cohort/20260925T115458.830078Z-cohort-a1-492dd7d8/remote-gpu-samples.jsonl) | 18/18 | 447,26 s | 19 / 1 | 104 427 / 29 537 / 24 280 | 94,42 % / 100 % | 70 °C | 417,95 W |
| 1 | 3 | [campagne](../results/raw/cohort/20260925T120957.534167Z-cohort-a1-81a73325/campaign.json), [GPU](../results/raw/cohort/20260925T120957.534167Z-cohort-a1-81a73325/remote-gpu-samples.jsonl) | 18/18 | 446,44 s | 19 / 1 | 104 427 / 29 537 / 24 280 | 94,67 % / 100 % | 75 °C | 420,74 W |
| 4 | 1 | [campagne](../results/raw/cohort/20260925T121732.553091Z-cohort-a4-0eb27965/campaign.json), [GPU](../results/raw/cohort/20260925T121732.553091Z-cohort-a4-0eb27965/remote-gpu-samples.jsonl) | 18/18 | 180,57 s | 20 / 4 | 105 163 / 34 111 / 28 402 | 99,98 % / 100 % | 70 °C | 405,45 W |
| 4 | 2 | [campagne](../results/raw/cohort/20260925T122404.305136Z-cohort-a4-1fdbc1bc/campaign.json), [GPU](../results/raw/cohort/20260925T122404.305136Z-cohort-a4-1fdbc1bc/remote-gpu-samples.jsonl) | 17/18 | 166,30 s | 19 / 4 | 104 427 / 29 360 / 24 022 | 99,31 % / 100 % | 68 °C | 408,69 W |
| 4 | 3 | [campagne](../results/raw/cohort/20260925T122723.732182Z-cohort-a4-9b41eeaa/campaign.json), [GPU](../results/raw/cohort/20260925T122723.732182Z-cohort-a4-9b41eeaa/remote-gpu-samples.jsonl) | 18/18 | 168,55 s | 19 / 4 | 104 427 / 29 374 / 24 182 | 98,97 % / 100 % | 69 °C | 410,55 W |
| 5 | 1 | [campagne](../results/raw/cohort/20260925T123019.341399Z-cohort-a5-6186ca84/campaign.json), [GPU](../results/raw/cohort/20260925T123019.341399Z-cohort-a5-6186ca84/remote-gpu-samples.jsonl) | 17/18 | 157,61 s | 19 / 5 | 104 427 / 29 604 / 24 269 | 99,26 % / 100 % | 71 °C | 403,25 W |
| 5 | 2 | [campagne](../results/raw/cohort/20260925T123454.288822Z-cohort-a5-00d297c7/campaign.json), [GPU](../results/raw/cohort/20260925T123454.288822Z-cohort-a5-00d297c7/remote-gpu-samples.jsonl) | 17/18 | 158,55 s | 19 / 5 | 104 427 / 29 748 / 24 272 | 99,71 % / 100 % | 68 °C | 408,13 W |
| 5 | 3 | [campagne](../results/raw/cohort/20260925T123736.203510Z-cohort-a5-1062895f/campaign.json), [GPU](../results/raw/cohort/20260925T123736.203510Z-cohort-a5-1062895f/remote-gpu-samples.jsonl) | 17/18 | 162,63 s | 19 / 5 | 104 427 / 31 592 / 26 273 | 98,73 % / 100 % | 70 °C | 403,43 W |
| 6 | 1 | [campagne](../results/raw/cohort/20260925T124031.095293Z-cohort-a6-8b05cc6f/campaign.json), [GPU](../results/raw/cohort/20260925T124031.095293Z-cohort-a6-8b05cc6f/remote-gpu-samples.jsonl) | 17/18 | 194,61 s | 21 / 6 | 106 307 / 37 353 / 31 474 | 99,91 % / 100 % | 71 °C | 416,44 W |
| 6 | 2 | [campagne](../results/raw/cohort/20260925T124523.340462Z-cohort-a6-d8069478/campaign.json), [GPU](../results/raw/cohort/20260925T124523.340462Z-cohort-a6-d8069478/remote-gpu-samples.jsonl) | 18/18 | 156,64 s | 19 / 6 | 104 427 / 32 044 / 26 508 | 99,25 % / 100 % | 68 °C | 407,60 W |
| 6 | 3 | [campagne](../results/raw/cohort/20260925T130919.465602Z-cohort-a6-c7db7959/campaign.json), [GPU](../results/raw/cohort/20260925T130919.465602Z-cohort-a6-c7db7959/remote-gpu-samples.jsonl) | 17/18 | 155,65 s | 19 / 6 | 104 427 / 30 943 / 25 595 | 98,69 % / 100 % | 65 °C | 414,25 W |
| 8 | 1 | [campagne](../results/raw/cohort/20260925T131312.188466Z-cohort-a8-551b2f2a/campaign.json), [GPU](../results/raw/cohort/20260925T131312.188466Z-cohort-a8-551b2f2a/remote-gpu-samples.jsonl) | 17/18 | 150,87 s | 21 / 8 | 105 776 / 35 589 / 29 261 | 98,64 % / 100 % | 67 °C | 409,51 W |
| 8 | 2 | [campagne](../results/raw/cohort/20260925T135303.674464Z-cohort-a8-97874a01/campaign.json), [GPU](../results/raw/cohort/20260925T135303.674464Z-cohort-a8-97874a01/remote-gpu-samples.jsonl) | 17/18 | 149,13 s | 19 / 8 | 104 427 / 31 160 / 25 789 | 98,53 % / 100 % | 65 °C | 414,40 W |
| 8 | 3 | [campagne](../results/raw/cohort/20260925T135539.241196Z-cohort-a8-21c71aa3/campaign.json), [GPU](../results/raw/cohort/20260925T135539.241196Z-cohort-a8-21c71aa3/remote-gpu-samples.jsonl) | 18/18 | 146,57 s | 19 / 8 | 104 427 / 31 278 / 26 055 | 99,12 % / 100 % | 69 °C | 404,99 W |
| 10 | 1 | [campagne](../results/raw/cohort/20260928T101806.832791Z-cohort-a10-1d5dcdc9/campaign.json), [GPU](../results/raw/cohort/20260928T101806.832791Z-cohort-a10-1d5dcdc9/remote-gpu-samples.jsonl) | 17/18 | 389,63 s | 20 / 10 | 111 115 / 33 534 / 27 502 | 40,86 % / 100 % | 46 °C | 400,51 W |
| 10 | 2 | [campagne](../results/raw/cohort/20260928T103321.606962Z-cohort-a10-b8c8721e/campaign.json), [GPU](../results/raw/cohort/20260928T103321.606962Z-cohort-a10-b8c8721e/remote-gpu-samples.jsonl) | 17/18 | 260,79 s | 18 / 10 | 103 061 / 23 156 / 18 001 | 28,91 % / 100 % | 44 °C | 253,82 W |
| 10 | 3 | [campagne](../results/raw/cohort/20260928T103936.648130Z-cohort-a10-cc8febac/campaign.json), [GPU](../results/raw/cohort/20260928T103936.648130Z-cohort-a10-cc8febac/remote-gpu-samples.jsonl) | 17/18 | 260,78 s | 18 / 10 | 103 061 / 22 624 / 17 239 | 27,20 % / 100 % | 43 °C | 252,77 W |

- Configuration commune : `benchmark.qwen3.8-nvfp4-medium-thinking.yaml`, SHA-256
  `e5b3387cfbe4c4e71f701eba1796741f15a682ec4b9c9dbc5e5c167191b86674`.
- Les dix-huit manifestes déclarent `reasoning_effort: medium`, seed 42, Qwen
  `dbb8f445b3145f8a4c18ddc769f032d57d32867c` et tokenizer
  `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`. Les 18 tâches et leurs révisions
  sont identiques dans les dix-huit runs. Les trois runs à 1 agent ont le même profil
  de 19 appels et les mêmes comptes de tokens. Les runs à 4 agents ont
  respectivement 20, 19 et 19 appels ; les trois runs à 5 agents ont 19 appels,
  ceux à 6 agents 21, 19 et 19 appels, les runs à 8 agents 21, 19 et 19
  appels, et ceux à 10 agents 20, 18 et 18 appels. Le nombre de tokens varie avec
  l'ordonnancement et les reprises.
- Les trois runs à 1 agent ont terminé sans erreur de runner ni tâche échouée. Le
  premier et le troisième run à 4 agents ont réussi 18/18 tâches ; le deuxième,
  17/18. Les trois runs à 5 agents ont chacun réussi 17/18 ; à 6 agents, le
  premier et le troisième ont réussi 17/18 ; le deuxième a réussi 18/18. À
  8 agents, les deux premiers runs ont réussi 17/18 et le troisième 18/18. Tous
  les échecs concernent `DOC-03` : validation échouée aux niveaux 4 et 5, au
  troisième run à 6 agents et aux deux premiers runs à 8 agents. Le premier run à
  6 agents a également eu deux erreurs `ChangeProtocolError`. À 10 agents, les
  trois runs ont réussi 17/18 tâches et échoué sur `DOC-03` à la validation.
  Aucun run n'a eu d'erreur de runner ni de requête modèle en échec. Les durées
  de tâche p50/p95 sont
  14,34 s / 126,97 s, 14,42 s / 127,01 s, 14,42 s / 127,25 s,
  18,32 s / 148,88 s, 19,90 s / 139,56 s, 19,00 s / 140,06 s,
  19,32 s / 138,29 s, 19,90 s / 136,65 s, 22,80 s / 140,06 s,
  21,50 s / 158,93 s, 20,39 s / 137,11 s, 19,88 s / 137,98 s,
  21,15 s / 140,98 s, 25,05 s / 137,72 s et 25,14 s / 137,91 s ; aux runs à 10
  agents correspondent 150,88 s / 389,63 s, 128,94 s / 235,69 s et 119,08 s /
  249,68 s.
- Les quinze premiers runs identifient la RTX PRO 6000 Blackwell Workstation
  Edition, GPU UUID `GPU-6d74fd11-1390-0f03-f603-058c602acf83`, driver 595.71.05
  et mémoire utilisée maximale 91 654 MiB. Les trois runs à 10 agents identifient
  une RTX PRO 6000 Blackwell Server Edition, GPU UUID
  `GPU-b368df4b-6e60-6e55-21ca-6547d4c3f036`, le même driver et mémoire utilisée
  maximale 91 599 MiB. Chaque groupe a une télémétrie distante échantillonnée à
  une seconde ; ces métriques viennent du serveur, pas du runner local.
- La mémoire GPU `nvidia-smi` est conservée comme télémétrie brute, pas comme
  mesure de la demande mémoire des requêtes. La commande de lancement ne fixe pas
  `gpu_memory_utilization` ; vLLM 0.29 utilise alors son défaut de 0,92 pour le
  budget du moteur et déduit la capacité du KV cache à partir de ce budget
  ([documentation vLLM](https://docs.vllm.ai/en/v0.29.0/api/vllm/config/cache/)).
  Les pics autour de 91,6 Go ne justifient donc pas à eux seuls de réduire le
  contexte ; le cache KV disponible et les résultats des requêtes sont à examiner.
- Les dix-huit manifestes déclarent que le worktree était modifié au lancement et
  le commit `9e898e335aac4b8dd8cad0060254e121de71d4a4` ; chaque résultat conserve
  l'empreinte de sa configuration.
- Les manifestes du profil sans DFlash2 indiquent `prefix_caching: false` et
  enregistrent une commande serveur dérivée de ce profil. La commande Vast.ai
  fournie pour l'instance utilisée comportait toutefois `--enable-prefix-caching`.
  Les manifestes ne décrivent donc pas fidèlement cette option du serveur et les
  campagnes ne conservent pas les hits réels du cache. Ne pas conclure que le
  cache était désactivé à partir de ce seul champ ; voir aussi le
  [rapport de cohorte NVFP4 + DFlash2](COHORT_SESSION_NVFP4_DFLASH2_2026-09-28.md).

## Suite

Le protocole de cohorte recommande trois répétitions par niveau utilisé dans une
comparaison. À 1 agent, les trois runs ont réussi 54/54 tâches, avec un makespan
médian de 446,57 s (446,44–447,26 s). À 4 agents, ils totalisent 53/54 tâches
réussies et un makespan médian de 168,55 s (166,30–180,57 s). À 5 agents, les
trois runs totalisent 51/54, tous avec `DOC-03` en échec ; le makespan médian est
158,55 s (157,61–162,63 s). À 6 agents, les trois runs totalisent
52/54 avec des makespans de 194,61 s, 156,64 s et 155,65 s ; la médiane est
156,64 s (155,65–194,61 s). À 8 agents, les trois runs totalisent 52/54 ; les
deux premiers ont échoué sur `DOC-03` à la validation et le troisième a réussi
18/18. Leur makespan médian est 149,13 s (146,57–150,87 s). À 10 agents, les
trois runs totalisent 51/54 tâches réussies, tous avec `DOC-03` en échec de
validation ; le makespan médian est 260,79 s (260,78–389,63 s). Les répétitions
de cette cellule ont été exécutées sur la Server Edition, alors que les autres
niveaux l'ont été sur la Workstation Edition : ne pas interpréter l'écart de
makespan comme un effet isolé du nombre d'agents.
