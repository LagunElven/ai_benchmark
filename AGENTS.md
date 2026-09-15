# AGENTS.md — Enterprise LLM Benchmark

## Mission

Build a reproducible benchmark suite for evaluating local and hosted LLM configurations used as enterprise development assistants and document-analysis models.

The benchmark must allow repeated comparison across:

- GPU / accelerator hardware: NVIDIA H200, RTX PRO 6000 Blackwell, DGX Spark, and future platforms.
- LLM families and exact model revisions.
- Quantizations / numeric formats: BF16, FP16, FP8, Q8, Q6, Q4, NVFP4, etc. when applicable.
- Inference engines and versions: primarily vLLM, but architecture must not depend on one engine.
- Serving configurations: context length, concurrency, prefix caching, tensor/pipeline parallelism, batching, etc.

The project must distinguish **model quality**, **agentic repair capability**, **document/OCR capability**, and **serving performance**. Never collapse these into a single score without preserving the underlying metrics.

## Primary use case

The benchmark is intended to help choose hardware and models for an internal enterprise AI platform with a strong software-development focus.

Important development domains:

- Java 17/21
- Spring Boot / Spring Framework
- Hibernate / JPA
- Reactor
- Axon Framework / event sourcing / sagas / upcasters / projections
- TypeScript
- Angular
- Ionic / Capacitor
- Legacy languages: COBOL, Delphi/Object Pascal, WinDev/WLanguage, ABAL
- Document OCR and structured data extraction

RAG is explicitly out of scope for the first versions. Long-context repository understanding is in scope.

## Core principles

1. **Reproducibility first.**
   Every benchmark run must capture enough metadata to rerun it later.

2. **Change one variable when making scientific comparisons.**
   A benchmark result may also represent an operational solution comparison, but it must be labelled as such.

3. **Automated validation over LLM judging.**
   Prefer deterministic tests, compilers, linters, schemas, exact output comparisons, and generated ground truth.

4. **Hidden tests must remain hidden from the model.**
   Public tests may be visible. Private tests must be mounted or injected only during validation.

5. **Fresh workspace for every run.**
   No benchmark run may inherit code modifications from a previous run.

6. **Quality and performance are separate dimensions.**
   A fast wrong answer is not a good result; a high-quality answer can still be operationally too slow.

7. **Preserve raw results.**
   Never overwrite prior raw benchmark results. Derived reports must be reproducible from raw run data.

8. **Do not optimize tasks for a particular model.**
   Prompts and validation must stay model-neutral.

9. **Use realistic enterprise tasks rather than trivia.**
   Prefer multi-file debugging, implementation, refactoring, migration, concurrency and framework-specific problems.

10. **Avoid accidental benchmark leakage.**
    Do not publish hidden expected outputs in task prompts, comments, fixture names or Git history intended for benchmark execution.

## Repository target structure

Create and evolve the repository toward this layout:

```text
enterprise-llm-bench/
├── AGENTS.md
├── README.md
├── benchmark.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── BENCHMARK_PLAN.md
│   ├── METRICS.md
│   ├── TASK_AUTHORING.md
│   ├── EXECUTION_PROTOCOL.md
│   └── ROADMAP.md
├── schemas/
│   ├── task.schema.json
│   ├── run-result.schema.json
│   └── benchmark-config.schema.json
├── tasks/
│   ├── java/
│   ├── spring/
│   ├── axon/
│   ├── web/
│   │   ├── angular/
│   │   └── ionic/
│   ├── legacy/
│   │   ├── cobol/
│   │   ├── delphi/
│   │   ├── windev/
│   │   └── abal/
│   ├── documents/
│   ├── context/
│   └── e2e/
├── private-tests/
├── datasets/
├── runner/
├── serving/
├── scripts/
└── results/
    ├── raw/
    └── reports/
```

`private-tests/` must never be sent to an evaluated model.

## Initial benchmark scope

The target quality suite should eventually contain approximately:

- Java: 8 tasks
- Spring: 10 tasks
- Axon: 10 tasks
- Angular/Ionic: 10 tasks
- COBOL: 5 tasks
- Delphi: 4 tasks
- WinDev/WLanguage: 4 tasks
- ABAL: 4 tasks
- Documents/OCR: 10 tasks
- Long-context: 6 tasks
- End-to-end / multi-technology: 3 tasks

Target total: ~74 quality tasks, plus a separate serving-performance matrix.

Do not reduce scope merely to make implementation faster. Implement incrementally, while retaining the complete roadmap.

## Benchmark suites

Tasks can carry suite tags:

- `smoke`: fast environment/model validation
- `core`: regular comparison suite
- `full`: complete qualification suite

A smoke task should normally also be part of core and full.

## Required execution modes for coding tasks

### one-shot

1. Provide task instructions and allowed workspace.
2. Model produces or edits code.
3. Run validation once.
4. Store result.

### repair

1. Provide task instructions and allowed workspace.
2. Model edits code.
3. Run public/validation tests.
4. Return permitted compiler/test logs to model.
5. Allow repair.
6. Repeat up to configured maximum, initially 3 iterations.
7. Run hidden validation and store final result.

Record Pass@1, Pass@2 and Pass@3 when applicable.

## Task format

Each task should converge toward:

```text
tasks/<category>/<task-id>/
├── task.yaml
├── prompt.md
├── workspace/
├── public-tests/
├── fixtures/
├── expected-public/
└── README.md
```

Hidden validation belongs outside the model-visible task directory, preferably under:

```text
private-tests/<task-id>/
```

A task definition should describe at least:

- id
- name
- category
- difficulty
- suites/tags
- mode support (`one-shot`, `repair`)
- language/toolchain requirements
- internet policy
- context/document inputs
- maximum iterations
- output/token limits
- validation commands
- metric extractors
- timeouts

## Initial task catalogue

### Java

- JAVA-01 Null-safety / Streams / Optional
- JAVA-02 Dates, timezones and DST
- JAVA-03 Concurrent modification of a collection
- JAVA-04 Synchronization and thread-safety
- JAVA-05 Refactor a complex business method without changing behavior
- JAVA-06 Diagnose an intermittent race condition
- JAVA-07 Optimize an implementation without behavioral regression
- JAVA-08 Evolve an API while retaining backward compatibility

### Spring

- SPRING-01 REST controller + validation
- SPRING-02 Exception handling
- SPRING-03 Transaction rollback behavior
- SPRING-04 Hibernate dirty checking
- SPRING-05 Lost update + optimistic locking / `@Version`
- SPRING-06 `@DynamicUpdate` and concurrent updates
- SPRING-07 JPA N+1 diagnosis and correction
- SPRING-08 Reactor asynchronous retry
- SPRING-09 Security / Bearer / CSRF
- SPRING-10 Multi-service transactional bug

### Axon

- AXON-01 Basic event handler
- AXON-02 Event upcaster adding a field from an existing field
- AXON-03 Multi-revision upcaster chain
- AXON-04 Ignore obsolete snapshots only
- AXON-05 Saga association handling
- AXON-06 Multiple `@StartSaga` paths
- AXON-07 Idempotent projection
- AXON-08 Replay and projection rebuild
- AXON-09 Optimistic locking / error propagation / retry behavior
- AXON-10 Multi-aggregate diagnostic task

### Angular / Ionic

- WEB-01 `Observable<T>` versus `T`
- WEB-02 Subscription lifecycle and cleanup
- WEB-03 Search pipeline with RxJS `switchMap`
- WEB-04 HTTP interceptor
- WEB-05 Bearer + CSRF handling
- WEB-06 Complex reactive forms
- WEB-07 Signals / RxJS state management
- WEB-08 Ionic navigation
- WEB-09 OAuth/deep-link handling with Capacitor
- WEB-10 Cross-layer feature: API/service/component/template

### COBOL

- COBOL-01 Explain existing program behavior
- COBOL-02 Find and fix business logic bug
- COBOL-03 Sequential file + PIC / COMP-3 handling
- COBOL-04 Behavior-preserving modification
- COBOL-05 COBOL-to-Java migration with equivalent outputs

### Delphi

- DELPHI-01 Object Pascal comprehension
- DELPHI-02 Object lifecycle/resource management
- DELPHI-03 Correct business treatment
- DELPHI-04 Delphi-to-Java migration

### WinDev / WLanguage

- WL-01 WLanguage comprehension
- WL-02 HFSQL access logic
- WL-03 Correct business treatment
- WL-04 WLanguage-to-Java migration

### ABAL

ABAL here means **Advanced Business Application Language**, not SAP ABAP.

- ABAL-01 Explain an ABAL program
- ABAL-02 Modify an ABAL business rule
- ABAL-03 ABAL-to-Java migration with behavior checks
- ABAL-04 Documentation-assisted task using supplied ABAL/Open ABAL reference material

For rare-language tasks, distinguish:

- knowledge without supplied documentation
- ability to use supplied documentation effectively

### Documents / OCR

- DOC-01 Digital PDF/simple rendered document
- DOC-02 300 DPI scan
- DOC-03 150 DPI scan
- DOC-04 Rotated document
- DOC-05 Noisy/compressed document
- DOC-06 Table extraction
- DOC-07 Form extraction
- DOC-08 Multi-page document
- DOC-09 Mixed document types
- DOC-10 Complex structured JSON extraction

Ground truth should be generated or manually curated and versioned.

### Long context

Use the same underlying problem with increasing repository/context sizes when possible:

- CTX-01 ~10k tokens
- CTX-02 ~30k tokens
- CTX-03 ~60k tokens
- CTX-04 ~100k tokens
- CTX-05 ~150k tokens
- CTX-06 ~200k tokens

Measure whether the model can still locate and correctly modify the relevant files as distractor/context size increases.

### End-to-end

- E2E-01 Spring REST → DTO → Angular UI
- E2E-02 Angular → REST command → Axon aggregate/event → JPA projection
- E2E-03 Legacy program/rule → Java/Spring modernization

## OCR/document scoring

Prefer objective metrics:

- Character Error Rate (CER)
- Word Error Rate (WER)
- exact field accuracy
- numeric accuracy
- date accuracy
- JSON schema validity
- table cell accuracy
- missing field count/rate
- hallucinated field count/rate

Business-critical fields such as amount, dates, IBAN-like identifiers, references and currencies should be reported separately and may receive higher weighting in derived reports.

## Coding task scoring

Prefer raw components rather than a single opaque score.

Suggested components:

- hidden functional tests
- compilation/build success
- public tests
- regression tests
- static analysis / lint
- patch size / touched-file precision
- task completion iteration
- token use
- elapsed time

Human maintainability scoring may be added separately, but must not replace deterministic validation.

## Long-context metrics

In addition to task pass/fail, capture:

- context/input tokens
- files modified
- expected files modified
- unnecessary files modified
- relevant-file precision/recall when measurable
- time to first successful patch
- output tokens
- success rate by context size

## Serving benchmark matrix

Serving benchmarks are separate from quality tasks.

Initial concurrency levels:

- 1 user
- 2 users where useful
- 5 users
- 10 users

Initial context/input buckets:

- 8k
- 32k
- 64k
- 100k
- 200k when supported

Run both:

- `cold`: mostly distinct prefixes/contexts
- `shared-prefix`: common system prompt/repository prefix with different user requests

Capture at least:

- TTFT p50/p95
- tokens/s/user
- aggregate tokens/s
- inter-token latency or TPOT
- total latency p50/p95
- throughput / requests per second where meaningful
- GPU memory use
- KV-cache metrics when exposed
- GPU utilization
- CPU and host RAM use
- OOM/failure rate

When possible, also capture power/energy metrics.

## Run metadata

Every run record must include, when known:

- benchmark version / git commit
- task id
- task revision
- run id
- timestamp
- model name
- model exact revision/hash
- tokenizer revision
- quantization / dtype
- hardware model
- GPU count
- GPU memory
- driver version
- CUDA version
- inference engine and version
- command line / launch config
- tensor/pipeline parallel settings
- max model length
- prefix caching settings
- batch/concurrency settings
- temperature
- top-p/top-k when applicable
- seed when supported
- input tokens
- output tokens
- TTFT
- generation time
- total time
- validation outcome
- tests passed / total
- repair iterations
- tokens until success
- time until success
- raw logs/artifact references

## Comparison labels

Reports must distinguish at least:

### Controlled hardware comparison
Same model, revision, quantization/dtype, inference engine/config and benchmark inputs; only hardware differs.

### Controlled quantization comparison
Same hardware, model/revision, engine and benchmark inputs; quantization/dtype differs.

### Controlled model comparison
Same hardware and serving environment as far as practical; model differs.

### Operational solution comparison
Multiple variables may differ. Label clearly. Do not infer causality for one specific variable.

## Implementation guidance

- Prefer Python for orchestration unless a compelling reason exists otherwise.
- Keep model access behind an OpenAI-compatible client abstraction where practical.
- The runner must be able to execute against a remote OpenAI-compatible endpoint.
- Avoid coupling task definitions to vLLM internals.
- Use Docker/containers where useful for deterministic build/test environments.
- The initial codebase should run on a normal developer machine for task authoring and validation even before GPU infrastructure exists.
- Design result storage as JSON/JSONL first. CSV and dashboards are derived outputs.
- Validate YAML/JSON task configuration against schemas.
- Keep benchmark fixtures deterministic and small enough to version where licensing allows.

## Safety and isolation

- Disable internet for evaluated agents by default unless a task explicitly tests browsing/documentation lookup.
- Prevent evaluated agents from reading `private-tests/`, answer keys, result history or solution branches.
- Use filesystem/worktree/container isolation.
- Put time, token and command execution limits around every task.
- Treat model-generated shell commands as untrusted input.

## Development workflow for Codex

When implementing:

1. Read this file and relevant files in `docs/` first.
2. Prefer small, reviewable commits/changes.
3. Add tests for runner/schema behavior.
4. Do not create dozens of shallow benchmark tasks at once. Fully implement a few representative tasks first, establish the format, then scale.
5. When task requirements are underspecified, preserve extensibility rather than hardcoding assumptions.
6. Never silently change scoring or task semantics. Changes affecting comparability require a benchmark/task revision bump.
7. Keep a changelog of benchmark-semantic changes.
8. Do not fabricate ABAL syntax or proprietary WinDev behavior when authoring real tasks. Use documented/reference material or mark fixtures as synthetic/pseudocode until verified.

## Definition of done for Phase 1

Phase 1 is complete when:

- repository skeleton exists;
- configuration and result schemas exist;
- runner can discover tasks;
- runner can create a clean workspace;
- runner can call an OpenAI-compatible endpoint;
- runner supports one-shot and basic repair loops;
- runner executes validator commands safely;
- hidden tests are not model-visible;
- results are persisted as machine-readable JSON/JSONL;
- at least one representative task from Java, Spring, Axon, Angular/Ionic, legacy, documents and long-context categories is implemented or scaffolded with clear TODOs;
- a smoke suite can run end-to-end on a mock/fake model endpoint or deterministic test adapter.

Do not start GPU-specific optimization before this foundation is stable.
