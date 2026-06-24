"""Load the docs, extract metadata, chunk by section, and index into Chroma."""

import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from . import config

META_RE = re.compile(
    r"Last updated:\s*(?P<date>\d{4}-\d{2}-\d{2}).*?Owner:\s*(?P<owner>[^_\n·]+)",
    re.IGNORECASE | re.DOTALL,
)
# Optional self-declared authority, e.g. "... · Authority: 1 ..." in the header.
AUTH_RE = re.compile(r"Authority:\s*(?P<rank>\d+)", re.IGNORECASE)


def parse_metadata(text: str) -> tuple[str | None, str | None, int | None]:
    m = META_RE.search(text)
    if not m:
        return None, None, None
    date = m.group("date").strip()
    owner = m.group("owner").strip().rstrip("_").strip()
    a = AUTH_RE.search(text[: m.end() + 80])  # only trust it near the header
    declared = int(a.group("rank")) if a else None
    return date, owner, declared


def split_sections(text: str) -> list[tuple[str, str]]:
    # Split on H2 headings so each procedure stays in one chunk.
    parts = re.split(r"\n(?=##\s)", text)
    chunks: list[tuple[str, str]] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r"#+\s*(.+)", part)
        heading = m.group(1).strip() if m else "Overview"
        if len(part) <= config.CHUNK_MAX_CHARS:
            chunks.append((heading, part))
        else:
            step = config.CHUNK_MAX_CHARS - config.CHUNK_OVERLAP_CHARS
            for i in range(0, len(part), step):
                chunks.append((heading, part[i : i + config.CHUNK_MAX_CHARS]))
    return chunks


def get_collection(reset: bool = False):
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBED_MODEL
    )
    if reset:
        try:
            client.delete_collection(config.COLLECTION_NAME)
        except Exception:
            pass
    return client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )


def build_index(docs_dir: Path | None = None) -> int:
    docs_dir = docs_dir or config.DOCS_DIR
    collection = get_collection(reset=True)

    ids, documents, metadatas = [], [], []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        last_updated, owner, declared = parse_metadata(text)
        rank = config.authority_for(path.name, declared)
        for idx, (heading, body) in enumerate(split_sections(text)):
            ids.append(f"{path.name}::{idx}")
            documents.append(body)
            metadatas.append(
                {
                    "doc": path.name,
                    "heading": heading,
                    "owner": owner or "unknown",
                    "last_updated": last_updated or "unknown",
                    "authority_rank": rank,
                }
            )

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return len(ids)


if __name__ == "__main__":
    n = build_index()
    print(f"Indexed {n} chunks into '{config.COLLECTION_NAME}'")