# `rag-retrieval-eval`

## Why This Repository Exists

The preceding repository, [`rag-minimal-control`](https://github.com/Arnav-Ajay/rag-minimal-control), established a baseline behavior:

> Under strict evidence constraints, a minimal RAG system may consistently refuse to answer.

That refusal behavior is correct by design, but it leaves an open empirical question:

> **When the system refuses to answer, is the answer absent from the corpus — or present but not surfaced by retrieval?**

This repository exists to **measure retrieval behavior directly**, without changing any retrieval or generation components.

This is not an optimization repository.
It is a **retrieval observability and failure measurement harness**.

---

## What Problem This System Examines

Baseline RAG systems typically expose only a single outcome: an answer or a refusal.

They do not make observable whether failure arises from:

* absence of relevant information
* retrieval miss
* ranking depth effects
* or generation starvation

This repository isolates **retrieval behavior** and makes it:

* observable
* inspectable
* auditable

without modifying the underlying system.

---

## Experimental Setup

All system components are inherited unchanged from `rag-minimal-control`:

* Static PDF corpus
* Fixed chunking strategy
* Dense embedding model
* Cosine similarity retrieval
* Top-K passed to the LLM fixed at **K = 4**

The only addition is **retrieval logging and human-grounded evaluation**.

---

## Evaluation Corpus

The corpus consists of three canonical research papers:

* *Attention Is All You Need*
* *Large Language Models Are Few-Shot Learners*
* *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*

These documents are the **only knowledge source** available to the system.

The corpus is intentionally small and fixed so that observed failures can be attributed to **retrieval behavior**, not data scale.

---

## Evaluation Methodology

* **54 hand-authored evaluation questions**
* Each question paired with a **human-identified gold (answer-bearing) chunk**
* No automated relevance inference
* No LLM-based grading

Retrieval results are inspected at multiple depths:

* **Top-K (K = 4)** — passed to the generator
* **Inspect-20** — logged for diagnosis
* **Inspect-50** — logged for diagnosis

Only retrieval behavior is evaluated.
Answer correctness is not measured.

---

## Observed Results

### Top-K Retrieval (K = 4)

* **0 / 54 questions** retrieve the gold chunk in Top-4
* As a result, **generation is always starved of answer-bearing context**

This outcome is consistent across all questions and intents.

---

### Deeper Inspection (Inspect-20 vs Inspect-50)

| Metric                              | Inspect-20 | Inspect-50 |
| ----------------------------------- | ---------- | ---------- |
| Questions with gold chunk retrieved | 4 / 54     | 7 / 54     |
| Median rank (when retrieved)        | ~18–20     | ~19        |
| Gold chunks within Top-4            | 0          | 0          |

Increasing inspection depth from **20 to 50** recovers **three additional gold chunks**, all ranked well outside the generation window.

This indicates that deeper inspection yields **limited recovery** and does not change generation-time behavior.

---

### Rank Distribution Characteristics

When gold chunks are retrieved:

* They typically appear **far below Top-K**
* Median rank remains close to **~18–20**
* Most questions either:

  * never retrieve the gold chunk
  * or retrieve it at non-actionable depths

This pattern is consistent across both inspection depths.

---

### Retrieval Performance by Question Intent

Retrieval results were stratified by question intent.

Observed outcomes:

* No intent category achieves meaningful Top-K inclusion
* Some intents exhibit slightly higher deep-inspection recovery
* Differences are small and do not materially affect generation starvation

Under this setup, **intent stratification does not mitigate Top-K retrieval failure**.

---

## What This Repository Does *Not* Claim

This repository does **not** claim that:

* dense retrieval always fails in general
* ranking failure is universal across RAG systems
* embeddings are the sole cause of failure
* deeper cutoffs cannot ever be effective
* intent never matters in other setups

All observations are scoped strictly to **this system configuration**.

---

## Interpretation (Evidence-Bounded)

The results show that:

* Answer-bearing chunks often exist in the corpus
* They are rarely surfaced at generation-critical depths
* Increasing inspection depth yields diminishing returns
* Generation refusal is explained by **retrieval starvation**, not corpus absence

These observations are **consistent with a retrieval ranking failure**, rather than a simple cutoff effect, within this baseline system.

---

## Why This Matters

Before improving retrieval, reranking, chunking, or generation, it is necessary to establish:

* whether evidence exists
* whether retrieval surfaces it
* where in the ranking it appears

This repository provides that measurement.

It establishes a concrete diagnostic baseline against which future retrieval improvements can be evaluated.

---

## Relationship to Later Repositories

This repository sits between:

* **[`rag-minimal-control`](https://github.com/Arnav-Ajay/rag-minimal-control)**
  Establishes strict, retrieval-conditioned generation behavior

* **[`rag-hybrid-retrieval`](https://github.com/Arnav-Ajay/rag-hybrid-retrieval)**
  Tests whether sparse signals can surface evidence missed here

All future improvements are evaluated **relative to this observed failure baseline**.

---

### Design Principle

> **No claim in this repository exists without a corresponding artifact in `data/`.**

All results are derived directly from logged retrieval outputs and human-grounded labels.

---