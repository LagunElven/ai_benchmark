# Session GPU du 22 septembre 2026

## Objectif

Terminer la comparaison opérationnelle Qwen3.8 BF16/Q8 sur la RTX PRO 6000,
répliquer les tâches documentaires Q8 et mesurer le serving avec la matrice
complète. Les résultats ne constituent pas une comparaison contrôlée de la
seule quantification : le Q8 utilise un checkpoint tiers différent du BF16.

## Réplication qualité documentaire Q8

Les tâches ciblées étaient `DOC-02`, `DOC-03`, `DOC-05`, `DOC-06`, `DOC-07` et
`DOC-08`. Trois exécutions indépendantes ont été réalisées :

- `20260922T075636.823267Z-c-017-9f61ea07`
- `20260922T081235.618357Z-c-017-4ad7501e`
- `20260922T082116.668143Z-c-017-bc7530ee`

Chaque exécution a obtenu **1/6** après réparation. La faiblesse documentaire
Q8 observée dans la campagne complète n'est donc pas attribuée uniquement à
une variation aléatoire de génération. Les résultats individuels restent dans
`results/raw/`.

## Comparaison qualité retenue

| Profil | Résultat | Durée cumulée | Lecture |
|---|---:|---:|---|
| BF16 C-016, thinking medium | 64/74 (86,5 %) | 1 h 40 min 29 s | Baseline opérationnelle |
| Q8 C-017, thinking medium | 62/74 (83,8 %) | 1 h 00 min 04 s | 2 tâches de moins, environ 40 % plus rapide |

Les deux profils réussissent les mêmes tâches sur la majorité des catégories.
L'écart principal est documentaire : **7/10 en BF16 contre 4/10 en Q8**.
Q8 réussit `SPRING-04` là où BF16 échoue ; BF16 réussit notamment `DOC-02`,
`DOC-03` et `DOC-07` là où Q8 échoue.

Artefacts principaux :

- BF16 : `results/raw/campaigns/20260921T110238.257698Z-c-016-81173711/campaign.json`
- Q8 : `results/raw/campaigns/20260921T155315.525802Z-c-017-35d4e399/campaign.json`
- rapport local : `results/reports/qwen3.8-bf16-vs-q8-rtx-pro-6000-20260922.md`

## Serving

### Couverture

- BF16 shared-prefix : 20 cas, concurrences 1/2/5/10, contextes 8k/32k/64k/100k/200k.
- BF16 cold : 6 cas communs seulement, concurrence 1/5 et contextes 8k/32k/64k.
- Q8 : 40 cas, les deux modes, toutes les concurrences et tous les contextes,
  soit 540 requêtes, sans échec.

La campagne Q8 est disponible ici :
`results/raw/serving/q8-rtx-pro-6000/20260922T103519.752487Z-serving-c66ffad8/campaign.json`.

Les cellules `cold` BF16 non exécutées sont explicitement **non testées**. Elles
ne doivent pas être extrapolées depuis les autres cellules. Les futurs tests de
serving standard utiliseront `shared-prefix` comme mode principal ; `cold` sera
conservé comme mesure diagnostique ponctuelle lorsque son coût est acceptable.

Sur les six cellules `cold` communes, BF16 est plus rapide que Q8. En
`shared-prefix`, Q8 est plus rapide sur les 20 cellules communes, avec un
avantage qui augmente lorsque la concurrence augmente. Les valeurs détaillées
sont dans le rapport local indiqué ci-dessus.

### Métriques GPU distantes

Le runner et l'endpoint sont séparés par le tunnel. Les métriques de ressources
capturées automatiquement par le runner sont celles de la machine qui exécute
le runner ; pour ces campagnes, `nvidia-smi` voit donc le GPU local et non le
GPU distant. Les champs `server_metrics` et KV-cache distants n'ont pas été
exposés par l'endpoint. Ces valeurs ne sont pas utilisées pour conclure sur la
mémoire ou l'utilisation du GPU distant.

## Corrections du benchmark

Le résumé de campagne qualité conserve maintenant les types d'erreur provenant
des résultats individuels (`error_types`) et leur agrégation (`error_counts`).
Cela permet de distinguer les erreurs de protocole ou de client des échecs de
validation fonctionnelle. Le schéma, le runner et le test associé ont été mis à
jour ; l'import de type du benchmark serving a également été nettoyé.

## État en fin de session

- Guide synthétique des 74 tâches ajouté dans `docs/TASK_REFERENCE.md`.
- Matrice qualité et documentation serving mises à jour.
- Les résultats bruts ne sont pas écrasés ; les rapports et artefacts restent
  générés sous `results/`, conformément au `.gitignore` du projet.
- Vérification finale : 59 tests automatisés réussis et `python -m ruff check
  runner serving scripts tests` réussi.
