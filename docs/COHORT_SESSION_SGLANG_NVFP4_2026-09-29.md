# Session qualité et cohortes SGLang NVFP4 — 29 septembre 2026

## Périmètre et état

C-022 utilise Qwen3.8-27B NVFP4, seed 42, `reasoning_effort: medium`, sans
décodage spéculatif. Le checkpoint NVFP4 est épinglé à
`dbb8f445b3145f8a4c18ddc769f032d57d32867c`, le tokenizer à
`1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`. Les 18 cohortes emploient le même
profil et le même plan de 18 tâches/révisions ; trois répétitions ont été faites
à chaque niveau de 1/4/5/6/8/10 agents.

Le serveur était SGLang `0.5.20-cuda-13.0`, tag
`vastai/sglang:v0.5.20-cuda-13.0`. L'ID/digest immuable de l'image n'a pas été
enregistré dans les manifestes : le tag seul ne permet pas d'identifier
complètement le build.

La smoke qualité a réussi 7/7 tâches :
[résultat brut](../results/raw/campaigns/20260929T140251.023928Z-c-022-9b1275f5/campaign.json).
La suite qualité complète a réussi 64/74 tâches (8 échecs fonctionnels, 1 de
protocole et 1 rejet de capacité), sans erreur d'infrastructure ou du runner :
[résultat brut](../results/raw/campaigns/20260929T143712.429719Z-c-022-fd6d21a7/campaign.json).
`CTX-06` a demandé 273 488 tokens, au-delà des 262 144 configurés. La campagne
qualité a été reprise après le redémarrage du poste runner ; les durées cumulées
des tâches sont d'environ 32 min 03 s, alors que le temps mural inclut
l'interruption.

## Résultats du pilote de cohorte

Les cellules SGLang et vLLM portent les mêmes tâches, révisions, checkpoint et
seed, mais constituent une comparaison **opérationnelle**, pas un test contrôlé.
Les écarts de médiane ci-dessous décrivent ces séries et ne démontrent pas un
effet causal du moteur.

| Agents | SGLang run 1 | SGLang run 2 | SGLang run 3 | SGLang médiane (min–max) | Réussites SGLang | vLLM médiane / réussites | SGLang vs vLLM |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | [506,00 s — 18/18](../results/raw/cohort/20260929T151847.505335Z-cohort-a1-767415cb/campaign.json) | [391,56 s — 18/18](../results/raw/cohort/20260929T161733.031403Z-cohort-a1-8cfd0034/campaign.json) | [379,50 s — 18/18](../results/raw/cohort/20260929T162732.806120Z-cohort-a1-bb047449/campaign.json) | 391,56 s (379,50–506,00) | 54/54 | 446,57 s / 54/54 | −12,3 % |
| 4 | [119,16 s — 18/18](../results/raw/cohort/20260929T152736.226396Z-cohort-a4-27324fe2/campaign.json) | [201,69 s — 17/18](../results/raw/cohort/20260929T160957.803466Z-cohort-a4-963112bd/campaign.json) | [139,38 s — 17/18](../results/raw/cohort/20260929T161422.370311Z-cohort-a4-27e3e246/campaign.json) | 139,38 s (119,16–201,69) | 52/54 | 168,55 s / 53/54 | −17,3 % |
| 5 | [196,68 s — 17/18](../results/raw/cohort/20260929T153034.009491Z-cohort-a5-ba0b8c9c/campaign.json) | [139,10 s — 18/18](../results/raw/cohort/20260929T160250.615122Z-cohort-a5-78bd07ab/campaign.json) | [120,27 s — 18/18](../results/raw/cohort/20260929T160716.799407Z-cohort-a5-b36438e7/campaign.json) | 139,10 s (120,27–196,68) | 53/54 | 158,55 s / 51/54 | −12,3 % |
| 6 | [131,69 s — 17/18](../results/raw/cohort/20260929T153401.638629Z-cohort-a6-3c8b628b/campaign.json) | [97,49 s — 18/18](../results/raw/cohort/20260929T155737.767828Z-cohort-a6-da7148cb/campaign.json) | [101,74 s — 18/18](../results/raw/cohort/20260929T160043.571829Z-cohort-a6-fe0b08e0/campaign.json) | 101,74 s (97,49–131,69) | 53/54 | 156,64 s / 52/54 | −35,1 % |
| 8 | [161,86 s — 17/18](../results/raw/cohort/20260929T153621.380008Z-cohort-a8-3457b271/campaign.json) | [85,03 s — 18/18](../results/raw/cohort/20260929T155311.140283Z-cohort-a8-0c5c8b10/campaign.json) | [88,75 s — 17/18](../results/raw/cohort/20260929T155533.943016Z-cohort-a8-4f9004ab/campaign.json) | 88,75 s (85,03–161,86) | 52/54 | 149,13 s / 52/54 | −40,5 % |
| 10 | [175,43 s — 18/18](../results/raw/cohort/20260929T154030.312114Z-cohort-a10-2a38c1c2/campaign.json) | [116,25 s — 17/18](../results/raw/cohort/20260929T154417.210389Z-cohort-a10-fa057023/campaign.json) | [79,70 s — 18/18](../results/raw/cohort/20260929T155111.241324Z-cohort-a10-bdcfb78b/campaign.json) | 116,25 s (79,70–175,43) | 53/54 | 260,79 s / 51/54 | −55,4 % |

Au total, SGLang compte **317/324 tâches réussies** ; les sept échecs sont tous
`DOC-03`. La série vLLM documentée compte 313/324 réussites. Toutes les cohortes
SGLang ont atteint leur concurrence configurée et disposent de mesures GPU
distantes ; aucune n'a d'erreur runner ou d'échec de requête modèle. Des
`ChangeProtocolError` ponctuelles ont été récupérées dans certaines tâches.
Les 339 appels modèle ont consommé 1 875 120 tokens d'entrée et produit
507 498 tokens de sortie ; les volumes varient entre répétitions.

## Matériel et limites de comparaison

Les 18 runs SGLang ont utilisé une RTX PRO 6000 Blackwell Server Edition,
UUID `GPU-0097bc0d-1427-c260-0ae1-60087fd2b3db`, pilote 610.43.02. L'utilisation
moyenne observée varie de 94,36 à 99,94 %, la mémoire maximale échantillonnée
est 87 031 MiB et la température maximale 58 °C. Les manifestes rapportent une
limite de puissance de 400 W ; les pics échantillonnés atteignent 425,41 W. Ces
pics ne sont pas une mesure de puissance soutenue ni, à eux seuls, une preuve de
throttling.

Les cohortes vLLM à 1–8 agents ont utilisé une Workstation Edition (UUID
`GPU-6d74fd11-1390-0f03-f603-058c602acf83`, pilote 595.71.05) ; celles à 10
agents une autre Server Edition (UUID `GPU-b368df4b-6e60-6e55-21ca-6547d4c3f036`,
pilote 595.71.05). Les limites de puissance enregistrées étaient de 400 W pour
les runs Workstation et de 600 W pour les runs vLLM Server à 10 agents, dont les
pics de consommation sont restés entre 253 et 401 W avec 27–41 % d'utilisation
GPU moyenne. Les noms d'édition et les TDP nominaux ne suffisent donc pas à
attribuer les écarts de performance à une limite de puissance.

Les autres différences de moteur incluent les versions SGLang 0.5.20 et vLLM
0.29, `max_running_requests=10` contre `max_num_seqs=16`, et le type KV cache
`fp8_e4m3` contre `fp8`. Le profil/cache vLLM historique comporte aussi une
incertitude sur l'activation effective du prefix caching ; les hits ne sont pas
mesurés dans ces cohortes. Les résultats et écarts de médiane restent donc
exploratoires et ne doivent pas être interprétés comme un benchmark A/B contrôlé.
