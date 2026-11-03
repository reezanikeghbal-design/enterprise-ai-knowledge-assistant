from __future__ import annotations

import ollama

from app.core.config import Settings
from app.core.exceptions import LLMError
from app.services.retrieval_service import RetrievalService


SYSTEM_PROMPT = """You are an enterprise knowledge assistant.
Answer only from the supplied context. If the context does not contain enough
information, say that the uploaded documents do not contain sufficient
information. Do not invent facts or citations.
When answering, use source markers such as [S1], [S2] that correspond only
to the supplied sources."""


class RAGService:
    def __init__(self, settings: Settings, retrieval: RetrievalService):
        self.settings = settings
        self.retrieval = retrieval

    def _prompt(self, question: str, sources: list[dict], history: list[dict]) -> str:
        context = "\n\n".join(
            f"[S{i}] {s['document_name']} | page={s['page']}\n{s['text']}"
            for i, s in enumerate(sources, 1)
        )
        history_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in history[-6:]
        )
        return f"""{SYSTEM_PROMPT}

Conversation:
{history_text}

Context:
{context}

Question:
{question}
"""

    def chat(self, question: str, history: list[dict] | None = None) -> dict:
        sources = self.retrieval.search(question)
        if not sources:
            return {
                "answer": "The uploaded documents do not contain sufficient information to answer this question.",
                "sources": [],
            }

        prompt = self._prompt(question, sources, history or [])
        try:
            client = ollama.Client(host=self.settings.ollama_base_url, timeout=self.settings.ollama_timeout_seconds)
            response = client.chat(
                model=self.settings.ollama_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            answer = response["message"]["content"].strip()
        except Exception as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc

        return {"answer": answer, "sources": sources}
