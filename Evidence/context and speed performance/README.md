# Search Performance Evaluation: ChromaDB vs. Markdown vs. PDF

This document outlines the results of an experiment comparing the performance of different knowledge sources for information retrieval.

## Experimental Setup

The experiment was conducted using the following tools:

*   **Large Language Model (LLM):** `ollama gpt-oss:120b-cloud`
*   **Orchestration/Search Invocation:** Gemini (free version)
*   **Embedding Model (for ChromaDB):** `all-minilm-l6-v2` (default)

Two modes were tested, representing different underlying models used by the orchestrator:
*   **PRO:** Standard, high-performance model.
*   **AUTO:** Cheaper, more lightweight models (`gemini-flash`, `flash-lite`).

## Knowledge Sources Compared

1.  **ChromaDB:** A persistent vector database.
2.  **Markdown (MD):** Plain text `.md` files.
3.  **PDF:** Raw `.pdf` document files.

---

## Performance Analysis & Results

### 1. ChromaDB

*   **Speed:**
    *   **PRO:** ~1m 32s
    *   **AUTO:** ~1m 27s
*   **Context Usage:** Lowest among the three sources.
*   **Workflow:** Requires an initial data ingestion step to create the vector store.
*   **Notes & Cost-Effectiveness:**
    *   Performance between the PRO and AUTO modes was nearly identical, making it highly cost-effective when using cheaper models.
    *   The result quality could potentially be improved by experimenting with different embedding models.

### 2. Markdown (MD) Files

*   **Speed:**
    *   **PRO:** ~1m 21s (Slightly faster than ChromaDB)
    *   **AUTO:** ~2m 10s
*   **Context Usage:** Highest among the three sources.
*   **Workflow:** Requires documents to be converted from their original format (e.g., PDF, Word) to Markdown. This adds manual overhead and requires verification of the conversion quality.
*   **Notes & Cost-Effectiveness:**
    *   While fast in PRO mode, the reliance on a mix of models in AUTO mode makes it less cost-efficient compared to the consistent performance of ChromaDB.

### 3. PDF Files

*   **Speed:**
    *   **PRO:** ~6m 51s
    *   **AUTO:** ~8m 19s
*   **Context Usage:** Medium (between ChromaDB and Markdown).
*   **Workflow:** Simplest workflow; requires no pre-processing other than storing the files.
*   **Notes & Cost-Effectiveness:**
    *   This method is **significantly slower** (5-6 times) than the others, making it impractical for time-sensitive tasks.
    *   Even though the AUTO mode uses cheaper models, the extreme performance penalty outweighs the cost savings.

---

## Conclusion

Based on the results, **ChromaDB offers the best overall balance** of performance, cost-effectiveness, and efficient context usage. While it requires an initial ingestion step, its consistent speed across different model tiers makes it a reliable and scalable choice.

*   **Markdown** is a viable alternative if the document conversion overhead is manageable.
*   **Direct PDF search** is not recommended due to its exceptionally poor performance.
