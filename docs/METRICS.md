# Métriques du benchmark

## 1. Philosophie

Toujours conserver les métriques brutes. Les scores agrégés sont des vues dérivées.

## 2. Qualité de code

### Résultats fonctionnels

- build_success
- public_tests_passed / total
- hidden_tests_passed / total
- regression_tests_passed / total
- task_success

### Réparation

- pass_at_1
- pass_at_2
- pass_at_3
- successful_iteration
- repeated_failure_pattern
- time_until_success
- tokens_until_success

En mode `repair`, chaque tentative conserve son groupe de validations publiques et son artefact
de réponse. `pass_at_n` signifie que la tâche est réussie en au plus `n` tentatives ; la valeur
est `null` lorsque le budget d'itérations ne permet pas ce nombre. Les validations cachées ne
sont exécutées qu'après une tentative publiquement réussie et leurs logs ne sont jamais inclus
dans le feedback envoyé au modèle.

### Patch

- files_modified
- expected_files_modified
- unnecessary_files_modified
- lines_added
- lines_removed
- diff_size

Lorsque la vérité terrain permet de définir les fichiers attendus :

- relevant_file_precision
- relevant_file_recall

## 3. Coût de génération

- input_tokens
- cached_input_tokens si exposé
- output_tokens
- reasoning tokens si exposés par le moteur/API et comparables
- number_of_model_calls
- total_model_time

## 4. Latence

- time_to_first_token / TTFT
- generation_duration
- end_to_end_duration
- per-iteration duration

## 5. Serving

- concurrent_users
- request_rate
- successful_requests
- failed_requests
- TTFT p50/p95
- total latency p50/p95
- TPOT/inter-token latency p50/p95
- output_tokens_per_second_per_request
- aggregate_tokens_per_second
- requests_per_second
- GPU memory used/peak
- host memory used/peak
- GPU utilization
- KV cache utilization, if available
- OOM count
- timeout count

## 6. OCR

- CER
- WER
- exact_field_accuracy
- numeric_field_accuracy
- date_field_accuracy
- identifier_field_accuracy
- JSON_validity
- schema_validity
- table_cell_accuracy
- missing_field_rate
- hallucinated_field_rate

Conserver également la précision par champ critique.

Le module `runner.document_metrics` calcule CER/WER par distance de Levenshtein
et conserve séparément `json_validity`, `schema_validity`, `exact_field_accuracy`,
les précisions numérique/date/identifiant/tableau, ainsi que les taux et noms de
champs manquants ou hallucinés. Une sortie JSON invalide ne doit pas être
transformée en zéro silencieux pour les autres dimensions.

## 7. Long contexte

- context_tokens
- success
- relevant_file_precision/recall
- unnecessary_edits
- TTFT
- time_to_success
- token_use

Le rapport principal doit montrer l'évolution de ces métriques en fonction de la taille de contexte.

`runner.context_dataset` conserve pour chaque variante la cible et le nombre réel
de tokens, la méthode (`tiktoken:<encoding>` ou `fallback:regex`), le seed et les
empreintes des fichiers. Le fallback est une estimation de comparaison, jamais
présenté comme le nombre exact du tokenizer du modèle. `score_relevant_files`
calcule séparément précision, rappel et fichiers inutiles à partir du diff brut.

## 8. Répétitions et statistiques

Qualité :

- conserver chaque run individuellement ;
- calculer success rate sur N runs ;
- afficher N explicitement.

Serving :

- warmup séparé ;
- médiane ;
- p95 ;
- éventuellement moyenne et écart-type, mais ne pas les utiliser seuls pour les latences.

## 9. Coût opérationnel

Lorsque le coût de location ou d'infrastructure est disponible :

### coût par heure

Conserver le prix réellement payé pour la campagne.

### coût par tâche réussie

```text
cost_per_success = total_compute_cost / successful_tasks
```

### coût par million de tokens

Peut être calculé, mais ne doit pas remplacer le coût par tâche réussie.

## 10. Comparabilité

Chaque rapport doit indiquer les dimensions qui diffèrent :

- hardware
- GPU count
- model
- revision
- quantization/dtype
- inference engine/version
- serving parameters
- context size
- benchmark/task revision

Une comparaison n'est dite « contrôlée » que si toutes les variables non étudiées sont identiques ou explicitement justifiées.
