# Session cohorte agentique — 24 septembre 2026

## Objet

Série de mesures du profil Qwen3.8-27B-FP8 officiel, sans DFlash2, avec
`reasoning_effort: medium`, KV cache FP8 et prefix caching activé. Chaque run
couvre les mêmes 18 tâches du pilote avec vLLM 0.29.0. La télémétrie SSH est
disponible pour les 18 runs retenus, soit trois répétitions par niveau d'agents.
Le deuxième run initial à 5 agents n'a pas de télémétrie ; sa reprise est
incluse dans la série retenue. Les runs mesurés indiquent la même RTX PRO 6000
Blackwell Server Edition et le même GPU UUID
`GPU-6785a083-d5a0-769c-663d-f7058894e22e`.

## Runs conservés

| Agents | Résultat brut | Réussites | Makespan | Appels modèle simultanés max | Échantillons GPU | GPU-Util moyenne / max | VRAM utilisée min / moyenne / max | Puissance moyenne / pic |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 (run 1) | [campagne](../results/raw/cohort/20260924T101013.278116Z-cohort-a1-3eb01366/campaign.json), [échantillons](../results/raw/cohort/20260924T101013.278116Z-cohort-a1-3eb01366/remote-gpu-samples.jsonl) | 18/18 | 735,36 s | 1 | 734 | 98,14 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 317,1 / 350,06 W |
| 1 (run 2) | [campagne](../results/raw/cohort/20260924T120209.235121Z-cohort-a1-caaefcad/campaign.json), [échantillons](../results/raw/cohort/20260924T120209.235121Z-cohort-a1-caaefcad/remote-gpu-samples.jsonl) | 18/18 | 735,37 s | 1 | 734 | 97,57 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 318,27 / 349,80 W |
| 1 (run 3) | [campagne](../results/raw/cohort/20260924T121510.790650Z-cohort-a1-02285ea1/campaign.json), [échantillons](../results/raw/cohort/20260924T121510.790650Z-cohort-a1-02285ea1/remote-gpu-samples.jsonl) | 18/18 | 735,25 s | 1 | 734 | 97,51 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 318,54 / 350,44 W |
| 4 (run 1) | [campagne](../results/raw/cohort/20260924T113302.928936Z-cohort-a4-edc9a016/campaign.json), [échantillons](../results/raw/cohort/20260924T113302.928936Z-cohort-a4-edc9a016/remote-gpu-samples.jsonl) | 18/18 | 308,93 s | 4 | 308 | 99,67 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 316,40 / 365,19 W |
| 4 (run 2) | [campagne](../results/raw/cohort/20260924T114525.854242Z-cohort-a4-ac2d46c6/campaign.json), [échantillons](../results/raw/cohort/20260924T114525.854242Z-cohort-a4-ac2d46c6/remote-gpu-samples.jsonl) | 17/18 | 236,82 s | 4 | 236 | 99,49 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 315,58 / 361,59 W |
| 4 (run 3) | [campagne](../results/raw/cohort/20260924T115302.111089Z-cohort-a4-eb0f4894/campaign.json), [échantillons](../results/raw/cohort/20260924T115302.111089Z-cohort-a4-eb0f4894/remote-gpu-samples.jsonl) | 17/18 | 302,30 s | 4 | 302 | 99,67 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 318,20 / 353,08 W |
| 5 (run 1) | [campagne](../results/raw/cohort/20260924T102826.900415Z-cohort-a5-fb8c8b15/campaign.json), [échantillons](../results/raw/cohort/20260924T102826.900415Z-cohort-a5-fb8c8b15/remote-gpu-samples.jsonl) | 18/18 | 146,49 s | 5 | 146 | 99,30 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 322 / 361,63 W |
| 5 (run 2 initial, télémétrie absente) | [campagne](../results/raw/cohort/20260924T104005.933032Z-cohort-a5-7973e54e/campaign.json) | 17/18 | 135,89 s | 5 | 0 | — | — | — |
| 5 (run 3) | [campagne](../results/raw/cohort/20260924T105011.820397Z-cohort-a5-4cde059b/campaign.json), [échantillons](../results/raw/cohort/20260924T105011.820397Z-cohort-a5-4cde059b/remote-gpu-samples.jsonl) | 18/18 | 216,19 s | 5 | 216 | 99,07 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 318,72 / 370,94 W |
| 5 (reprise du run 2) | [campagne](../results/raw/cohort/20260924T122950.381623Z-cohort-a5-10436d1f/campaign.json), [échantillons](../results/raw/cohort/20260924T122950.381623Z-cohort-a5-10436d1f/remote-gpu-samples.jsonl) | 18/18 | 133,93 s | 5 | 133 | 99,23 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 322,78 / 364,45 W |
| 6 (run 1) | [campagne](../results/raw/cohort/20260924T105658.934496Z-cohort-a6-d5c4d762/campaign.json), [échantillons](../results/raw/cohort/20260924T105658.934496Z-cohort-a6-d5c4d762/remote-gpu-samples.jsonl) | 18/18 | 237,56 s | 6 | 237 | 99,31 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 321,56 / 368,77 W |
| 6 (run 2) | [campagne](../results/raw/cohort/20260924T110120.056471Z-cohort-a6-cf95cd33/campaign.json), [échantillons](../results/raw/cohort/20260924T110120.056471Z-cohort-a6-cf95cd33/remote-gpu-samples.jsonl) | 17/18 | 182,38 s | 6 | 182 | 99,44 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 320,03 / 374,66 W |
| 6 (run 3) | [campagne](../results/raw/cohort/20260924T110439.283386Z-cohort-a6-1d19bcf2/campaign.json), [échantillons](../results/raw/cohort/20260924T110439.283386Z-cohort-a6-1d19bcf2/remote-gpu-samples.jsonl) | 17/18 | 182,27 s | 6 | 182 | 99,43 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 319,78 / 380,14 W |
| 8 (run 1) | [campagne](../results/raw/cohort/20260924T110824.703013Z-cohort-a8-0be22368/campaign.json), [échantillons](../results/raw/cohort/20260924T110824.703013Z-cohort-a8-0be22368/remote-gpu-samples.jsonl) | 18/18 | 188,26 s | 8 | 188 | 97,84 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 317,19 / 356,76 W |
| 8 (run 2) | [campagne](../results/raw/cohort/20260924T111232.184788Z-cohort-a8-394d29df/campaign.json), [échantillons](../results/raw/cohort/20260924T111232.184788Z-cohort-a8-394d29df/remote-gpu-samples.jsonl) | 18/18 | 252,66 s | 8 | 252 | 99,19 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 316,62 / 371,50 W |
| 8 (run 3) | [campagne](../results/raw/cohort/20260924T111706.474038Z-cohort-a8-ab156de8/campaign.json), [échantillons](../results/raw/cohort/20260924T111706.474038Z-cohort-a8-ab156de8/remote-gpu-samples.jsonl) | 18/18 | 149,56 s | 8 | 149 | 99,31 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 318,36 / 379,01 W |
| 10 (run 1) | [campagne](../results/raw/cohort/20260924T112005.401950Z-cohort-a10-674ab622/campaign.json), [échantillons](../results/raw/cohort/20260924T112005.401950Z-cohort-a10-674ab622/remote-gpu-samples.jsonl) | 18/18 | 198,09 s | 10 | 198 | 99,49 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 320,68 / 416,61 W |
| 10 (run 2) | [campagne](../results/raw/cohort/20260924T112443.669085Z-cohort-a10-7ed414db/campaign.json), [échantillons](../results/raw/cohort/20260924T112443.669085Z-cohort-a10-7ed414db/remote-gpu-samples.jsonl) | 18/18 | 189,95 s | 10 | 189 | 99,45 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 317,54 / 445,97 W |
| 10 (run 3) | [campagne](../results/raw/cohort/20260924T112845.608945Z-cohort-a10-07a3b7df/campaign.json), [échantillons](../results/raw/cohort/20260924T112845.608945Z-cohort-a10-07a3b7df/remote-gpu-samples.jsonl) | 18/18 | 184,11 s | 10 | 184 | 98,81 % / 100 % | 91 499 / 91 499 / 91 499 MiB | 318,97 / 417,50 W |

Le run à 5 agents numéro 2 initial, les runs à 4 agents numéros 2 et 3 et les
runs à 6 agents numéros 2 et 3 ont échoué à la validation de `DOC-03`. Les
températures maximales étaient de 49, 53 et 52 °C aux runs à 1 agent ; de 50,
59 et 59 °C aux runs à 4 agents ; de 58, 50 et 49 °C aux runs mesurés à 5
agents ; de 56, 55 et 57 °C aux runs à 6 agents ; de 52, 50 et 57 °C aux runs à
8 agents ; et de 52 °C aux trois runs à 10 agents. Ces dix-huit campagnes
mesurées indiquent le même GPU UUID et le même pilote distant 595.71.05. Le
sampler SSH du deuxième run initial à 5 agents s'est terminé avec le statut 255 ;
aucun échantillon n'a été enregistré. Dans tous les artefacts,
`environment.hardware_declared` indique le pilote 610.43.02 et CUDA 13.3,
alors que la télémétrie distante des dix-huit runs retenus rapporte le pilote
595.71.05. Le GPU UUID est confirmé par SSH ; le pilote déclaré diffère
systématiquement et CUDA 13.3 n'est pas confirmé par l'échantillonneur.

## Synthèse par niveau de concurrence

Les statistiques ci-dessous portent sur les trois runs télémétrés de chaque
niveau. Le nombre de tâches réussies est cumulé sur les 54 exécutions ; le
GPU-Util est la moyenne simple des moyennes des trois runs. Les plages de temps
et les mesures GPU restent descriptives.

| Agents | Tâches réussies | Makespan médian (min–max) | GPU-Util moyenne | VRAM observée | Puissance de pointe max. |
|---:|---:|---:|---:|---:|---:|
| 1 | 54/54 | 735,36 s (735,25–735,37) | 97,74 % | 91 499 MiB | 350,44 W |
| 4 | 52/54 | 302,30 s (236,82–308,93) | 99,61 % | 91 499 MiB | 365,19 W |
| 5 | 54/54 | 146,49 s (133,93–216,19) | 99,20 % | 91 499 MiB | 370,94 W |
| 6 | 52/54 | 182,38 s (182,27–237,56) | 99,39 % | 91 499 MiB | 380,14 W |
| 8 | 54/54 | 188,26 s (149,56–252,66) | 98,78 % | 91 499 MiB | 379,01 W |
| 10 | 54/54 | 189,95 s (184,11–198,09) | 99,25 % | 91 499 MiB | 445,97 W |

La série retenue totalise 320/324 tâches réussies (98,77 %) ; les quatre échecs
sont des échecs de validation `DOC-03` aux niveaux 4 et 6 agents. La VRAM
rapportée est restée à 91 499 MiB sur chaque échantillon, y compris au repos
selon l'instantané nvidia-smi communiqué séparément. Le GPU-Util échantillonné
reste élevé à chaque niveau, mais ne mesure ni l'occupation effective des unités
de calcul ni le débit utile.

Le makespan médian à 5 agents est environ 5,02 fois inférieur à celui à 1 agent.
Cette comparaison est descriptive : elle n'isole pas causalement l'effet du
nombre d'agents. Le run initial à 5 agents (17/18, 135,89 s), sans télémétrie,
reste conservé dans le tableau des runs, mais ne fait pas partie de cette
synthèse. Le niveau de 5 agents présente le makespan médian le plus bas parmi
les niveaux mesurés, mais la dispersion de ses trois temps (133,93–216,19 s) et
l'absence de contrôle du prefix cache/warmup ne permettent pas d'en conclure
qu'il s'agit du réglage optimal.

Après le run à 5 agents, un instantané `nvidia-smi` communiqué alors qu'aucune
requête n'était en cours montrait toujours 91 499 MiB utilisés sur 97 887 MiB,
mais 0 % de GPU-Util, 95 W et 39 °C. Cela confirme que l'allocation mémoire
persistante de vLLM ne suit pas l'activité des requêtes. La série de campagne
montre l'activité du GPU pendant le run, mais GPU-Util mesure le temps où au
moins un kernel est actif ; elle ne mesure pas directement l'occupation des
unités de calcul ni le débit utile. Voir la
[définition NVIDIA](https://docs.nvidia.com/deploy/nvidia-smi/).

## Limites de comparaison

Le profil active le prefix caching et le run à 5 agents suit celui à 1 agent
sur le même serveur. Si vLLM n'a pas été redémarré entre les deux, la campagne
à 5 agents a pu réutiliser des préfixes calculés pendant le run précédent.
vLLM peut réutiliser le KV cache des requêtes antérieures ayant un préfixe
commun, ce qui évite de recalculer la partie partagée du prefill ; les runs ne
contrôlent pas les hits ni leur effet sur le temps total. Voir la
[documentation APC de vLLM 0.29](https://docs.vllm.ai/en/v0.29.0/features/automatic_prefix_caching/).

Les runs exploratoires antérieurs restent conservés séparément : ils n'ont ni
UUID GPU ni échantillons SSH permettant de vérifier l'instance. Leurs valeurs
`hardware_declared` ne suffisent pas à établir le pilote ou le GPU réellement
utilisés ; ne pas les agréger comme une série matériellement appariée.

Les trois runs retenus de chaque niveau ont été enregistrés sur la même instance
et le même GPU UUID, mais ils forment une série exploratoire, pas une comparaison
contrôlée. Le prefix caching était activé, tandis que les hits de cache et l'état
de warmup n'ont pas été mesurés ou normalisés ; les runs se sont enchaînés.
Sur le même GPU UUID, trois runs DFlash2 à chacun des niveaux 1/4/5/6/8/10 ont
été exécutés ; ils sont rapportés dans la [session DFlash2 du 24 septembre](COHORT_SESSION_2026-09-24-DFLASH2.md).
Une comparaison contrôlée devra rejouer les deux variantes sous un protocole commun et résoudre
l'écart entre pilote déclaré et pilote distant. Le run initial à 5 agents sans
télémétrie reste archivé à part des 18 runs retenus.
