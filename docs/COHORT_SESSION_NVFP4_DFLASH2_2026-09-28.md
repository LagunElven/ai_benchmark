# Session cohorte agentique NVFP4 + DFlash2 — 28 septembre 2026

## Périmètre

Le pilote fini porte sur les mêmes 18 tâches et révisions à chaque run, avec le
profil `benchmark.qwen3.8-nvfp4-dflash2-medium-thinking.yaml`, seed 42,
`reasoning_effort: medium`, Qwen3.8-27B NVFP4 et le draft DFlash2 BF16 épinglés.
vLLM 0.29.0 utilise un KV cache FP8, `max-model-len=262144`,
`max-num-seqs=16` et sept tokens spéculatifs. Trois répétitions ont été faites
à chacun des niveaux 1, 4, 5, 6, 8 et 10 agents.

Les 18 runs ont échantillonné le GPU distant par SSH. Ils identifient tous une
RTX PRO 6000 Blackwell Server Edition, UUID
`GPU-b368df4b-6e60-6e55-21ca-6547d4c3f036`, pilote 595.71.05. Les données
matérielles CPU ne sont pas déclarées dans ces campagnes. Le cache de préfixe
est activé dans la configuration/commande DFlash2, mais les métriques de hits
ne sont pas enregistrées par le pilote de cohorte.

## Synthèse par concurrence

| Agents | Makespans des runs | Médiane (min–max) | Réussites | GPU-Util moyenne des trois runs | Tâche en échec |
|---:|---|---:|---:|---:|---|
| 1 | 209,77 / 193,73 / 195,22 s | 195,22 s (193,73–209,77) | 51/54 | 75,6 % | DOC-03 dans les trois runs |
| 4 | 261,02 / 174,44 / 289,35 s | 261,02 s (174,44–289,35) | 52/54 | 26,1 % | DOC-03 aux runs 2 et 3 |
| 5 | 211,87 / 235,12 / 185,41 s | 211,87 s (185,41–235,12) | 53/54 | 31,6 % | DOC-03 au run 2 |
| 6 | 141,38 / 230,03 / 199,57 s | 199,57 s (141,38–230,03) | 52/54 | 27,4 % | DOC-03 aux runs 2 et 3 |
| 8 | 193,55 / 159,52 / 98,98 s | 159,52 s (98,98–193,55) | 52/54 | 34,0 % | DOC-03 aux runs 1 et 2 |
| 10 | 82,21 / 81,81 / 107,57 s | 82,21 s (81,81–107,57) | 51/54 | 32,5 % | DOC-03 dans les trois runs |

Au total, 311/324 tâches ont réussi. Les 13 échecs concernent tous DOC-03 ;
aucune requête modèle ni tâche du runner n'a été signalée en erreur. La
concurrence maximale configurée a été atteinte dans chacun des 18 runs. Les
durées varient aussi avec le nombre d'appels de réparation et les tokens
générés : les temps muraux ne mesurent donc pas une charge identique au token
près.

## Runs conservés

Chaque campagne référence le fichier `remote-gpu-samples.jsonl` correspondant.
Les tokens sont indiqués entrée / sortie / raisonnement.

| Agents | Run | Campagne / télémétrie distante | Tâches | Makespan | Appels | Tokens entrée / sortie / raisonnement | GPU-Util moyenne / pic |
|---:|---:|---|---:|---:|---:|---:|---:|
| 1 | 1 | [campagne](../results/raw/cohort/20260928T144427.054399Z-cohort-a1-588f0207/campaign.json) / [GPU](../results/raw/cohort/20260928T144427.054399Z-cohort-a1-588f0207/remote-gpu-samples.jsonl) | 17/18 | 209,77 s | 18 | 103 061 / 27 554 / 22 327 | 77,2 % / 100 % |
| 1 | 2 | [campagne](../results/raw/cohort/20260928T144824.537381Z-cohort-a1-c6ba4c6a/campaign.json) / [GPU](../results/raw/cohort/20260928T144824.537381Z-cohort-a1-c6ba4c6a/remote-gpu-samples.jsonl) | 17/18 | 193,73 s | 18 | 103 061 / 27 554 / 22 327 | 75,6 % / 100 % |
| 1 | 3 | [campagne](../results/raw/cohort/20260928T145402.885776Z-cohort-a1-96f7dce8/campaign.json) / [GPU](../results/raw/cohort/20260928T145402.885776Z-cohort-a1-96f7dce8/remote-gpu-samples.jsonl) | 17/18 | 195,22 s | 18 | 103 061 / 27 554 / 22 327 | 74,0 % / 90 % |
| 4 | 1 | [campagne](../results/raw/cohort/20260928T145909.619475Z-cohort-a4-de9a2c24/campaign.json) / [GPU](../results/raw/cohort/20260928T145909.619475Z-cohort-a4-de9a2c24/remote-gpu-samples.jsonl) | 18/18 | 261,02 s | 19 | 110 112 / 32 877 / 27 488 | 24,5 % / 99 % |
| 4 | 2 | [campagne](../results/raw/cohort/20260928T151037.169214Z-cohort-a4-318c29e5/campaign.json) / [GPU](../results/raw/cohort/20260928T151037.169214Z-cohort-a4-318c29e5/remote-gpu-samples.jsonl) | 17/18 | 174,44 s | 18 | 103 061 / 24 607 / 19 291 | 23,3 % / 89 % |
| 4 | 3 | [campagne](../results/raw/cohort/20260928T151534.652183Z-cohort-a4-76f67681/campaign.json) / [GPU](../results/raw/cohort/20260928T151534.652183Z-cohort-a4-76f67681/remote-gpu-samples.jsonl) | 17/18 | 289,35 s | 21 | 106 307 / 37 163 / 30 718 | 30,5 % / 90 % |
| 5 | 1 | [campagne](../results/raw/cohort/20260928T152050.042737Z-cohort-a5-ef39eb1e/campaign.json) / [GPU](../results/raw/cohort/20260928T152050.042737Z-cohort-a5-ef39eb1e/remote-gpu-samples.jsonl) | 18/18 | 211,87 s | 19 | 110 112 / 32 374 / 26 791 | 32,0 % / 100 % |
| 5 | 2 | [campagne](../results/raw/cohort/20260928T152600.375055Z-cohort-a5-22b83c69/campaign.json) / [GPU](../results/raw/cohort/20260928T152600.375055Z-cohort-a5-22b83c69/remote-gpu-samples.jsonl) | 17/18 | 235,12 s | 20 | 104 941 / 33 888 / 27 935 | 36,2 % / 100 % |
| 5 | 3 | [campagne](../results/raw/cohort/20260928T153121.944192Z-cohort-a5-32bdbe09/campaign.json) / [GPU](../results/raw/cohort/20260928T153121.944192Z-cohort-a5-32bdbe09/remote-gpu-samples.jsonl) | 18/18 | 185,41 s | 18 | 103 061 / 29 530 / 24 166 | 26,5 % / 100 % |
| 6 | 1 | [campagne](../results/raw/cohort/20260928T154102.023618Z-cohort-a6-621e3023/campaign.json) / [GPU](../results/raw/cohort/20260928T154102.023618Z-cohort-a6-621e3023/remote-gpu-samples.jsonl) | 18/18 | 141,38 s | 19 | 104 079 / 28 037 / 22 254 | 26,7 % / 100 % |
| 6 | 2 | [campagne](../results/raw/cohort/20260928T154451.318765Z-cohort-a6-83635972/campaign.json) / [GPU](../results/raw/cohort/20260928T154451.318765Z-cohort-a6-83635972/remote-gpu-samples.jsonl) | 17/18 | 230,03 s | 20 | 111 037 / 35 502 / 29 588 | 26,3 % / 100 % |
| 6 | 3 | [campagne](../results/raw/cohort/20260928T154906.614448Z-cohort-a6-626c2075/campaign.json) / [GPU](../results/raw/cohort/20260928T154906.614448Z-cohort-a6-626c2075/remote-gpu-samples.jsonl) | 17/18 | 199,57 s | 20 | 187 365 / 35 549 / 29 753 | 29,3 % / 100 % |
| 8 | 1 | [campagne](../results/raw/cohort/20260928T155319.817850Z-cohort-a8-efd4c501/campaign.json) / [GPU](../results/raw/cohort/20260928T155319.817850Z-cohort-a8-efd4c501/remote-gpu-samples.jsonl) | 17/18 | 193,55 s | 20 | 104 941 / 37 924 / 31 539 | 40,9 % / 100 % |
| 8 | 2 | [campagne](../results/raw/cohort/20260928T155713.842349Z-cohort-a8-1d73fb20/campaign.json) / [GPU](../results/raw/cohort/20260928T155713.842349Z-cohort-a8-1d73fb20/remote-gpu-samples.jsonl) | 17/18 | 159,52 s | 20 | 104 789 / 34 222 / 27 546 | 35,1 % / 90 % |
| 8 | 3 | [campagne](../results/raw/cohort/20260928T160234.881433Z-cohort-a8-9c68ec7f/campaign.json) / [GPU](../results/raw/cohort/20260928T160234.881433Z-cohort-a8-9c68ec7f/remote-gpu-samples.jsonl) | 18/18 | 98,98 s | 18 | 103 061 / 24 454 / 19 185 | 26,1 % / 89 % |
| 10 | 1 | [campagne](../results/raw/cohort/20260928T160537.511528Z-cohort-a10-6268a4cb/campaign.json) / [GPU](../results/raw/cohort/20260928T160537.511528Z-cohort-a10-6268a4cb/remote-gpu-samples.jsonl) | 17/18 | 82,21 s | 18 | 103 061 / 25 229 / 19 738 | 31,9 % / 86 % |
| 10 | 2 | [campagne](../results/raw/cohort/20260928T160705.505880Z-cohort-a10-2d3e4702/campaign.json) / [GPU](../results/raw/cohort/20260928T160705.505880Z-cohort-a10-2d3e4702/remote-gpu-samples.jsonl) | 17/18 | 81,81 s | 18 | 103 061 / 25 122 / 19 883 | 33,1 % / 90 % |
| 10 | 3 | [campagne](../results/raw/cohort/20260928T160846.027703Z-cohort-a10-0d321c09/campaign.json) / [GPU](../results/raw/cohort/20260928T160846.027703Z-cohort-a10-0d321c09/remote-gpu-samples.jsonl) | 17/18 | 107,57 s | 19 | 104 940 / 28 088 / 22 226 | 32,4 % / 88 % |

## Lecture comparative

Les cohortes NVFP4 sans DFlash2 à 1–8 agents ont été exécutées sur une RTX PRO
6000 Blackwell Workstation Edition, UUID différent. Leurs durées ne sont pas
comparables directement aux niveaux 1–8 de cette session, tous réalisés sur la
Server Edition. Au niveau 10, les cohortes sans DFlash2 du 28 septembre et les
présentes cohortes identifient le même GPU Server Edition et le même UUID.
Leur makespan médian est de 260,79 s sans DFlash2 (389,63 / 260,79 / 260,78)
contre 82,21 s avec DFlash2 (82,21 / 81,81 / 107,57), soit 68,5 % de moins
dans cette série. Les deux séries réussissent 51/54 tâches et échouent chacune
sur DOC-03 dans les trois répétitions. Les runs DFlash2 à 10 agents ont généré
environ 25–28 k tokens, contre 23–34 k sans DFlash2.

Cette différence est un signal opérationnel fort, pas une attribution causale
parfaite au seul DFlash2 : les runs sont séquentiels, les sorties/réparations
varient et les hits du cache de préfixe ne sont pas capturés. Le manifeste des
cohortes NVFP4 sans DFlash2 déclare `prefix_caching: false`, alors que la
commande `VLLM_ARGS` du template Vast.ai fournie pour ce serveur comportait
`--enable-prefix-caching`. Le champ de configuration historique ne reflète donc
pas fidèlement l'option de lancement effective ; les hits réels restent
indisponibles. Les manifestes DFlash2 déclarent le cache activé. À 1–8 agents,
le changement Workstation/Server Edition est une limite supplémentaire.

Les résultats qualité restent séparés de cette mesure de débit : C-020 sans
DFlash2 a réussi 59/74 tâches, contre 57/74 pour C-021 NVFP4 + DFlash2. C-021
a 16 échecs fonctionnels, aucun échec de protocole et un rejet de capacité ;
C-020 a 12 échecs fonctionnels, deux échecs de protocole et un rejet de
capacité. C-020 utilise la Workstation Edition observée, tandis que la
télémétrie GPU distante n'a pas été demandée pour C-021. Une seule campagne
qualité par profil ne permet pas d'attribuer ces écarts à DFlash2.

Le serving NVFP4 + DFlash2 a réussi 1 800/1 800 requêtes dans 20 cas
`shared-prefix`. Les cas à 10 utilisateurs ont cependant un TTFT p95 de 67,75 s
à 64k tokens et de 205,16 s à 100k tokens. Les compteurs de hits KV-cache et la
télémétrie GPU distante ne sont pas disponibles dans cet artefact ; ces valeurs
ne permettent donc pas de conclure sur la cause des latences longues.

## Limites et suite

Le pilote mesure un lot fini en boucle fermée : lorsque les tâches se terminent,
les agents sont libérés. Il ne prédit pas seul le débit d'un flux continu
saturant. Les trois répétitions montrent une baisse du makespan médian de
5 à 8 puis 10 agents sur ce serveur, mais DOC-03 échoue dans plusieurs runs et
la longueur de sortie influe fortement sur le temps. Pour une comparaison plus
stricte, redémarrer le moteur ou vider son cache avant chaque répétition,
normaliser le warmup, enregistrer les arguments effectifs du serveur ainsi que
les compteurs cache, et apparier sans/avec DFlash2 sur le même matériel.
