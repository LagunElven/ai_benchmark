# Enterprise LLM Benchmark

Suite reproductible pour comparer la qualité, la réparation agentique, les capacités
documentaires/OCR et les performances de serving de modèles locaux ou hébergés.

Les milestones 0 à 10 sont en place : schémas, découverte des tâches, workspaces propres,
exécutions `one-shot` et `repair`, validation publique et cachée isolée, résultats JSON/JSONL,
catalogue de 74 tâches et matrice de serving reproductible.

Le milestone 11 est en cours. Les profils opérationnels Qwen C-016 (BF16) et C-017 (Q8)
ont été évalués sur RTX PRO 6000. La réplication documentaire Q8 et sa matrice serving sont
terminées ; la comparaison BF16/Q8 reste opérationnelle, notamment parce que C-017 utilise
un checkpoint tiers. Les campagnes matérielles contrôlées H200, RTX PRO et DGX Spark ainsi
que les campagnes NVFP4 restent à exécuter. Le reporting comparatif est planifié au
milestone 12. Voir la [roadmap](docs/ROADMAP.md), la [matrice des campagnes](docs/CAMPAIGN_MATRIX.md)
et le [compte rendu GPU du 22 septembre](docs/GPU_SESSION_2026-09-22.md).

Une smoke suite hors ligne de sept tâches représentatives (Java, Spring, Axon, Web,
COBOL, documents et long contexte) peut être lancée avec :

```powershell
python scripts/run_smoke.py
```

Elle utilise uniquement des réponses de test sous `tests/fixtures/`; ces fixtures ne
sont jamais copiées dans le workspace présenté à un modèle évalué.

## Installation locale

Python 3.11 ou plus récent est requis.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Commandes

```powershell
python -m runner validate-config
python -m runner list-tasks
python -m runner list-tasks --suite smoke --category java
python -m runner run --task-id JAVA-03 --mode one-shot
python scripts/run_smoke.py
python scripts/generate_context_variants.py tasks/context/CTX-01/workspace .tmp/context-ctx01 --relevant-file src/billing.py
python scripts/score_context.py --manifest .tmp/context-ctx01/ctx-10k.context-manifest.json --modified-file src/billing.py
python scripts/check_catalogue.py
python scripts/run_serving_benchmark.py --plan-only
python scripts/prepare_gpu_campaign.py --campaign-id C-003 --config benchmark.qwen3.8-bf16.yaml --serving-config campaigns/gpu/serving-qwen.yaml
python scripts/run_quality_campaign.py --campaign-id C-003 --plan-only
# Lancer puis reprendre avec le même seed explicite
python scripts/run_quality_campaign.py --campaign-id C-003 --seed 43
python scripts/run_quality_campaign.py --campaign-id C-003 --seed 43 --resume
# Pour comparer plusieurs seeds, répéter le même jeu sur chaque configuration
python -m unittest discover -s tests -v
python -m ruff check runner serving scripts tests
```

L'URL du serveur et le modèle se configurent dans `benchmark.yaml`. La clé d'API est lue
depuis la variable dont le nom figure dans `model.api_key_env`; elle n'est jamais stockée dans
les résultats.

## Documentation

- `AGENTS.md` : règles de contribution et périmètre complet.
- `docs/BENCHMARK_PLAN.md` : objectifs et plan de construction.
- `docs/TASK_AUTHORING.md` : format et conception des tâches.
- `docs/METRICS.md` : métriques et comparabilité.
- `docs/ARCHITECTURE.md` : composants et frontières de sécurité.
- `docs/EXECUTION_PROTOCOL.md` : cycle précis d'un run.
- `docs/DOCUMENTS.md` : génération des fixtures et scoring OCR/documents.
- `docs/LEGACY.md` : statuts des fixtures legacy et équivalences Java.
- `docs/CONTEXT.md` : génération et mesure des variantes long-context.
- `docs/SERVING.md` : matrice, exécution et métriques du benchmark serving.
- `docs/GPU_CAMPAIGN_PLAN.md` : protocole et ordre des futures campagnes GPU.
- `docs/GPU_REMOTE_RUNBOOK.md` : préparation et exécution sur une machine GPU louée.
- `docs/REMOTE_GPU_CHECKLIST.md` : checklist courte avant location, après connexion et avant arrêt.
- `campaigns/gpu/plan.yaml` : plan machine-readable des campagnes GPU et configurations à figer.
- `docs/CAMPAIGN_MATRIX.md` : résultats de qualité et de serving effectivement documentés.
- `docs/GPU_SESSION_2026-09-22.md` : résultats et limites de la session BF16/Q8 sur RTX PRO 6000.
- `docs/CATALOGUE.md` : inventaire des 74 tâches cibles et état d'implémentation.
- `docs/TASK_REFERENCE.md` : référence synthétique par tâche, critères de réussite,
  d'échec et pièges à surveiller.
- `docs/ROADMAP.md` : état courant des milestones et prochaines actions.
- `docs/CHANGELOG.md` : changements affectant la comparabilité.

## État des fonctions sensibles

Les tests cachés sont injectés uniquement dans une copie validator-visible distincte du
workspace du modèle, puis supprimés après validation. Le mode `repair` renvoie uniquement les
logs publics entre tentatives et s'arrête dès que la validation finale réussit. L'isolation
forte par conteneur reste à traiter pour les validateurs non fiables.
