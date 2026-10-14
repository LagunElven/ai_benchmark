# Cohortes SGLang NVFP4 + DFlash2 sur DGX Spark — 14 octobre 2026

## Périmètre

C-025 comprend 18 runs du pilote fermé de 18 tâches : trois répétitions pour
chacun des niveaux 1, 4, 5, 6, 8 et 10 agents. Le plan, les tâches et leurs
révisions sont identiques dans les manifestes. Le smoke séquentiel distinct de
dix tâches n'est pas inclus dans les statistiques ci-dessous.

La configuration modèle est Qwen3.8-27B NVFP4, révision
`dbb8f445b3145f8a4c18ddc769f032d57d32867c`, tokenizer
`1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`, et draft
`incoai/Qwen3.8-27B-DFlash2`, révision
`015e795645c74b1a0eeef3b570031fb62e769bc5`. Les runs utilisent SGLang
`0.0.0.dev1+g5f55db35e`, image épinglée
`lmsysorg/sglang@sha256:616a3e97f45191af975896cfa644279096cb31bd408a071c2e99ca7209c3cafe`,
KV cache FP8, `reasoning_effort=medium`, seed 42, DFlash avec huit tokens draft
et le contexte configuré à 262 144 tokens. Les paramètres détaillés figurent
dans le [runbook DGX Spark](SGLANG_DGX_SPARK_RUNBOOK.md).

Les 18 manifestes portent le même hash de configuration benchmark
`29f0d12a69ffdd4f4c850e9144c79e6d19d7eefa8ae3c6df680ab777e88eecda` et le même
hash de plan `7b2f19101c0c57df4f855383ba6180012d10a2c3b4b82fe34a65575d2107b96b`.
Ils enregistrent le commit `49f2711a4f8db0b4417deb55701de0c5ee8420a0` et un
worktree sale (`working_tree_dirty: true`).

## Synthèse par niveau

| Agents | Réussites cumulées | Makespan médian (min–max) | Pic de requêtes mesuré | Runs |
|---:|---:|---:|---:|---:|
| 1 | 51/54 | 488,61 s (475,73–896,62) | 1 | 3 |
| 4 | 52/54 | 185,38 s (167,20–278,14) | 4 | 3 |
| 5 | 52/54 | 241,15 s (231,96–533,38) | 5 | 3 |
| 6 | 52/54 | 252,84 s (216,77–306,44) | 6 | 3 |
| 8 | 52/54 | 201,65 s (197,38–266,01) | 8 | 3 |
| 10 | 52/54 | 318,06 s (187,17–404,55) | 10 | 3 |
| **Total** | **311/324** | — | **tous les paliers atteints** | **18** |

Les médianes sont calculées sur les trois makespans de chaque niveau. Les
réussites cumulées gardent le nombre de tâches réussi dans chacun des trois
runs, sans agréger les durées. Les 18 runs ont atteint exactement la concurrence
configurée.

## Runs et manifestes bruts

| Agents | Run | Tâches réussies | Makespan | Échec de tâche | Manifeste |
|---:|---:|---:|---:|---|---|
| 1 | 1 | 17/18 | 896,62 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T144023.830406Z-cohort-a1-cfbc24c0/campaign.json) |
| 1 | 2 | 17/18 | 488,61 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T152329.187911Z-cohort-a1-ebb79981/campaign.json) |
| 1 | 3 | 17/18 | 475,73 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T162737.364373Z-cohort-a1-e6c04f7b/campaign.json) |
| 4 | 1 | 18/18 | 278,14 s | — | [campagne](../results/raw/cohort/20261014T143333.305278Z-cohort-a4-1507cff0/campaign.json) |
| 4 | 2 | 17/18 | 185,38 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T162023.967401Z-cohort-a4-4401ce29/campaign.json) |
| 4 | 3 | 17/18 | 167,20 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T162353.893341Z-cohort-a4-9ad997cf/campaign.json) |
| 5 | 1 | 17/18 | 231,96 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T150840.541155Z-cohort-a5-a8b46e80/campaign.json) |
| 5 | 2 | 17/18 | 533,38 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T160450.741290Z-cohort-a5-a9b55bec/campaign.json) |
| 5 | 3 | 18/18 | 241,15 s | — | [campagne](../results/raw/cohort/20261014T161349.992047Z-cohort-a5-988507c8/campaign.json) |
| 6 | 1 | 17/18 | 216,77 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T151354.607041Z-cohort-a6-6694f44e/campaign.json) |
| 6 | 2 | 18/18 | 306,44 s | — | [campagne](../results/raw/cohort/20261014T155339.203800Z-cohort-a6-e80dbb8b/campaign.json) |
| 6 | 3 | 17/18 | 252,84 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T155857.443559Z-cohort-a6-014ab37f/campaign.json) |
| 8 | 1 | 17/18 | 201,65 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T151927.336120Z-cohort-a8-4158133a/campaign.json) |
| 8 | 2 | 17/18 | 197,38 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T154328.856578Z-cohort-a8-4ea6634f/campaign.json) |
| 8 | 3 | 18/18 | 266,01 s | — | [campagne](../results/raw/cohort/20261014T154853.217196Z-cohort-a8-afb4db07/campaign.json) |
| 10 | 1 | 17/18 | 318,06 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T150304.281482Z-cohort-a10-f100e02f/campaign.json) |
| 10 | 2 | 17/18 | 404,55 s | `DOC-03` | [campagne](../results/raw/cohort/20261014T153213.712396Z-cohort-a10-1a331c2f/campaign.json) |
| 10 | 3 | 18/18 | 187,17 s | — | [campagne](../results/raw/cohort/20261014T154010.108165Z-cohort-a10-460ebbc7/campaign.json) |

## Échecs et télémétrie

Les 13 échecs de tâche concernent tous `DOC-03`. Pour chacun, le test public a
réussi et la validation cachée a échoué ; le contenu des tests cachés n'est pas
reproduit ici. Trois runs comportent aussi des `ChangeProtocolError` pendant les
réparations : deux événements dans le deuxième run à 5 agents, et un événement
dans chacun des deux premiers runs à 10 agents. Les manifestes ne signalent
aucune erreur de runner, requête modèle échouée ou tâche rejetée pour capacité.

La télémétrie distante est disponible pour les 18 runs : 5 815 échantillons au
total, tous sur le même NVIDIA GB10, UUID
`GPU-b9e280f0-fb24-0d67-ba08-c99d1b848a71`, driver `595.71.05`. L'utilisation
GPU moyenne par run varie de 92,91 à 95,94 % et le pic atteint 96 % dans chaque
run. La température maximale échantillonnée varie de 61 à 75 °C et la puissance
maximale de 42,69 à 91,25 W. Les champs de mémoire GPU sont indisponibles ; aucune
valeur de VRAM ou mémoire unifiée n'est déduite des mesures du runner local.

## Interprétation et limites

Le palier de dix requêtes simultanées a été atteint dans chacune des trois
répétitions à dix agents. Les résultats établissent la concurrence observée sur
ce serveur et cette configuration ; les makespans mesurent un lot fermé de 18
tâches, pas le débit d'un flux continu. Les 13 échecs étant tous `DOC-03`, ils
n'indiquent pas à eux seuls un mélange de réponses entre prompts.

Il n'existe pas dans cette campagne de cohorte RTX PRO 6000 sous SGLang avec
DFlash2 pour une comparaison matérielle exacte. La référence RTX PRO avec
NVFP4 + DFlash2 utilise vLLM ; la référence RTX PRO SGLang NVFP4 n'utilise pas
DFlash2. Voir les rapports [vLLM NVFP4 + DFlash2](COHORT_SESSION_NVFP4_DFLASH2_2026-09-28.md)
et [SGLang NVFP4](COHORT_SESSION_SGLANG_NVFP4_2026-09-29.md).

Le smoke de dix tâches précédemment exécuté reste une expérience séparée et
n'entre ni dans les 18 runs ni dans les statistiques de cette session. La
qualité complète et le serving C-025 restent à exécuter.
