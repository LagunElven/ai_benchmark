# Session GPU du 18 septembre 2026

## Environnement utilisé

- GPU : NVIDIA RTX PRO 6000 Blackwell Server Edition, 96 GiB
- CPU : Xeon Platform 8559C
- Pilote : 610.43.02
- CUDA visible : 13.3
- Image : `vastai/vllm:v0.29.0-cuda-13.0`
- Moteur : vLLM 0.29.0
- Modèle : `Qwen/Qwen3.8-27B`
- Révision modèle et tokenizer : `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`
- Poids : BF16
- KV cache : FP8
- Contexte configuré : 262144 tokens
- `max_num_seqs` : 16
- Parser de raisonnement : `qwen3`
- Prefix caching : activé

Le endpoint OpenAI-compatible local a été validé avant les campagnes. Le
checkpoint a utilisé environ 89--92 GiB de mémoire GPU pendant la génération,
avec une utilisation GPU proche de 100 %. Aucun OOM n'a été observé.

## Serving

La campagne serving limitée au mode `shared-prefix` a terminé 20 cas de
matrice et 270 requêtes sans erreur ni OOM. Le prefix caching a produit un gain
important sur les préfixes partagés, notamment sur les contextes 64k et plus.
Le profil est conservé dans
[`campaigns/gpu/serving-qwen-rtx-pro-6000-shared-prefix.yaml`](../campaigns/gpu/serving-qwen-rtx-pro-6000-shared-prefix.yaml).

## Campagne qualité C-015

C-015 est un profil opérationnel BF16 avec prefix caching et
`reasoning_effort: low`. La configuration versionnée est
[`benchmark.qwen3.8-bf16-shared-prefix-low-thinking.yaml`](../benchmark.qwen3.8-bf16-shared-prefix-low-thinking.yaml).

### Smoke et calibrage

- Smoke : 7/7 tâches réussies en environ 5 minutes.
- AXON-03 ciblé : réussi en environ 37 secondes.
- Résultats smoke :
  `results/raw/campaigns/20260918T133723.264083Z-c-015-115853bc/campaign.json`
- Résultat AXON-03 ciblé :
  `results/raw/campaigns/20260918T133925.211372Z-c-015-0a971016/campaign.json`

Le passage de `xhigh` à `low` a fortement réduit les durées sur les tâches
simples. AXON-01 et AXON-02 sont passées en environ 22 et 34 secondes dans la
campagne low, contre environ 111 et 281 secondes dans l'essai précédent en
`xhigh`.

### Campagne complète interrompue

La campagne complète a été arrêtée manuellement après WL-04, à la tâche 54/74.
Les résultats individuels des 54 tâches terminées sont conservés sous
`results/raw/`, mais le `campaign.json` global n'a pas été finalisé. Un dossier
partiel de SPRING-01 contenant uniquement une réponse modèle ne constitue pas
un résultat de tâche et n'est pas comptabilisé.

Bilan des 54 tâches terminées :

- 41 réussites
- 13 échecs
- AXON : 9/10
- Contexte : 5/6 ; CTX-06 rejetée par HTTP 400 avant génération
- Documents : 2/10
- E2E : 2/3
- Java : 6/8
- ABAL : 4/4
- COBOL : 5/5
- Delphi : 4/4
- WinDev/WLanguage : 4/4

### Analyse des échecs

- AXON-10 : les tests publics passent, mais le test caché provoque un
  `NullPointerException` pour une commande `null`.
- CTX-06 : l'estimation de 200k tokens du générateur de contexte est trop
  optimiste pour le prompt réellement sérialisé. Les mesures CTX-03 à CTX-05
  indiquent qu'un prompt CTX-06 dépasserait probablement la fenêtre effective
  de 262144 tokens, avant même la marge de sortie. Le test doit être recalibré
  avec le tokenizer exact ou abaissé pour cette configuration.
- Documents : plusieurs implémentations acceptent des dates invalides,
  normalisent mal les dates, acceptent des champs incomplets ou échouent sur
  des tables/formulaires complexes. Les premiers appels ont aussi fréquemment
  produit une réponse non JSON, entraînant une réparation coûteuse.
- E2E-01, JAVA-07 et JAVA-08 : échecs de cas limites cachés après compilation
  et parfois après réussite des tests publics.

Le profil `low` est donc très efficace pour les tâches de compréhension,
migration et code relativement direct, mais moins robuste pour les validations
documentaires, les cas limites et les tâches complexes. `low` est une consigne
d'effort adaptatif, pas une limite stricte de tokens de raisonnement.

## Décisions et suite recommandée

1. Conserver C-015 comme profil opérationnel rapide, sans la présenter comme
   une référence de qualité universelle.
2. Tester ensuite le Qwen officiel avec `reasoning_effort: medium` sur les
   tâches échouées avant de relancer une suite complète.
3. Garder l'appel d'outils pour une campagne distincte : il pourrait aider les
   tâches multi-fichiers et les longs contextes, mais changerait le protocole et
   la comparabilité avec C-015.
4. Le modèle Swift n'a pas été retenu à ce stade en raison de sa restriction
   de licence commerciale.
5. Le checkpoint
   `ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF`, en particulier IQ3_S, est un candidat
   de quantification à examiner. Sa licence Apache 2.0 est plus simple pour
   notre usage, mais le support GGUF vLLM reste expérimental ; il devra faire
   l'objet d'un smoke séparé, éventuellement avec llama.cpp.

L'instance GPU a été arrêtée après cette session. Les résultats bruts restent
sur le poste local, conformément au `.gitignore`, et ne sont pas réécrits par
les configurations versionnées.
