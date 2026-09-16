# Matrice des campagnes

Document de suivi initial des campagnes qualité. Les colonnes correspondent aux campagnes ; les lignes gardent les mêmes catégories et métriques pour faciliter les comparaisons futures.

Cette matrice reste volontairement simple pour la milestone 10. La présentation et les analyses comparatives seront approfondies en milestone 12.

## Campagnes référencées

| ID | Date | Campagne | Rapport |
|---|---|---|---|
| C-001 | 2026-09-16 | Gemma 4 local — baseline, thinking désactivé | [Synthèse](../results/reports/gemma4-local-20260916.md) |
| C-002 | 2026-09-16 | Gemma 4 local — thinking / contexte 100k | [Synthèse](../results/reports/gemma4-thinking-100k-20260916.md) |

Les résultats détaillés sont disponibles dans les rapports associés. Les résultats bruts restent dans results/raw et sont indexés par results/raw/runs.jsonl.

## Matrice qualité

Les valeurs de catégorie sont au format réussites/total. Les tokens sont ceux rapportés par l’endpoint OpenAI-compatible et le temps est le temps cumulé des runs qualité.

| Métrique | C-001 | C-002 |
|---|---:|---:|
| ABAL | 4/4 | 4/4 |
| Axon | 8/10 | 9/10 |
| COBOL | 3/5 | 4/5 |
| Context | 1/6 | 3/6 |
| Delphi | 4/4 | 4/4 |
| Documents | 1/10 | 2/10 |
| E2E | 2/3 | 2/3 |
| Java | 6/8 | 6/8 |
| Spring | 8/10 | 8/10 |
| Web | 5/10 | 5/10 |
| WinDev | 3/4 | 4/4 |
| **Total réussi** | **45/74** | **51/74** |
| Pass@1 | 43/74 | 47/74 |
| Pass@2 | 45/74 | 51/74 |
| Pass@3 | 45/74 | 51/74 |
| Appels modèle | 94 | 101 |
| Tokens entrée | 83 612 | 212 558 |
| Tokens générés | 48 041 | 867 269 |
| Temps cumulé | 30 min 29 s | 2 h 50 min 31 s |

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
