# Architecture Decisions

## Modular monolith

The application keeps a single deployable backend while separating ingestion, embeddings, retrieval, generation, conversations, storage, and evaluation. This follows the project requirement to remain lightweight without unnecessary microservices.

## ChromaDB

ChromaDB provides persistent local vector storage and metadata filtering without requiring another infrastructure service.

## Local conversation persistence

Conversations are stored in a JSON file to satisfy the requirement for simple local persistence while avoiding an unnecessary database dependency.

## RAG grounding

The RAG service first retrieves chunks and then constructs a prompt that explicitly restricts answers to supplied context. When retrieval returns nothing above the threshold, the service refuses to answer from unsupported information.

## Citations

Every retrieved source carries document name, chunk source, excerpt, score, and optional page number. The LLM is instructed to use source markers matching the supplied source list.

## Evaluation

Retrieval metrics are computed from expected source documents. Answer relevance and faithfulness use lightweight heuristics in the included evaluator and are explicitly labeled as such. No benchmark result is hardcoded.

## Security

Uploaded filenames are sanitized, extensions and file sizes are validated, secrets are environment-based, and files are written under the configured upload directory.
