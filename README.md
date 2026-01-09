# `rag-retrieval-eval`

## Why This Repository Exists

The preceding repository,
[`rag-minimal-control`](https://github.com/Arnav-Ajay/rag-minimal-control), established a critical baseline:

> A minimal RAG system can behave *correctly* and still refuse to answer.

That refusal was **expected and correct** under strict evidence constraints —
but it left an essential question unanswered:

> **When a RAG system refuses to answer, is it because the answer is absent — or because retrieval failed to surface it?**

This repository exists to answer **only that question**.

This is not an optimization repository.
It is a **retrieval observability and failure measurement harness**.

---

## What Problem This System Solves

Most RAG systems fail silently.

They do not distinguish between:

* missing information
* retrieval failure
* ranking collapse
* generation refusal

This repository makes retrieval behavior:

* **Observable**
* **Measurable**
* **Falsifiable**

without changing the underlying retrieval or generation system.

---

## What This Repository Demonstrates (Empirically)

Using a fixed corpus and **54 human-grounded evaluation questions** spanning three canonical research papers, this repository establishes a hard result:

> **Dense retrieval fails catastrophically even when the answer-bearing chunk exists in the corpus.**

This failure persists even when inspecting retrieval results as deep as **Top-50**.

---

## Core Findings (Week-2 Final Results)

### Top-K for Generation (K = 4)

* **0 / 54 questions** retrieve the gold chunk in Top-4
* **100% generation starvation** despite corpus completeness

---

### Inspect-20 vs Inspect-50

| Metric                              | Inspect-20    | Inspect-50    |
| ----------------------------------- | ------------- | ------------- |
| Questions with gold chunk retrieved | 4 / 54        | 7 / 54        |
| Median rank (when retrieved)        | ~18–20        | ~19           |
| % questions with rank > 4           | ~92%          | ~90%          |
| Questions never retrieved           | Vast majority | Vast majority |

**Key observation**

Increasing inspection depth from **20 → 50** recovers only **3 additional questions**, all still far outside Top-K.

This is **not a cutoff artifact**.
It is a **ranking failure**.

---

## What This System Explicitly Does NOT Do

This repository deliberately avoids:

* Changing embedding models
* Improving chunking strategies
* Retrieval reranking
* Hybrid / lexical search
* Query rewriting
* LLM-based grading
* Answer correctness evaluation
* Any attempt to “fix” retrieval

If retrieval looks bad, that is **expected and desired**.

This repository exists to **measure failure**, not correct it.

---

## System Relationship to Other Repositories

This repository sits **between** two others in the series:

* [`rag-minimal-control`](https://github.com/Arnav-Ajay/rag-minimal-control)
  Establishes a strict, retrieval-conditioned control system

* [`rag-hybrid-retrieval`](https://github.com/Arnav-Ajay/rag-hybrid-retrieval)
  Tests whether sparse signals can surface evidence that dense retrieval misses

All components inherited from `rag-minimal-control` remain **unchanged**:

* Corpus
* Chunking
* Embeddings
* Similarity metric
* Top-K passed to the LLM (**K = 4**)

The **only addition** is retrieval observability and human-grounded evaluation.

---

## Retrieval Pipeline (Unchanged)

```
Document → Chunk → Embed → Retrieve → Rank → Top-K → Generate
```

**Important distinction**

* **Top-K (K = 4)** → passed to the LLM (unchanged)
* **Top-N (20 / 50)** → logged strictly for diagnosis

---

## Evaluation Methodology

This repository performs **human-grounded retrieval evaluation**.

Measured signals include:

* Rank of first relevant chunk
* Retrieval miss rate
* False similarity dominance
* Ranking depth collapse

No automated grading is used.
No relevance is inferred.
All gold labels are human-assigned.

---

## Data Directory Structure

All inputs, ground truth artifacts, and evaluation outputs are stored under a single versioned `data/` directory.

Data artifacts are treated as **first-class evaluation objects**, not transient logs.

```
data/
├── input_pdfs/
├── chunks_and_questions/
└── results_and_summaries/
```

---

### `data/input_pdfs/`

Static source corpus used for all experiments.

Includes **three canonical research papers**:

* *Attention Is All You Need*
* *Large Language Models Are Few-Shot Learners*
* *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*

These PDFs are the **only knowledge source** available to the system.

The corpus is intentionally small and fixed to ensure failures are attributable to **retrieval behavior**, not data scale.

---

### `data/chunks_and_questions/`

Ground-truth construction artifacts.

* `chunks_output.csv`

  * Exported chunk-level view of the corpus
  * Includes chunk IDs and document IDs
  * Used to manually identify **gold (answer-bearing) chunks**

* `question_input.csv`

  * Hand-authored evaluation questions
  * Each question is paired with a human-identified gold chunk
  * Questions are natural-language and retrieval-faithful

This directory defines the **evaluation contract**.
Questions and gold labels are fixed.
No automated relevance inference is performed.

---

### `data/results_and_summaries/`

Primary outputs of the repository.

* `questions_retrieval_results_inspect_20.csv`

* `questions_retrieval_results_inspect_50.csv`

  * Ranked retrieval results at two inspection depths
  * Top-K for generation remains fixed at **K = 4**

* `summary_overall.csv`

  * Aggregate retrieval metrics
  * Median rank, miss rates, Top-K failure rates

* `summary_by_intent.csv`

  * Retrieval performance stratified by question intent
  * Used to test whether intent mitigates ranking failure

All claims in this README are derived directly from these files.

---

## Design Principle

> **Nothing in `data/` is ephemeral.**

Every artifact exists to support:

* reproducibility
* human auditability
* causal reasoning about retrieval failure

No artifact is overwritten, sampled, or silently discarded.

---

## Why This Repository Matters

This repository establishes a non-negotiable baseline:

> **The dominant failure mode in baseline RAG systems is retrieval ranking collapse — not generation, not corpus absence, and not refusal logic.**

This causal diagnosis is a prerequisite for:

* hybrid retrieval
* reranking
* chunking strategy research
* agentic retrieval systems

No optimization is meaningful until this failure is measured.

This repository measures it — conclusively.

---