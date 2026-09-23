# Session cohorte agentique — 23 septembre 2026

## Objet et périmètre

Cette session mesure le temps nécessaire à un lot fini de 18 tâches de réparation, exécutées
par des agents en boucle fermée : chaque agent prend une nouvelle tâche après avoir terminé
la précédente, validations comprises. Elle ne représente pas une arrivée continue d'utilisateurs
et ne remplace pas la matrice serving à requêtes fixes.

Les 13 campagnes utilisent Qwen3.8-27B-FP8 avec le draft DFlash2, `reasoning_effort: medium`,
vLLM 0.29.0, KV cache FP8 et prefix caching activé, sur une RTX PRO 6000 Blackwell déclarée
avec un GPU de 96 Go. Chaque campagne réutilise les mêmes 18 IDs et les mêmes révisions de
tâches. L'empreinte de configuration benchmark est identique (`426420e7…`), mais le plan passe
de la version 0.1.0 à 0.1.1 lorsque les valeurs exploratoires 4/6/8 sont ajoutées ; les tâches
et le mode restent inchangés.

## Résultats par nombre d'agents

La médiane et les plages ci-dessous sont descriptives : plusieurs niveaux n'ont que deux
répétitions et les sorties/réparations générées varient d'un run à l'autre.

| Agents | Runs (makespan en secondes, liens bruts) | Médiane | Campagnes 18/18 | Tâches réussies |
|---:|---|---:|---:|---:|
| 1 | [259,82](../results/raw/cohort/20260923T143842.221698Z-cohort-a1-cb6ef25f/campaign.json) | 259,82 | 1/1 | 18/18 |
| 4 | [238,27](../results/raw/cohort/20260923T161710.972437Z-cohort-a4-365c5fe7/campaign.json), [418,81](../results/raw/cohort/20260923T162513.438634Z-cohort-a4-443a9111/campaign.json) | 328,54 | 1/2 | 35/36 |
| 5 | [102,80](../results/raw/cohort/20260923T145859.829746Z-cohort-a5-0aeee91d/campaign.json), [196,26](../results/raw/cohort/20260923T150814.992575Z-cohort-a5-9e565016/campaign.json), [252,08](../results/raw/cohort/20260923T151725.947037Z-cohort-a5-f8860e4f/campaign.json), [179,65](../results/raw/cohort/20260923T152616.549152Z-cohort-a5-8eded3e4/campaign.json) | 187,95 | 3/4 | 71/72 |
| 6 | [186,28](../results/raw/cohort/20260923T154714.795834Z-cohort-a6-1424692d/campaign.json), [198,67](../results/raw/cohort/20260923T160508.787300Z-cohort-a6-13d6aaaf/campaign.json) | 192,48 | 2/2 | 36/36 |
| 8 | [242,25](../results/raw/cohort/20260923T160134.269065Z-cohort-a8-b338f61d/campaign.json), [214,67](../results/raw/cohort/20260923T161000.686998Z-cohort-a8-11cf205e/campaign.json) | 228,46 | 1/2 | 35/36 |
| 10 | [245,25](../results/raw/cohort/20260923T153031.968794Z-cohort-a10-84b70377/campaign.json), [367,94](../results/raw/cohort/20260923T153851.405412Z-cohort-a10-94e6f9dc/campaign.json) | 306,60 | 2/2 | 36/36 |

Au total, **10 campagnes sur 13** ont réussi les 18 tâches, soit **231 validations réussies
sur 234 exécutions de tâches**. Les trois campagnes avec un échec ont échoué sur `DOC-03` à la
validation cachée ; les détails attendus par les tests cachés ne sont pas reproduits ici. Les
validations publiques de ces exécutions avaient réussi. Toutes les campagnes rapportent zéro
erreur runner, zéro rejet de capacité et zéro requête modèle échouée. Plusieurs tentatives
contiennent cependant des `ChangeProtocolError`, parfois récupérées lors d'une reprise.

## Lecture opérationnelle

- **4 agents n'ont pas amélioré le makespan** dans ces essais. Le run à 418,81 s a été dominé
  par `AXON-05` : trois appels et environ 15 651 tokens de sortie pour cette tâche.
- **5 et 6 agents sont les niveaux les plus prometteurs de cette cohorte.** Le niveau 6 est
  particulièrement régulier sur ses deux essais (186,28–198,67 s, 18/18 à chaque fois).
  Sa médiane de 192,48 s est proche de celle des runs à 5 agents. Le run à 5 agents en 102,80 s
  est un outlier rapide : il a suivi un run à 1 agent sur le même processus vLLM.
- **8 et 10 agents n'ont pas apporté de gain visible par rapport à 6** sur ces observations.
  Les médianes sont respectivement 228,46 s et 306,60 s. Le maximum configuré de requêtes
  simultanées a été atteint, mais pas maintenu ; la concurrence moyenne mesurée ne croît pas
  de façon monotone avec le nombre d'agents.
- Les durées sont fortement influencées par la longueur des sorties et les reprises. À 6 agents,
  `CTX-01` a duré environ 170 s dans les deux essais ; à 8 agents, `AXON-05` a été le plus long,
  jusqu'à 242 s. Ces tâches peuvent presque déterminer le makespan d'une cohorte finie.

**Conclusion provisoire :** la zone 5–6 agents semble plus favorable que 8–10 pour ce profil
de travail, et 6 agents est le meilleur point répété et entièrement réussi. Cela ne démontre
pas un optimum : les répétitions sont peu nombreuses, le premier run à 5 agents est atypique,
et les trajectoires de réparation diffèrent.

## Cache, charge serveur et reproductibilité

Le prefix caching était activé, mais les campagnes n'enregistrent pas de métrique de cache hit
(`cached_input_tokens` reste indisponible). Les mesures de GPU/charge serveur distante n'étaient
pas exposées non plus. La première campagne à 5 agents suivait le run à 1 agent sur le même
processus ; une autre campagne à 5 agents a été exécutée après redémarrage de vLLM. Les temps
ne montrent ensuite pas de relation stable entre redémarrage et makespan. On ne peut donc pas
attribuer les écarts au cache seul ni comparer ces runs comme une expérience cold/warm contrôlée.

Toutes les campagnes indiquent le même commit Git, mais `working_tree_dirty: true`. Les
artefacts bruts conservent les hashes de configuration et de plan ; le diff exact du code
exécuté n'est pas inclus dans ces manifestes. Les campagnes préfixées `cohort-a1/a5/a10` sont
en workload 0.1.0 ; les runs exploratoires `a4/a6/a8` utilisent le plan 0.1.1.

## Suites recommandées

1. Répéter les niveaux 5 et 6 dans des conditions comparables ; considérer 8 comme point de
   contrôle, sans conclure à partir d'une seule paire.
2. Mesurer en parallèle les métriques serveur vLLM, en particulier les hits de prefix cache,
   et noter explicitement chaque redémarrage ainsi que l'état de warmup.
3. Lancer une cohorte appariée avec le FP8 sans DFlash2 aux niveaux retenus afin d'isoler
   l'effet opérationnel du speculative decoding.
4. Examiner les échecs `DOC-03` et les erreurs de protocole avant d'interpréter la réussite
   qualité agrégée.

Les résultats bruts restent dans `results/raw/cohort/` et ne sont pas modifiés par ce rapport.
