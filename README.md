# Enterprise LLM Benchmark

Suite reproductible pour comparer la qualité, la réparation agentique, les capacités
documentaires/OCR et les performances de serving de modèles locaux ou hébergés.

La fondation actuelle couvre les milestones 0 à 5 : schémas, découverte des tâches,
workspace propre, exécution `one-shot`, endpoint OpenAI-compatible, faux adaptateur
déterministe, validation publique et cachée isolée, boucle `repair` et résultats JSON/JSONL.

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
- `docs/ROADMAP.md` : milestones.
- `docs/CHANGELOG.md` : changements affectant la comparabilité.

## État des fonctions sensibles

Les tests cachés sont injectés uniquement dans une copie validator-visible distincte du
workspace du modèle, puis supprimés après validation. Le mode `repair` renvoie uniquement les
logs publics entre tentatives et s'arrête dès que la validation finale réussit. L'isolation
forte par conteneur reste à traiter pour les validateurs non fiables.
