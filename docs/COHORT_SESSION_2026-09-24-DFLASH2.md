# Cohorte FP8 + DFlash2 — 24 septembre 2026

## Objet

Série de cohortes Qwen3.8-27B-FP8 avec le draft BF16 DFlash2 sur le serveur
utilisé pour les runs FP8 sans DFlash2 du 24 septembre. Le runner utilise le
profil medium, le KV cache FP8, le prefix caching, vLLM 0.29.0 et le même plan de
18 tâches. Le serveur a exposé le GPU UUID
`GPU-6785a083-d5a0-769c-663d-f7058894e22e`, déjà observé dans la série sans
DFlash2.

## Runs conservés

| Agents | Résultat brut | Réussites | Makespan | Appels modèle simultanés max | Échantillons GPU | GPU-Util moyenne / max | VRAM min / moyenne / max | Puissance moyenne / pic |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 (run 1) | [campagne](../results/raw/cohort/20260924T130714.567359Z-cohort-a1-e40f4932/campaign.json), [échantillons](../results/raw/cohort/20260924T130714.567359Z-cohort-a1-e40f4932/remote-gpu-samples.jsonl) | 18/18 | 265,37 s | 1 | 265 | 92,71 % / 100 % | 88 663 / 89 831 / 90 679 MiB | 324,32 / 604,65 W |
| 1 (run 2) | [campagne](../results/raw/cohort/20260924T132457.125212Z-cohort-a1-7db136c5/campaign.json), [échantillons](../results/raw/cohort/20260924T132457.125212Z-cohort-a1-7db136c5/remote-gpu-samples.jsonl) | 18/18 | 251,55 s | 1 | 251 | 92,42 % / 100 % | 90 679 / 90 679 / 90 679 MiB | 309,79 / 356,85 W |
| 1 (run 3) | [campagne](../results/raw/cohort/20260924T133114.023226Z-cohort-a1-97d85b00/campaign.json), [échantillons](../results/raw/cohort/20260924T133114.023226Z-cohort-a1-97d85b00/remote-gpu-samples.jsonl) | 18/18 | 251,71 s | 1 | 251 | 93,84 % / 100 % | 90 679 / 90 679 / 90 679 MiB | 309,30 / 363,70 W |
| 4 (run 1) | [campagne](../results/raw/cohort/20260924T134300.540507Z-cohort-a4-9e1787fb/campaign.json), [échantillons](../results/raw/cohort/20260924T134300.540507Z-cohort-a4-9e1787fb/remote-gpu-samples.jsonl) | 18/18 | 111,79 s | 4 | 111 | 98,74 % / 100 % | 90 679 / 90 681 / 90 681 MiB | 336,89 / 433,59 W |
| 4 (run 2) | [campagne](../results/raw/cohort/20260924T134457.252673Z-cohort-a4-11edb359/campaign.json), [échantillons](../results/raw/cohort/20260924T134457.252673Z-cohort-a4-11edb359/remote-gpu-samples.jsonl) | 17/18 | 68,59 s | 4 | 68 | 98,22 % / 100 % | 90 681 / 90 681 / 90 681 MiB | 344,37 / 422,58 W |
| 4 (run 3) | [campagne](../results/raw/cohort/20260924T134836.893508Z-cohort-a4-c1252464/campaign.json), [échantillons](../results/raw/cohort/20260924T134836.893508Z-cohort-a4-c1252464/remote-gpu-samples.jsonl) | 18/18 | 111,84 s | 4 | 111 | 98,68 % / 100 % | 90 681 / 90 681 / 90 681 MiB | 337,33 / 429,32 W |
| 5 (run 1) | [campagne](../results/raw/cohort/20260924T135038.017472Z-cohort-a5-ef8b38bd/campaign.json), [échantillons](../results/raw/cohort/20260924T135038.017472Z-cohort-a5-ef8b38bd/remote-gpu-samples.jsonl) | 17/18 | 110,03 s | 5 | 110 | 98,15 % / 100 % | 90 681 / 90 681 / 90 681 MiB | 341,56 / 444,58 W |
| 5 (run 2) | [campagne](../results/raw/cohort/20260924T135413.893293Z-cohort-a5-177377ee/campaign.json), [échantillons](../results/raw/cohort/20260924T135413.893293Z-cohort-a5-177377ee/remote-gpu-samples.jsonl) | 17/18 | 49,96 s | 5 | 50 | 98,00 % / 100 % | 90 681 / 90 681 / 90 681 MiB | 373,49 / 456,87 W |
| 5 (run 3) | [campagne](../results/raw/cohort/20260924T135517.672477Z-cohort-a5-b7a64c5e/campaign.json), [échantillons](../results/raw/cohort/20260924T135517.672477Z-cohort-a5-b7a64c5e/remote-gpu-samples.jsonl) | 18/18 | 109,75 s | 5 | 109 | 98,04 % / 100 % | 90 681 / 90 681 / 90 681 MiB | 346,91 / 433,69 W |
| 6 (run 1) | [campagne](../results/raw/cohort/20260924T135738.528155Z-cohort-a6-bd6aa237/campaign.json), [échantillons](../results/raw/cohort/20260924T135738.528155Z-cohort-a6-bd6aa237/remote-gpu-samples.jsonl) | 17/18 | 94,31 s | 6 | 94 | 97,67 % / 100 % | 90 681 / 90 681 / 90 681 MiB | 356,37 / 498,52 W |
| 6 (run 2) | [campagne](../results/raw/cohort/20260924T135930.158766Z-cohort-a6-9a802254/campaign.json), [échantillons](../results/raw/cohort/20260924T135930.158766Z-cohort-a6-9a802254/remote-gpu-samples.jsonl) | 17/18 | 109,87 s | 6 | 109 | 98,73 % / 100 % | 90 681 / 90 681 / 90 681 MiB | 348,74 / 471,80 W |
| 6 (run 3) | [campagne](../results/raw/cohort/20260924T141057.006320Z-cohort-a6-c8b48419/campaign.json), [échantillons](../results/raw/cohort/20260924T141057.006320Z-cohort-a6-c8b48419/remote-gpu-samples.jsonl) | 18/18 | 86,98 s | 6 | 87 | 96,66 % / 100 % | 90 683 / 90 683 / 90 683 MiB | 350,40 / 440,96 W |
| 8 (run 1) | [campagne](../results/raw/cohort/20260924T140923.647637Z-cohort-a8-f4c8b99a/campaign.json), [échantillons](../results/raw/cohort/20260924T140923.647637Z-cohort-a8-f4c8b99a/remote-gpu-samples.jsonl) | 18/18 | 67,19 s | 8 | 67 | 98,18 % / 100 % | 90 681 / 90 683 / 90 683 MiB | 367,35 / 491,10 W |
| 8 (run 2) | [campagne](../results/raw/cohort/20260924T141324.718384Z-cohort-a8-454f9908/campaign.json), [échantillons](../results/raw/cohort/20260924T141324.718384Z-cohort-a8-454f9908/remote-gpu-samples.jsonl) | 18/18 | 104,81 s | 8 | 104 | 98,80 % / 100 % | 90 683 / 90 683 / 90 683 MiB | 352,38 / 512,89 W |
| 8 (run 3) | [campagne](../results/raw/cohort/20260924T141556.492737Z-cohort-a8-8177d975/campaign.json), [échantillons](../results/raw/cohort/20260924T141556.492737Z-cohort-a8-8177d975/remote-gpu-samples.jsonl) | 17/18 | 64,24 s | 8 | 64 | 98,19 % / 100 % | 90 683 / 90 683 / 90 683 MiB | 361,64 / 501,26 W |
| 10 (run 1) | [campagne](../results/raw/cohort/20260924T142003.273671Z-cohort-a10-5b69be3a/campaign.json), [échantillons](../results/raw/cohort/20260924T142003.273671Z-cohort-a10-5b69be3a/remote-gpu-samples.jsonl) | 17/18 | 47,67 s | 10 | 47 | 95,43 % / 100 % | 90 683 / 91 149 / 91 159 MiB | 383,71 / 558,02 W |
| 10 (run 2) | [campagne](../results/raw/cohort/20260924T151642.961050Z-cohort-a10-60b0faea/campaign.json), [échantillons](../results/raw/cohort/20260924T151642.961050Z-cohort-a10-60b0faea/remote-gpu-samples.jsonl) | 17/18 | 37,15 s | 10 | 37 | 97,16 % / 100 % | 91 159 / 91 159 / 91 159 MiB | 392,50 / 570,56 W |
| 10 (run 3) | [campagne](../results/raw/cohort/20260924T151925.274085Z-cohort-a10-e8614a1a/campaign.json), [échantillons](../results/raw/cohort/20260924T151925.274085Z-cohort-a10-e8614a1a/remote-gpu-samples.jsonl) | 17/18 | 83,31 s | 10 | 83 | 98,47 % / 100 % | 91 159 / 91 159 / 91 159 MiB | 361,20 / 547,27 W |

Les trois runs à 1 agent sont terminés sans tâche en échec. À 4 agents, les runs
1 et 3 ont réussi 18/18 tâches ; le run 2 en a réussi 17/18, avec un échec sur
`DOC-03`. À 5 agents, le premier run a aussi réussi 17/18 tâches, avec un échec
sur `DOC-03` ; le deuxième run a le même résultat et échoue également sur
`DOC-03`, tandis que le troisième a réussi 18/18. À 6 agents, les runs 1 et 2
ont réussi 17/18 tâches et échoué sur `DOC-03` ; le run 3 a réussi 18/18. Aucun
runner error n'est rapporté sur les dix-huit runs. Les températures maximales
échantillonnées sont de 65 °C, 51 °C et 55 °C aux runs à 1 agent, puis de 58 °C,
60 °C et 48 °C aux runs à 4 agents, puis 55 °C, 50 °C et 56 °C aux runs à 5 agents,
et 56 °C et 52 °C aux deux premiers runs à 6 agents, puis 58 °C au troisième.
Les runs à 8 agents ont culminé à 56 °C, 54 °C et 54 °C ; le run 3 a échoué sur
`DOC-03`. Les trois runs à 10 agents ont réussi 17/18 tâches chacun et échoué
sur `DOC-03`, avec des températures maximales de 52 °C, 52 °C et 54 °C.
Le pic de puissance du premier run à 1 agent est de 604,65 W pour une limite
rapportée de 600 W ; c'est le maximum d'un échantillon, pas une mesure de
puissance soutenue. Les pics des autres runs sont de 356,85 W, 363,70 W,
433,59 W, 422,58 W, 429,32 W, 444,58 W, 456,87 W, 433,69 W, 498,52 W,
471,80 W, 491,10 W, 440,96 W, 512,89 W, 501,26 W, 558,02 W, 570,56 W et
547,27 W.

La télémétrie SSH des dix-huit runs indique le même RTX PRO 6000 Blackwell Server
Edition que la série sans DFlash2, avec le même UUID et le pilote distant
595.71.05. Comme dans les autres artefacts du 24 septembre,
`environment.hardware_declared` indique toutefois le pilote 610.43.02 et CUDA
13.3 ; l'écart du pilote déclaré reste à résoudre.

Les 18 campagnes représentent trois répétitions à chacun des six niveaux
d'agents. Elles ont toutes une télémétrie GPU disponible, totalisent 315/324
tâches réussies et ne rapportent aucun runner error ; les neuf échecs sont des
échecs de validation `DOC-03`.

## Comparaison exploratoire

La médiane des trois runs DFlash2 à 1 agent est de 251,71 s, environ 2,92 fois
plus rapide que la médiane des trois runs sans DFlash2 à 1 agent (735,36 s). Les
six runs ont réussi 18/18 tâches. À 4 agents, les trois runs DFlash2 ont une
médiane de 111,79 s (68,59–111,84 s) et cumulent 53/54 tâches réussies. La
médiane sans DFlash2 est de 302,30 s (52/54 tâches réussies sur trois runs),
soit un écart descriptif d'environ 2,70 fois.

À 5 agents, les trois runs DFlash2 ont une médiane de 109,75 s
(49,96–110,03 s) et cumulent 52/54 tâches réussies. La médiane sans DFlash2 est
de 146,49 s (54/54 tâches réussies), soit un écart descriptif d'environ
1,33 fois.

À 6 agents, les trois runs DFlash2 ont une médiane de 94,31 s
(86,98–109,87 s) et cumulent 52/54 tâches réussies. La médiane sans DFlash2 est
de 182,38 s (52/54 tâches réussies), soit un écart descriptif d'environ
1,93 fois.

À 8 agents, les trois runs DFlash2 ont une médiane de 67,19 s
(64,24–104,81 s) et cumulent 53/54 tâches réussies. La médiane sans DFlash2 est
de 188,26 s (54/54 tâches réussies), soit un écart descriptif d'environ
2,80 fois.

À 10 agents, les trois runs DFlash2 ont une médiane de 47,67 s
(37,15–83,31 s) et cumulent 51/54 tâches réussies. La médiane sans DFlash2 est
de 189,95 s (54/54 tâches réussies), soit un écart descriptif d'environ
3,98 fois.

Ces observations ne permettent pas encore d'attribuer causalement les écarts à
DFlash2 : les hits de prefix cache n'ont pas été relevés et le warmup n'a pas
été normalisé entre les runs.

Les niveaux 1, 4, 5, 6, 8 et 10 comptent maintenant trois répétitions DFlash2
sur ce serveur. À 8 agents, les résultats sont 18/18, 18/18 et 17/18 tâches ;
le troisième run a échoué sur `DOC-03`. Les trois runs à 10 agents ont réussi
17/18 tâches et échoué sur `DOC-03`. La comparaison
restera exploratoire tant que l'état du cache et le warmup ne sont pas contrôlés
de façon cohérente dans les deux variantes. Les anciennes cohortes DFlash2 du
23 septembre restent des données historiques d'une autre session ; elles ne
remplacent pas les répétitions sur ce serveur.
