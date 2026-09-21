# Session GPU du 21 septembre 2026

## Objectif de la session

Comparer le profil qualité Qwen3.8-27B BF16 avec `reasoning_effort: medium` à
un checkpoint INT8/W8A16 servi par vLLM sur une NVIDIA RTX PRO 6000 Blackwell
Server Edition, puis préparer les mesures de concurrence.

## Environnement distant

- GPU : NVIDIA RTX PRO 6000 Blackwell Server Edition, 96 GiB
- Pilote : 610.43.02
- CUDA visible : 13.3
- Moteur : vLLM 0.29.0
- KV cache : FP8
- Parser : `qwen3`
- Tensor parallelism : 1
- Pipeline parallelism : 1
- `max_num_seqs` : 16 pour la configuration qualité
- Contexte cible : 262144 tokens

Le portail Caddy de l'instance occupe le port distant `8000`. vLLM Q8 a donc
été lancé sur le port distant `8001`. Le tunnel SSH mappe le port local `8000`
vers le port distant `8001`, ce qui permet de conserver `base_url:
http://127.0.0.1:8000/v1` dans les configurations du benchmark.

## Profil Q8

- Dépôt : `GotoAI-Inc/Qwen3.8-27B-W8A16`
- Révision : `e349969d1d27552c755c992ae64a2ea56007f3e4`
- Format : `INT8-W8A16` Safetensors `compressed-tensors`
- Activations : BF16
- Tokenizer : `Qwen/Qwen3.8-27B`, révision
  `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`
- Nom servi : `Qwen3.8-27B-Q8`
- Configuration versionnée :
  [`benchmark.qwen3.8-q8-w8a16-shared-prefix-medium-thinking.yaml`](../benchmark.qwen3.8-q8-w8a16-shared-prefix-medium-thinking.yaml)
- Campagne : `C-017`

Le checkpoint est tiers et non officiel Qwen. C-017 reste donc exploratoire
jusqu'à la réplication documentaire et la mesure serving ; il ne faut pas
présenter son résultat comme une équivalence définitive BF16/Q8.

## Incidents de démarrage et réseau

- Le port distant `8000` était occupé par
  `/opt/portal-aio/caddy_manager/caddy` ; le processus Caddy n'a pas été tué.
- Un premier démarrage Q8 avec le contexte étendu a laissé un processus
  `VLLM::EngineCore` orphelin consommant environ 89 GiB ; il a été terminé
  avant le smoke suivant.
- Le smoke Q8 a d'abord été lancé avec `max_model_len=65536` et
  `max_num_seqs=2`. Cette configuration a permis de valider le chargement, mais
  elle ne convenait pas à une campagne complète de contexte.
- Le tunnel SSH final utilise le mapping local `8000` vers distant `8001`.

## Résultats qualité BF16 medium

Le profil BF16 no-thinking `C-013` avait obtenu **0/11** sur le sous-ensemble
diagnostique, sans erreur de protocole. Le profil `C-016` avec thinking
`medium` avait ensuite obtenu **5/11** sur ce même sous-ensemble, ce qui a
justifié son extension à la suite complète.

Configuration : C-016, Qwen3.8-27B BF16, prefix caching, thinking `medium`.

- Résultat : **64/74**, soit **86,5 %**.
- Résultat brut :
  [`20260921T110238.257698Z-c-016-81173711/campaign.json`](../results/raw/campaigns/20260921T110238.257698Z-c-016-81173711/campaign.json)
- Temps écoulé : environ **1 h 40 min**.

Ce profil est devenu la baseline qualité BF16 de référence pour la comparaison
Q8, avec C-013 no-thinking et C-015 low conservés comme profils opérationnels.

## Résultats qualité Q8

### Première exécution non comparable

La première exécution C-017 a utilisé le serveur smoke limité à 65536 tokens.
Elle a produit **60/74**, mais `CTX-03` à `CTX-06` ont échoué en HTTP 400 avant
génération. Ce résultat est conservé comme mesure indicative de performance,
mais n'est pas utilisé pour conclure sur la qualité.

Résultat :
[`20260921T145105.155254Z-c-017-8b2b2a4e/campaign.json`](../results/raw/campaigns/20260921T145105.155254Z-c-017-8b2b2a4e/campaign.json)

### Exécution avec contexte étendu

Après redémarrage vLLM avec `max_model_len=262144`, C-017 a produit :

- **62/74**, soit **83,8 %** ;
- `CTX-01` à `CTX-05` réussies ;
- `CTX-06` échoue encore en HTTP 400 car le prompt sérialisé dépasse la
  fenêtre effective de 262144 tokens, comme en BF16 ;
- temps écoulé : environ **1 h 00 min** ;
- résultat brut :
  [`20260921T155315.525802Z-c-017-35d4e399/campaign.json`](../results/raw/campaigns/20260921T155315.525802Z-c-017-35d4e399/campaign.json)

Comparaison directe avec C-016 :

- 60 tâches réussies par les deux profils ;
- Q8 réussit en plus `SPRING-04` et `WEB-10` ;
- BF16 réussit en plus `DOC-02`, `DOC-03`, `DOC-07` et `WEB-07` ;
- écart global : **−2 tâches**, soit **−2,7 points**.

Par catégorie, Q8 est équivalent ou meilleur sur Axon, contexte, Java, Spring,
Web et les catégories legacy. L'écart est concentré sur les documents :

- BF16 : **7/10** ;
- Q8 : **4/10**.

Les échecs documentaires Q8 sont `DOC-02`, `DOC-03`, `DOC-05`, `DOC-06`,
`DOC-07` et `DOC-08`. La première exécution Q8 avait obtenu un autre profil
sur plusieurs de ces tâches, ce qui justifie une réplication ciblée avant de
conclure à une perte systématique due à la quantification.

### Vitesse et protocole

- C-016 : environ **100 min 29 s** ;
- C-017 étendu : environ **60 min 05 s** ;
- gain corrigé : environ **40 %** ;
- les appels modèle sont pratiquement aussi nombreux, le gain provient donc
  principalement de la vitesse d'inférence.

C-017 étendu a enregistré 8 `ChangeProtocolError` et 1 `ModelClientError`.
Le champ agrégé `tasks_with_errors` reste à zéro et sous-estime ces erreurs de
réponse ; l'analyse doit continuer à utiliser les `result.json` individuels.

## Décisions pour la prochaine session

1. Conserver C-016 comme baseline qualité BF16 medium.
2. Conserver C-017 comme candidat Q8 opérationnel à fort gain de vitesse.
3. Ne pas déclarer Q8 équivalent au BF16 pour les documents sans réplication.
4. Ne pas relancer une campagne qualité complète avant la campagne documentaire
   ciblée et la validation serving.

## TODO de la prochaine session

### Révision documentaire Q8

Répéter avec Q8 les tâches `DOC-02`, `DOC-03`, `DOC-05`, `DOC-06`, `DOC-07` et
`DOC-08`, idéalement avec plusieurs répétitions et avec la même sélection en
BF16. Comparer séparément les erreurs de validation cachée, les erreurs de
protocole, les tokens et les temps de réparation.

### Serving et concurrence Q8

Créer un clone Q8 de
[`serving-qwen-rtx-pro-6000-full.yaml`](../campaigns/gpu/serving-qwen-rtx-pro-6000-full.yaml)
avec le checkpoint `INT8-W8A16`, le nom servi Q8, le port distant `8001` et le
même endpoint local `8000`. Exécuter la matrice complète :

- concurrence 1, 2, 5 et 10 ;
- contextes 8k, 32k, 64k, 100k et 200k ;
- préfixes `cold` et `shared-prefix` ;
- warmup puis trois répétitions ;
- `enable_thinking=false` pour isoler la performance de serving.

Comparer BF16/Q8 sur TTFT p50/p95, TPOT, tokens/s par utilisateur, débit
agrégé, latence totale, mémoire GPU, KV cache et taux d'OOM/échec.

### Corrections de reporting à prévoir

- Faire compter les `ChangeProtocolError` et `ModelClientError` individuels dans
  un résumé de campagne distinct de `tasks_with_errors`.
- Conserver séparément les échecs de capacité de contexte (`CTX-06`) et les
  échecs fonctionnels du modèle.
