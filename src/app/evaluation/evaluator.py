from pathlib import Path
import json
from app.evaluation.metrics import precision_at_k, recall_at_k, reciprocal_rank


class Evaluator:
    def __init__(self, retrieval_service, rag_service, dataset_path: str):
        self.retrieval = retrieval_service
        self.rag = rag_service
        self.dataset_path = Path(dataset_path)

    def run(self) -> dict:
        dataset = json.loads(self.dataset_path.read_text(encoding="utf-8"))
        p, r, mrr = [], [], []
        relevance, faithfulness, citation_accuracy = [], [], []

        for item in dataset:
            results = self.retrieval.search(item["question"], top_k=5, threshold=0.0)
            retrieved = [x["document_name"] for x in results]
            relevant = set(item["expected_sources"])
            p.append(precision_at_k(retrieved, relevant, 5))
            r.append(recall_at_k(retrieved, relevant, 5))
            mrr.append(reciprocal_rank(retrieved, relevant))

            response = self.rag.chat(item["question"])
            answer = response["answer"].lower()
            expected_terms = item.get("expected_answer_terms", [])
            relevance.append(
                sum(term.lower() in answer for term in expected_terms) / len(expected_terms)
                if expected_terms else 0.0
            )
            cited = response.get("sources", [])
            cited_names = {s["document_name"] for s in cited}
            faithfulness.append(1.0 if cited else 0.0)
            citation_accuracy.append(
                len(cited_names & relevant) / len(cited_names) if cited_names else 0.0
            )

        n = max(len(dataset), 1)
        return {
            "samples": len(dataset),
            "retrieval_precision_at_5": sum(p) / n,
            "retrieval_recall_at_5": sum(r) / n,
            "mrr": sum(mrr) / n,
            "answer_relevance_heuristic": sum(relevance) / n,
            "faithfulness_heuristic": sum(faithfulness) / n,
            "citation_accuracy": sum(citation_accuracy) / n,
            "note": "These are computed results from the included dataset, not fabricated benchmark values. Relevance and faithfulness are lightweight heuristics and should be human-verified.",
        }
