# Enterprise LLM Benchmark

Suite reproductible pour comparer la qualité, la réparation agentique, les capacités
documentaires/OCR et les performances de serving de modèles locaux ou hébergés.

La fondation actuelle couvre les milestones 0 à 10 : schémas, découverte des tâches,
workspace propre, exécution `one-shot`, endpoint OpenAI-compatible, faux adaptateur
déterministe, validation publique et cachée isolée, boucle `repair` et résultats JSON/JSONL.
Le benchmark serving dispose d'une matrice reproductible concurrence/contexte/préfixe et
conserve ses résultats séparément des résultats de qualité.

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
python -m pip install -e .
```

## Commandes

```powershell
python -m runner validate-config
python -m runner list-tasks
python -m runner list-tasks --suite smoke --category java
python -m runner run --task-id JAVA-03 --mode one-shot
python scripts/run_smoke.py
python scripts/generate_context_variants.py tasks/context/CTX-01/workspace .tmp/context-ctx01 --relevant-file src/billing.py
python scripts/score_context.py --manifest .tmp/context-ctx01/ctx-10k/context-manifest.json --modified-file src/billing.py
python scripts/check_catalogue.py
python scripts/run_serving_benchmark.py --plan-only
python scripts/prepare_gpu_campaign.py --campaign-id C-003 --config benchmark.qwen3.8-bf16.yaml --serving-config campaigns/gpu/serving-qwen.yaml
python scripts/run_quality_campaign.py --campaign-id C-003 --plan-only
python -m unittest discover -s tests -v
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
- `campaigns/gpu/plan.yaml` : campagnes C-003 à C-006, C-009/C-010 et C-011/C-012, avec les valeurs à figer avant location.
- `docs/CATALOGUE.md` : inventaire des 74 tâches cibles et état d'implémentation.
- `docs/ROADMAP.md` : milestones.
- `docs/CHANGELOG.md` : changements affectant la comparabilité.

## État des fonctions sensibles

Les tests cachés sont injectés uniquement dans une copie validator-visible distincte du
workspace du modèle, puis supprimés après validation. Le mode `repair` renvoie uniquement les
logs publics entre tentatives et s'arrête dès que la validation finale réussit. L'isolation
forte par conteneur reste à traiter pour les validateurs non fiables.
