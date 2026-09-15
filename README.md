# Enterprise LLM Benchmark

Suite reproductible pour comparer la qualité, la réparation agentique, les capacités
documentaires/OCR et les performances de serving de modèles locaux ou hébergés.

La fondation actuelle couvre les milestones 0 à 2 : schémas, découverte des tâches,
workspace propre, exécution `one-shot`, endpoint OpenAI-compatible, faux adaptateur
déterministe, validation publique et résultats JSON/JSONL.

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
python -m runner run --task-id JAVA-01 --mode one-shot
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
- `docs/ROADMAP.md` : milestones.
- `docs/CHANGELOG.md` : changements affectant la comparabilité.

## État des fonctions sensibles

Le mode `repair` et l'injection validator-visible des tests cachés ne sont pas encore actifs.
Une tâche déclarant des validations cachées peut exécuter sa validation publique, mais son run
reste explicitement `incomplete`. L'isolation forte et sa preuve automatisée constituent le
prochain milestone.
