def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    items = retrieved[:k]
    return sum(x in relevant for x in items) / len(items) if items else 0.0


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return sum(x in relevant for x in retrieved[:k]) / len(relevant)


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for i, item in enumerate(retrieved, 1):
        if item in relevant:
            return 1.0 / i
    return 0.0
