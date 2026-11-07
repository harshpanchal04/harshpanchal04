<!-- Generated parts: assets/*.svg and the upstream table are rebuilt by scripts/build_profile.py.
     Edit data/career.json or this file, not the SVGs. -->

<h1 align="center">Harsh Kumar Panchal</h1>

<p align="center">
  <b>Backend and data engineer.</b> At work I move data: CDC logs into Parquet, with Spark on Kubernetes.<br/>
  On my own I move bytes: a lock-free ring buffer in C++, concurrent object models in Java, a sharded cache in Go.<br/>
  <sub>Data Engineering Intern @ Fam · CS @ Scaler School of Technology · B.Sc. CS, BITS Pilani · Bengaluru</sub>
</p>

<p align="center">
  <a href="https://linkedin.com/in/harshpancha1"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
  <a href="https://ds-portfolio-lemon.vercel.app/"><img src="https://img.shields.io/badge/Portfolio-24292f?style=flat-square&logo=vercel&logoColor=white" alt="Portfolio" /></a>
  <a href="mailto:harshpanchal.space@gmail.com"><img src="https://img.shields.io/badge/Email-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email" /></a>
  <a href="https://drive.google.com/drive/folders/1r7QSJUW-qG1GwGQkx-1UNUZVw1DzK5b5?usp=sharing"><img src="https://img.shields.io/badge/Project%20demos-34A853?style=flat-square&logo=googledrive&logoColor=white" alt="Project demos" /></a>
</p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/trace-dark.svg">
  <img src="assets/trace-light.svg" width="100%" alt="My career drawn as a distributed trace: CS undergrad 2023 to 2027; Urban Company SDE intern 2024; Piramal big data intern 2024 to 2025; RagaAI data science intern 2025; side projects 2025 to 2026; Fam data engineering intern since October 2026, still running." />
</picture>

<sub>My career drawn as a distributed trace. At RagaAI I fixed a trace timeline that collapsed microsecond spans into one-second buckets, so this felt like the right format. The green span is still running.</sub>

## Now

At **Fam** I work on the data platform's move to a lakehouse (S3, Iceberg, Trino):

- a **Spark job on EKS**, run by Airflow, that compacts the CDC write-ahead log into one Parquet file per day. It keeps the latest event per key by LSN, checks data-quality invariants before every write, and gives the same output on a rerun.
- a **multi-user JupyterHub on Kubernetes** (Helm, Karpenter, Pulumi): one pod per analyst, JumpCloud login, and read-only Trino access where every query is tagged with the user's email.

## Measured, not claimed

<a href="https://github.com/harshpanchal04/Market-Data-System-HFT">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/latency-dark.svg">
  <img src="assets/latency-light.svg" width="100%" alt="Latency of one market-data tick over a lock-free shared-memory ring versus TCP with JSON, measured by CI" />
</picture>
</a>

<sub>Every Monday, CI clones <a href="https://github.com/harshpanchal04/Market-Data-System-HFT">Market-Data-System-HFT</a>, compiles it, runs <code>scripts/bench.sh</code> (a publisher and two subscribers on one runner) and redraws this card from the output. GitHub runners are shared VMs, so compare the two paths, not the absolute numbers.</sub>

## Claims, with receipts

| Claim | Where to check it |
|---|---|
| Lock-free single-producer/single-consumer ring buffer, read and write indices on separate cache lines | [`spsc_queue.hpp`](https://github.com/harshpanchal04/Market-Data-System-HFT/blob/main/include/core/spsc_queue.hpp) |
| Nearest-rank latency percentiles on `CLOCK_MONOTONIC`, plus a regression test for a shared-memory bug I shipped and then fixed | [`latency_recorder.hpp`](https://github.com/harshpanchal04/Market-Data-System-HFT/blob/main/include/util/latency_recorder.hpp) · [`test_tick_data.cpp`](https://github.com/harshpanchal04/Market-Data-System-HFT/blob/main/tests/test_tick_data.cpp) |
| Sharded in-memory cache with TTL, eviction under a memory cap, Prometheus metrics (Go) | [`key_value_cache.go`](https://github.com/harshpanchal04/key-value-cache/blob/main/key_value_cache.go) |
| Idempotency keys and atomic stock decrement on order placement | [`app.py`](https://github.com/harshpanchal04/inventory-order-service/blob/main/app.py) · [`DECISIONS.md`](https://github.com/harshpanchal04/inventory-order-service/blob/main/DECISIONS.md) |
| Parking lot with 6 GoF patterns and zero class inheritance; its race condition is written up | [`LLD-Parking-Lot`](https://github.com/harshpanchal04/LLD-Parking-Lot#thread-safety-analysis) |
| 10-stage CI: Flake8, CodeQL, OWASP Dependency-Check, pytest, Docker smoke test, Trivy | [`ci.yml`](https://github.com/harshpanchal04/ReserveX/blob/main/.github/workflows/ci.yml) |
| Offline Ed25519 signature checks with 30-second rotating QR challenges | [`crypto-utils`](https://github.com/harshpanchal04/AuthX/blob/main/packages/crypto-utils/src/index.ts) |
| Hybrid BM25 + dense retrieval fused with Reciprocal Rank Fusion (k = 60) | [`search.py`](https://github.com/harshpanchal04/Organizational-Reasoning-Engine/blob/main/src/retrieval/search.py) |

## Projects

| | Project | The interesting part |
|:-:|---|---|
| ⚡ | **[Market-Data-System-HFT](https://github.com/harshpanchal04/Market-Data-System-HFT)**<br/><sub>C++17 · POSIX shm · Boost.Asio</sub> | The same tick goes over a lock-free ring in shared memory and over TCP + JSON, and both are timed on one clock. Measuring it exposed two bugs of mine: a read-only mapping the consumer wrote to, and a cached clock that was only accurate to 1 ms. |
| 🗃️ | **[key-value-cache](https://github.com/harshpanchal04/key-value-cache)**<br/><sub>Go · Prometheus</sub> | Sharded map to cut lock contention, TTL expiry, and eviction once a memory cap is hit |
| 🧩 | **[LLD in Java](https://github.com/harshpanchal04/LLD-Parking-Lot)**<br/><sub>Java 11 · GoF · SOLID</sub> | Parking lot, [ATM](https://github.com/harshpanchal04/LLD-ATM-Solution) and [Snake & Ladder](https://github.com/harshpanchal04/Snake-Ladder-): strategies you can swap at runtime, a State-pattern slot lifecycle, `AtomicLong` ticket IDs |
| 🚆 | **[ReserveX](https://github.com/harshpanchal04/ReserveX)**<br/><sub>Python · K3s · AWS EC2</sub> | Greedy interval stitching that chains partial seat vacancies into full journeys, shipped through a 10-stage CI pipeline and CD to K3s |
| 📊 | **[Impactra](https://impactra.vercel.app/)**<br/><sub>Node.js · Redis · BullMQ · Postgres</sub> | Queue-backed workers that score PR diffs, with Postgres caching to stay under GitHub and LLM rate limits; ranked 1,200+ student profiles at Chitkara University |
| 🔐 | **[AuthX](https://github.com/harshpanchal04/AuthX)**<br/><sub>TypeScript · Ed25519</sub> | The guard app verifies signed, rotating QR codes with no network, so entry works when the Wi-Fi doesn't |
| 🧠 | **[TrustLoop](https://github.com/harshpanchal04/TrustLoop)** · **[Org Reasoning Engine](https://github.com/harshpanchal04/Organizational-Reasoning-Engine)**<br/><sub>LangGraph · retrieval</sub> | Agents that route low-confidence answers to a human, and learn from expert feedback without fine-tuning |

<details>
<summary><b>How two of these work (click to expand)</b></summary>
<br/>

**Market data: one tick, two transports**

```mermaid
flowchart LR
    P[publisher<br/>pinned to core 0] -->|stamp CLOCK_MONOTONIC| R[(SPSC ring<br/>POSIX shm, 64-byte slots)]
    P -->|to_json + TCP_NODELAY| T[[TCP :8800]]
    R -->|busy-poll pop| S[shm subscriber<br/>core 1]
    T -->|read_until newline| C[tcp subscriber]
    S & C --> L[latency recorder<br/>p50 / p99 / p99.9]
```

Bugs I found by measuring it: the consumer mapped the segment `PROT_READ` but `pop()` writes the read index, so the first message crashed it. The cached clock refreshed every 1 ms, so per-message latencies were noise. A subscriber that slept after 1,000 empty polls added the OS wake-up time to every tick. Each fix has a test or a benchmark that shows it.

**CDC log compaction (the pattern, at work)**

```mermaid
flowchart LR
    W[(CDC write-ahead log<br/>many small Parquet files per day)] --> D[Spark on EKS<br/>latest event per key by LSN]
    D --> Q{data-quality gates<br/>no key lost · 1 row per key · latest wins}
    Q -- pass --> O[(1 Parquet file per day)]
    Q -- fail --> X[job fails, nothing written]
```

De-duplicate within a day, never across days: a key that changed on two days has to appear in both day folders, or the incremental job for the earlier day misses the change.
</details>

## Upstream

<!-- upstream:start -->
| merged | repo | pull request |
|---|---|---|
| 2026-08-13 | `freeCodeCamp-Summer-Cohort-2026/datalens` | [#31 feat: add --verbose flag to datalens clean command](https://github.com/freeCodeCamp-Summer-Cohort-2026/datalens/pull/31) |
| 2025-04-17 | `aristotle-ai/RagaAI-Catalyst` | [#128 Create Quickstart.md](https://github.com/aristotle-ai/RagaAI-Catalyst/pull/128) |
| 2024-09-26 | `Vishesh-Paliwal/Shatranj` | [#5 Implemented Queen Piece moveTo method](https://github.com/Vishesh-Paliwal/Shatranj/pull/5) |
<!-- upstream:end -->

<sub>My RagaAI internship work on <a href="https://github.com/raga-ai-hub/RagaAI-Catalyst">RagaAI Catalyst</a> (16K★): the test infrastructure and the integrations for 7 agent frameworks were merged through team branches, so it isn't listed under my name.</sub>

## Toolbox

<p>
  <img src="https://skillicons.dev/icons?i=java,python,cpp,go,ts,nodejs,spring,fastapi,postgres,redis,mongodb,aws,kubernetes,docker,githubactions,linux&perline=16" alt="Java, Python, C++, Go, TypeScript, Node.js, Spring, FastAPI, PostgreSQL, Redis, MongoDB, AWS, Kubernetes, Docker, GitHub Actions, Linux" />
</p>

<sub>Data: Apache Spark · Airflow · Trino · Iceberg · Parquet · Snowflake. Infra: EKS · Helm · Karpenter · Pulumi.</sub>

---

<sub>This page rebuilds itself every Monday. <a href=".github/workflows/profile.yml"><code>profile.yml</code></a> compiles and benchmarks my C++ project on the runner, then <a href="scripts/build_profile.py"><code>build_profile.py</code></a> (standard-library Python) redraws the trace and latency cards and refreshes the upstream list from the GitHub API.</sub>
