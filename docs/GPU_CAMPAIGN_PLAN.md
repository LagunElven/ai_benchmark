# Plan des campagnes GPU — Milestone 11

Ce document prépare les campagnes réelles sur une NVIDIA H200 et une NVIDIA
RTX PRO 6000 Blackwell. Il sépare les comparaisons contrôlées, destinées à
mesurer l'effet du matériel ou de la quantification, des profils opérationnels
qui cherchent le meilleur service possible sur chaque carte.

Les campagnes listées ici sont planifiées, pas exécutées. Les résultats ne
doivent être ajoutés à `docs/CAMPAIGN_MATRIX.md` qu'après la conservation des
artefacts bruts et la génération des rapports.

## Campagnes planifiées

| ID | Statut | Matériel | Format | Type de comparaison | Objectif |
|---|---|---|---|---|---|
| C-003 | planifiée | 1x H200 | BF16 | contrôlée matériel | qualité de référence BF16 |
| C-004 | planifiée | 1x RTX PRO 6000 Blackwell | BF16 | contrôlée matériel | qualité de référence BF16 |
| C-005 | planifiée | 1x H200 | Q8_0 | contrôlée matériel | qualité de référence Q8_0 |
| C-006 | planifiée | 1x RTX PRO 6000 Blackwell | Q8_0 | contrôlée matériel | qualité de référence Q8_0 |
| C-007 | exploratoire | 1x H200 | UD-Q8_K_XL | opérationnelle | mesurer le compromis Unsloth UD |
| C-008 | exploratoire | 1x RTX PRO 6000 Blackwell | UD-Q8_K_XL | opérationnelle | mesurer le compromis Unsloth UD |

C-003/C-004 forment la comparaison matérielle BF16 et C-005/C-006 la
comparaison matérielle Q8_0. C-003/C-005 et C-004/C-006 permettent ensuite une
comparaison de quantification sur chaque carte. C-007/C-008 restent séparées :
une quantification UD, un fichier et potentiellement une révision différente
ne permettent pas d'attribuer un écart uniquement au GPU.

## Configuration contrôlée de départ

Les quatre campagnes C-003 à C-006 doivent partager les paramètres ci-dessous.
Seuls le GPU et le format BF16/Q8_0 changent dans chaque comparaison annoncée.

- Modèle : `Qwen3.8-27B-GGUF`, même dépôt, même révision et même tokenizer pour
  les quatre campagnes.
- Moteur : même moteur, même version et même build CUDA ; le backend GGUF
  effectivement utilisé doit être consigné dans le run.
- GPU : un seul accélérateur, tensor parallelism 1, pipeline parallelism 1.
- KV cache : `Q8_0`, K et V ; aucune modification silencieuse entre les cartes.
- Contexte : cible native 262 144 tokens, validée par une montée progressive
  `64k -> 128k -> 262k`. Une limite inférieure effectivement imposée par le
  moteur doit être enregistrée comme un résultat de capacité, pas masquée.
- Concurrence qualité : 1, slots 1 et prefix caching désactivé.
- Batch qualité : valeur commune conservatrice, à fixer après le smoke mémoire
  et à conserver pour C-003 à C-006.
- Thinking : activé ; `reasoning_effort=xhigh` lorsque le serveur et le
  template Qwen le supportent.
- Échantillonnage thinking : température 1.0, `top_p=0.95`, `top_k=20`,
  `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`.
- Seed : 42 lorsque supporté.
- Sortie : plafond initial 32 768 tokens, identique entre les campagnes.
- Flash attention : activée si disponible sur les deux builds ; le nom exact
  de l'option et son état effectif doivent être conservés dans les métadonnées.
- Speculative decoding : désactivé pour la première série qualité afin de ne
  pas ajouter un second modèle ou un backend MTP comme variable expérimentale.

Le contexte 262k est un objectif de validation, pas une promesse de capacité
à pleine charge. Le poids du modèle, le KV cache, les buffers CUDA, les graphes
et les sorties simultanées doivent tous tenir dans la mémoire disponible.

## Pourquoi les paramètres ne seront pas toujours identiques

Pour une comparaison scientifique du matériel, les paramètres doivent être
identiques autant que possible. Sinon, une différence de débit ou de latence
peut venir du batch, du nombre de slots ou du cache et non du GPU.

Pour choisir une configuration exploitable en production, il est au contraire
pertinent d'optimiser chaque carte séparément. Ces résultats seront alors
étiquetés `operational solution comparison` et ne serviront pas à conclure
qu'un GPU est intrinsèquement plus rapide qu'un autre.

La séquence retenue est donc :

1. quatre campagnes qualité contrôlées C-003 à C-006 ;
2. campagne serving contrôlée avec la configuration commune ;
3. profils serving optimisés séparément par carte ;
4. essais UD-Q8_K_XL C-007/C-008 après validation des profils Q8_0.

## Profils opérationnels à tester après la série contrôlée

Les valeurs ci-dessous sont des points de départ, pas des valeurs garanties.
Chaque changement doit être précédé d'un smoke court et consigné dans la
configuration du run.

### H200

- Commencer par BF16 puis Q8_0 avec contexte 262k.
- Tester ensuite un contexte supérieur uniquement si la montée de capacité
  précédente est stable.
- Augmenter progressivement `batch_size` et le nombre de slots ; la H200 peut
  être testée avec une enveloppe plus agressive grâce à sa mémoire HBM, mais la
  capacité réelle doit être mesurée avec KV Q8.
- Activer le speculative decoding/MTP seulement dans une campagne dédiée,
  après avoir établi le débit sans spéculation.

### RTX PRO 6000 Blackwell

- Commencer par BF16 avec contexte 128k puis 262k, et par Q8_0 avec le même
  protocole de montée.
- Garder un seul slot au smoke initial ; tester 2 puis 4 slots seulement après
  validation de la mémoire et de la stabilité.
- Augmenter le batch par paliers plus prudents que sur H200.
- Tester MTP dans une campagne séparée, car son coût mémoire peut modifier la
  capacité de contexte disponible.

Ces profils ne remplacent pas C-003 à C-006 : ils répondent à une question
d'exploitation et non à une comparaison contrôlée.

## Ordre de reprise demain

### 1. Préflight logiciel et matériel

Capturer et conserver :

- commit Git du benchmark ;
- modèle, dépôt, révision, tokenizer et SHA-256 de chaque fichier GGUF ;
- version du moteur, build CUDA, pilote et OS/image ;
- modèle exact du GPU, mémoire, température et mémoire hôte ;
- commande de lancement complète, paramètres effectifs et logs serveur.

Vérifier également que le fichier BF16, le fichier Q8_0 et leurs éventuels
fichiers MTP/mmproj proviennent bien de la source choisie. Ne pas mélanger un
Q8_0 `ggml-org` avec un UD-Q8_K_XL `Unsloth` dans une comparaison contrôlée.

### 2. Smoke et montée mémoire

Pour chaque format et chaque carte :

1. démarrer le serveur avec slots 1, batch conservateur et KV Q8 ;
2. exécuter une requête courte de validation du template et du thinking ;
3. tester environ 64k, 128k puis 262k tokens ;
4. noter la mémoire utilisée, le temps de démarrage, les erreurs HTTP, OOM,
   crash et limite de contexte effective ;
5. arrêter la campagne si le serveur devient instable et conserver le log.

Une capacité refusée par le moteur ou un OOM est un résultat exploitable. Il ne
faut pas relancer silencieusement avec des paramètres différents en conservant
le même identifiant de campagne.

### 3. Qualité

Lancer la suite complète des 74 tâches en mode `repair`, avec le même ordre et
les mêmes budgets pour C-003 à C-006. Produire pour chaque campagne :

- résultats bruts JSON/JSONL non écrasés ;
- synthèse par catégorie ;
- détail tâche par tâche avec commentaire d'échec ;
- Pass@1/2/3, appels, tokens entrée/sortie et temps ;
- état des tâches CTX-01 à CTX-06 et taille de contexte réellement acceptée.

### 4. Serving

Lancer séparément la matrice serving définie dans `serving/config.yaml` après
avoir remplacé ses métadonnées Gemma par celles de la campagne Qwen. Conserver
la séparation entre `cold` et `shared-prefix`, et ne pas mélanger les mesures
avec les résultats qualité.

### 5. Mise à jour et arrêt propre

Après chaque campagne terminée :

1. générer les rapports ;
2. ajouter la colonne correspondante à `docs/CAMPAIGN_MATRIX.md` seulement si
   les résultats bruts sont présents ;
3. vérifier les tests et la validation de configuration ;
4. commit et push avec l'identifiant de campagne dans le message ;
5. noter tout écart au protocole dans le rapport, sans réécrire les résultats.

## Critères de comparabilité

Une campagne est `controlled hardware comparison` uniquement si le modèle, la
révision, le tokenizer, le format, le moteur, les paramètres de génération, le
contexte, le batch, les slots, le KV cache et les entrées sont identiques. Le
GPU est alors la variable étudiée.

Une campagne devient `operational solution comparison` dès qu'un ou plusieurs
de ces éléments sont adaptés à la carte. Les rapports doivent le dire
explicitement et conserver les paramètres complets de chaque run.

## Références techniques

- [Qwen3.8-27B — fiche modèle](https://huggingface.co/Qwen/Qwen3.8-27B)
- [Qwen3.8-27B — configuration officielle](https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json)
- [GGUF Qwen3.8-27B — dépôt ggml-org](https://huggingface.co/ggml-org/Qwen3.8-27B-GGUF/tree/main)
- [GGUF Qwen3.8-27B — dépôt Unsloth](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/main)
- [NVIDIA H200](https://www.nvidia.com/en-gb/data-center/h200/)
- [NVIDIA RTX PRO 6000 Blackwell](https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000-family/)
