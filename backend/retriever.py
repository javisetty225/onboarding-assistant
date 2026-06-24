"""Semantic search over the Chroma collection."""

from dataclasses import dataclass

from . import config
from .ingest import get_collection


@dataclass
class RetrievedChunk:
    doc: str
    heading: str
    owner: str
    last_updated: str
    authority_rank: int
    text: str
    distance: float


# Build the collection (and load the embedding model) once per process instead
# of on every request — reconstructing it each call reloaded the model and was
# the bulk of the avoidable latency.
_COLLECTION = None


def _collection():
    global _COLLECTION
    if _COLLECTION is None:
        _COLLECTION = get_collection()
    return _COLLECTION


def retrieve(question: str, top_k: int = config.DEFAULT_TOP_K) -> list[RetrievedChunk]:
    res = _collection().query(query_texts=[question], n_results=top_k)

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    return [
        RetrievedChunk(
            doc=meta.get("doc", "unknown"),
            heading=meta.get("heading", ""),
            owner=meta.get("owner", "unknown"),
            last_updated=meta.get("last_updated", "unknown"),
            authority_rank=int(meta.get("authority_rank", config.DEFAULT_TIER)),
            text=text,
            distance=float(dist),
        )
        for text, meta, dist in zip(docs, metas, dists)
    ]