# Tulia AI Enablement: Arwin Responsibilities and RAG Plan

## Goals
- Add a pragmatic Retrieval-Augmented Generation (RAG) layer to Tulia.
- Provide lesson assistance, Q&A, and rubric-aligned coaching with citations.

## Responsibilities (Arwin)
- Implement content ingestion and vector index build.
- Expose minimal APIs: `/api/rag/query`, `/api/rag/lesson_help`.
- Add lesson-runner help widget with citations.
- Ship evaluation harness (golden set, scores, logs).
- Add privacy, rate limits, and cost controls.

## Architecture (v1)
- Sources: Lessons, Exercises, ContentBlocks, Milestone rubrics, tip sheets.
- Chunking: 300–500 tokens, 50 overlap; metadata for level/unit/lesson.
- Embeddings: `text-embedding-3-small` (fallback: `all-MiniLM-L6-v2`).
- Vector store: FAISS (upgrade path: Chroma/PGVector).
- Retrieval: top-k=6 with MMR; optional filters by level/unit.
- Generation: `gpt-4o-mini` with strict "answer-from-context" system prompt.
- Caching: semantic cache via embeddings; TTL 15–60m.
- Observability: structured logs (prompt, citations, cost, latency, user hash).

## Django Integration
- Management command: `build_rag_index` to ingest and index.
- Endpoints:
  - POST `/api/rag/query` → { query, scope?, level?, unit?, lesson? } → { answer, citations[] }
  - POST `/api/rag/lesson_help` → lesson hints with citations
- UI: help widget on `templates/myApp/lesson_runner.html` with “Explain this” and “Give a hint”.

## Security & Safety
- Strip PII, do not log raw user text/audio by default.
- Refuse out-of-scope requests; rate limit (e.g., 20/day, 5/min burst).
- Timeouts + retries; exponential backoff.

## Evaluation
- Golden set: 50–100 Q&A from Level 1.
- Metrics: precision@k, faithfulness, refusal accuracy, latency, cost.
- Weekly regression; store in SQLite + simple admin chart.

## Cost Controls
- Batch embeddings on ingestion; use small models; cache answers.
- Stream responses; cap tokens per session.

## Deliverables (v1)
1. `build_rag_index` command.
2. FAISS store + retriever utils.
3. `/api/rag/query` and `/api/rag/lesson_help` endpoints.
4. Lesson help widget with citations.
5. Eval harness + seed golden set.

## Two-Week Sprint
- Week 1
  - D1–2: Ingestion + index build command.
  - D3–4: Vector store + retriever with filters/MMR.
  - D5: `/api/rag/query` + structured logging.
- Week 2
  - D6–7: `/api/rag/lesson_help` + UI hook on lesson runner.
  - D8: Eval harness and baseline run.
  - D9: Rate limiting, caching, admin toggles.
  - D10: Hardening, docs, demo.

## Access & Env Checklist
- Keys: OpenAI (or local alt), optional reranker.
- Deps: `faiss-cpu`, `numpy`, `pydantic`, `httpx`, `tiktoken`.
- Settings: vector path, chunk sizes, rate limits.

## Runbook (local)
- Build index: `python manage.py build_rag_index`
- Run server: `python manage.py runserver`
- Query: POST `/api/rag/query` with JSON body `{ "query": "What is the RICE framework?", "level": 1 }`

