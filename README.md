# `rag-retrieval-eval`

## Why This Repository Exists

[rag-minimal-control](https://github.com/Arnav-Ajay/rag-minimal-control) established a **minimal RAG control system** and showed that, under strict evidence constraints, the model consistently refused to answer.

That refusal was *correct* — but **unexplained**.

This repository exists to answer a narrower and more fundamental question:

> **When a RAG system refuses to answer, is it because the answer is absent — or because retrieval failed?**

This is not an optimization repo.
It is a **retrieval observability and evaluation harness**.

---

## What Problem This System Solves

This system makes retrieval behavior:

* Observable
* Measurable
* Falsifiable

It allows a human to determine whether retrieval failures are due to:

* Corpus absence
* Representation collapse
* Lexical bias
* Ranking cutoff
* Similarity score pathologies

without changing the retrieval system itself.

---

## What This System Explicitly Does NOT Do

This implementation deliberately avoids:

* Changing embedding models
* Improving chunking strategies
* Retrieval reranking
* Semantic search
* LLM-based grading
* Answer correctness evaluation
* Any attempt to “fix” retrieval

If retrieval looks bad, that is the expected and desired outcome.

---

## System Relationship to rag-minimal-control

This repository is a **direct clone** of `rag-minimal-control` with:

* Identical corpus
* Identical chunking
* Identical embeddings
* Identical similarity metric
* Identical Top-K retrieval for generation

The **only difference** is the addition of retrieval observability.

`rag-minimal-control` answers:

> “Does the system behave correctly under constraint?”

`rag-retrieval-eval` answers:

> “Why does retrieval fail when answers exist?”

---

## System Overview

**Repo Contract:**

* Inputs: same static PDF corpus as `rag-minimal-control`
* Query input: deterministic evaluation questions
* Output:

  * Ranked retrieval results (Top-N for inspection)
  * Similarity scores
  * Human relevance labels (external)
* Non-goal: generating correct answers

---

## Retrieval Pipeline (Unchanged)

```
Document → Chunk → Embed → Retrieve → Rank → Top-K → Generate
```

**Important distinction:**

* **Top-K (K=4)** → passed to the LLM (unchanged)
* **Top-N (e.g., 20–50)** → logged for analysis only

---

## What Is Being Measured

This repository supports manual evaluation of:

* **Context Recall @ K**
* **Rank of First Relevant Chunk**
* **Retrieval Miss Rate**
* **False Similarity Signals**

All relevance judgments are made by a human.

No automated scoring is used.

---

## Expected Observations

This system is expected to show:

* High similarity scores for semantically irrelevant chunks
* Near-identical similarity values across many chunks
* Relevant chunks appearing far below Top-K
* Complete retrieval failure even when answers exist

These are not bugs.
They are **diagnostic signals**.

---

## Why This Matters

Most RAG systems fail silently.

By separating:

* **Retrieval failure**
* **Corpus absence**
* **Generation refusal**

this repository establishes a causal foundation for all future improvements.

No optimization is meaningful until failure is measured.

---

## How to Run

Same as `rag-minimal-control`.

- create a folder `data/` and add pdf files in it. (just 1 is fine)
- create a .env file in root dir and add you OpenAI API key ket as:
```
OPENAI_API_KEY=<your-api-key>

```
- simply run:

```bash
pip install -r requirements.txt
python app.py
```

Ensure retrieval logs are enabled.

## Text Normalization Note

PDF text extraction exhibited common mojibake artifacts
(e.g., mis-decoded dashes, arrows, and mathematical symbols).

These were corrected using deterministic Unicode normalization
and explicit glyph replacement. No semantic rewriting or
content alteration was performed.
