# Analyse des échecs C-018/C-019 et des cohortes FP8 — 24 septembre 2026

## Périmètre et conclusion

Cette analyse recoupe les résultats bruts de C-018 (FP8 sans DFlash2), C-019 (FP8
avec DFlash2) et les 36 cohortes FP8 retenues du 24 septembre. Elle distingue les
échecs de validation fonctionnelle, les réponses incompatibles avec le protocole et
les refus de capacité.

Les traces ne montrent aucun échec d'infrastructure ou d'exécution pour C-018/C-019,
ni d'erreur runner pour les cohortes retenues. Deux sujets demandent un suivi séparé :
les limites de sortie conduisent parfois à l'absence de réponse finale exploitable,
et le contrat de DOC-03 ne précise pas les formats de date d'entrée que son validateur
attend.

## Campagnes qualité C-018 et C-019

| Campagne | Réussites | Taux qualité | Échecs fonctionnels | Échecs protocole | Refus de capacité | Infrastructure / exécution |
|---|---:|---:|---:|---:|---:|---:|
| C-018, FP8 sans DFlash2 | 58/73 | 79,45 % | 8 | 7 | 1 | 0 |
| C-019, FP8 avec DFlash2 | 62/73 | 84,93 % | 9 | 2 | 1 | 0 |

Le taux qualité exclut CTX-06, qui n'a pas pu être évaluée ; sur les 74 tâches
opérationnelles, les taux de réussite sont respectivement 58/74 (78,38 %) et
62/74 (83,78 %). Toutes les défaillances fonctionnelles ci-dessous ont passé les
tests publics et échoué aux validations cachées. Les journaux ne signalent donc pas
une panne du validateur public ou du runner, mais ils ne suffisent pas à établir si
chaque attente cachée était assez explicitement annoncée dans le contrat de sa tâche.

| C-018 : échec fonctionnel | C-019 : échec fonctionnel |
|---|---|
| DOC-01, DOC-04, DOC-08, E2E-01, JAVA-07, JAVA-08, WEB-04, WEB-10 | DOC-04, DOC-05, DOC-06, DOC-08, DOC-09, E2E-01, JAVA-07, WEB-04, WEB-10 |

### Erreurs de protocole

Chaque campagne a 15 tentatives de réparation où le parseur a rejeté la réponse
comme JSON incompatible, réparties sur 12 tâches. Les campagnes finales en classent
respectivement 7 (C-018) et 2 (C-019) comme échecs de protocole ; les autres erreurs
ont été récupérées ou suivies d'une autre validation. Une erreur de tentative n'est
donc pas à compter comme une tâche finale échouée.

| Campagne | Réponses terminées par la limite de sortie | Sans contenu final exploitable | Échecs protocole finaux |
|---|---:|---:|---:|
| C-018 | 6/15 | 4/15 | 7 |
| C-019 | 11/15 | 9/15 | 2 |

Toutes les autres tentatives avaient un contenu, mais celui-ci ne formait pas le JSON
attendu par le protocole de changements. Les réponses coupées portent
finish_reason=length ; leurs usages atteignent les plafonds effectifs de la tâche,
souvent 5 000 ou 6 000 tokens, et les tokens consommés sont presque entièrement du
raisonnement. La configuration globale permet 32 768 tokens, mais
override_task_max_output_tokens est désactivé : ce sont donc les plafonds par tâche
qui s'appliquent. Il s'agit d'une limite de génération/protocole, pas d'une erreur
de transport GPU.

### Refus de capacité CTX-06

CTX-06 est rejetée dans les deux campagnes avant génération. Le serveur annonce une
fenêtre de 262 144 tokens, alors que la requête demande au moins 256 145 tokens
d'entrée et 6 000 de sortie, soit au moins 262 145 tokens. Le dépassement est d'un
token. Selon la définition de [METRICS.md](METRICS.md), ce refus est exclu du taux qualité ; il
reste un échec du taux opérationnel et confirme qu'il faut recalibrer ou documenter
CTX-06 avant de l'utiliser comme mesure.

## Évolution descriptive de C-018 à C-019

Sur les 73 tâches évaluables, 56 réussissent dans les deux campagnes, 6 passent
d'échec dans C-018 à réussite dans C-019, 2 régressent, et 9 échouent dans les deux.
Les six transitions vers la réussite sont DOC-01, DOC-02, DOC-07, JAVA-08, SPRING-08
et WEB-08 ; les deux régressions sont AXON-06 et DOC-09.

C-019 a donc quatre réussites nettes supplémentaires et un taux qualité supérieur
de 5,48 points. C'est une observation opérationnelle d'un run par configuration,
pas une mesure causale de DFlash2. Les transitions montrent également qu'une seule
moyenne masquerait des régressions et des améliorations par tâche.

Les résultats bruts sont [C-018](../results/raw/campaigns/20260923T092442.115230Z-c-018-9fd089f6/campaign.json)
et [C-019](../results/raw/campaigns/20260923T114649.829983Z-c-019-bd43a89d/campaign.json).

## Échecs DOC-03 dans les cohortes

Les 18 runs FP8 sans DFlash2 retenus ont 4 échecs DOC-03 ; les 18 runs FP8 avec
DFlash2 en ont 9. Dans les 13 cas, le run modèle s'est terminé, le test public a
passé et le test caché a échoué. Aucun n'est classé comme erreur runner.

| Variante | Réussites DOC-03 | Échecs | Diagnostic des traces cachées |
|---|---:|---:|---|
| FP8 sans DFlash2 | 14/18 | 4 | Trois implémentations rejettent une notation de date valide ; une accepte une date calendrier invalide. |
| FP8 avec DFlash2 | 9/18 | 9 | Les neuf implémentations rejettent une notation de date valide. |

L'échec dominant est donc une erreur fonctionnelle de normalisation de date dans
l'implémentation produite. Mais il révèle aussi une ambiguïté du contrat de révision 1 :
le prompt exige une date ISO normalisée sans énumérer les formats d'entrée acceptés ;
l'unique fixture publique montre une notation, tandis que le validateur caché en
demande une autre. Le cas de date invalide accepté dans un run sans DFlash2, lui,
contredit directement l'exigence visible de rejeter les dates malformées.

Le run initial sans télémétrie à 5 agents, exclu des 18 runs retenus, a aussi échoué
sur DOC-03 ; il n'est pas inclus dans les comptes ci-dessus. Détails et liens vers
les campagnes conservées : [série sans DFlash2](COHORT_SESSION_2026-09-24.md) et
[série avec DFlash2](COHORT_SESSION_2026-09-24-DFLASH2.md).

## Suites recommandées

1. Conserver les résultats et validateurs actuels de DOC-03 comme révision 1 ; ne
   pas attribuer les 12 rejets du format de date au seul modèle tant que le contrat
   reste ambigu.
2. Clarifier dans le prompt et les notes les formats de date acceptés. Si le prompt,
   les données ou les tests changent, créer une nouvelle révision de DOC-03 et
   consigner le changement dans [CHANGELOG.md](CHANGELOG.md) avant toute nouvelle comparaison.
3. Pour les prochaines campagnes qualité, auditer les plafonds de sortie effectifs
   par tâche et distinguer les réponses coupées des contenus non JSON terminés.
   Toute modification de budget doit être figée dans une nouvelle configuration de
   campagne ; les taux C-018/C-019 restent ceux de leurs configurations exécutées.
4. Garder CTX-06 séparément dans le backlog de recalibrage de contexte.

Cette analyse ne modifie ni les tâches, ni les tests cachés, ni les artefacts bruts.
