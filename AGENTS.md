# AGENTS.md — Enterprise LLM Benchmark

## Mission

Maintain a reproducible, model-neutral benchmark for enterprise coding assistants,
document/OCR extraction, agentic repair and serving performance. Preserve the separate
metrics for each dimension. RAG is out of scope for the current benchmark; long-context
repository work is in scope.

The quality catalogue targets 74 tasks across Java, Spring, Axon, Web, legacy languages,
documents, long context and end-to-end scenarios. The current inventory and implementation
status live in `docs/CATALOGUE.md`; do not duplicate the task list here.

## Source of truth

Use the focused document for the work at hand:

- Current milestone status and backlog: `docs/ROADMAP.md`.
- Implemented tasks and their status: `docs/CATALOGUE.md` and `docs/TASK_REFERENCE.md`.
- Task design, format and revisions: `docs/TASK_AUTHORING.md`.
- Runner boundaries and security: `docs/ARCHITECTURE.md` and `docs/EXECUTION_PROTOCOL.md`.
- Quality, OCR, context and serving metrics: `docs/METRICS.md`, `docs/DOCUMENTS.md`,
  `docs/CONTEXT.md` and `docs/SERVING.md`.
- Executed campaigns and their limits: `docs/CAMPAIGN_MATRIX.md` and the dated session
  reports under `docs/GPU_SESSION_*.md`.
- Planned GPU comparisons and setup: `docs/GPU_CAMPAIGN_PLAN.md` and
  `campaigns/gpu/plan.yaml`.
- Changes that affect benchmark comparability: `docs/CHANGELOG.md`.

When status differs between documents, treat the roadmap as the current backlog, the
campaign matrix/session reports as evidence for completed runs, and task definitions plus
schemas as the execution contract. Update the relevant source of truth instead of copying
the same mutable status into several documents.

## Non-negotiable benchmark rules

1. Capture enough model, tokenizer, hardware, engine, configuration and run metadata to
   reproduce each result.
2. Change one variable for a controlled comparison. Label multi-variable comparisons as
   operational and do not attribute their results to one variable.
3. Keep quality and performance dimensions separate; preserve raw metrics beneath any
   derived score.
4. Prefer deterministic validation over LLM judging.
5. Give every run a fresh workspace. Never overwrite raw results; derive reports from the
   preserved run artifacts.
6. Keep prompts and validators model-neutral. Do not tune tasks to a specific model under
   evaluation.
7. Keep hidden tests, answer keys and historical results out of model-visible prompts and
   workspaces. Inject hidden tests only into the validator workspace.
8. Disable internet for evaluated models unless the task explicitly measures browsing or
   documentation use.

## Contribution workflow

1. Read this file, `README.md`, the current roadmap and the focused design document before
   changing a subsystem.
2. Inspect the worktree first and preserve unrelated or pre-existing changes.
3. Make the smallest change that fully addresses the request. Keep generated campaign
   outputs and local `results/` artifacts intact.
4. Run focused validation for code or schema changes. For runner-wide changes, use the
   documented test and lint commands in `README.md`; for task changes, also validate the
   catalogue and the affected task.
5. If a change can alter task behavior, scoring, prompts, fixtures, validation or comparison
   semantics, increment the relevant task revision or benchmark version and record the
   semantic change in `docs/CHANGELOG.md`. Documentation-only edits do not need a semantic
   changelog entry.
6. Do not start a paid or remote GPU campaign unless the user asks for that execution.

## Task authoring and legacy fixtures

Follow `docs/TASK_AUTHORING.md` and `schemas/task.schema.json`. A task should have a clear
behavioral objective, deterministic validation and versioned inputs. Keep task-visible
files under `tasks/<category>/<task-id>/`; hidden validation belongs under
`private-tests/<task-id>/` and must never be copied to a model workspace.

Do not fabricate production syntax or behavior for ABAL or proprietary WinDev/WLanguage.
Use verified references or label a fixture as synthetic/pseudocode. Keep the distinction
between ABAL and SAP ABAP explicit. For rare toolchains, document whether validation is
native or uses a verified equivalent-output harness.

## Safety and execution boundaries

- Treat model-generated shell commands as untrusted input.
- Keep validation commands bounded by the task workspace and configured timeout; do not
  silently grant network or host access.
- Preserve the distinction between model-visible and validator-visible files.
- Never publish hidden expected outputs in prompts, comments, fixture names or benchmark
  execution history.
- Do not infer remote GPU memory or utilization from measurements collected on the local
  runner host; record unavailable metrics as unavailable.
