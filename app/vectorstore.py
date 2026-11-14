"""
Vector store module for HealthLabelCheck
Indexes all chunks into a persistent Chroma collection.
Adds GET /search/semantic?q= to the FastAPI app.
"""

import os
from typing import List, Dict

import chromadb
from chromadb.utils import embedding_functions

from app.chunking import load_records, chunk_all_records

COLLECTION_NAME = "healthlabelcheck"
PERSIST_DIR = "chroma_db"
MODEL_NAME = "all-MiniLM-L6-v2"


def get_chroma_client() -> chromadb.PersistentClient:
    """Return a persistent Chroma client stored in PERSIST_DIR."""
    os.makedirs(PERSIST_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=PERSIST_DIR)


def get_collection(client: chromadb.PersistentClient = None):
    """Get or create the regulation chunks collection."""
    if client is None:
        client = get_chroma_client()

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=MODEL_NAME
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def index_chunks(chunks: List[Dict], collection=None) -> int:
    """
    Upsert chunks into the Chroma collection.
    Returns the number of items now in the collection.
    """
    if collection is None:
        collection = get_collection()

    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "page": c["page"],
            "title": c["title"],
            "regulation_no": c["regulation_no"],
            "applies_to": c["applies_to"],
        }
        for c in chunks
    ]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return collection.count()


def semantic_search(query: str, top_k: int = 3, collection=None) -> List[Dict]:
    """
    Query the Chroma collection and return top_k results.
    Each result dict has: id, text, score, and metadata fields.
    """
    if collection is None:
        collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append(
            {
                "text": doc,
                "score": round(1 - dist, 4),   # cosine distance → similarity
                "regulation_no": meta.get("regulation_no"),
                "title": meta.get("title"),
                "source": meta.get("source"),
                "page": meta.get("page"),
            }
        )
    return hits


def build_index() -> int:
    """Full pipeline: load records → chunk → index."""
    print("Loading records …")
    records = load_records()
    chunks = chunk_all_records(records)
    print(f"Chunks to index: {len(chunks)}")

    collection = get_collection()
    total = index_chunks(chunks, collection)
    print(f"Collection size after upsert: {total}")
    return total


if __name__ == "__main__":
    total = build_index()
    print(f"\nIndex built. Total chunks: {total}")

    print("\n=== Test semantic search ===")
    queries = [
        "vegetarian symbol rules",
        "font size for small pouch",
        "FSSAI license number on label",
    ]
    for q in queries:
        print(f"\nQuery: '{q}'")
        for hit in semantic_search(q, top_k=2):
            print(f"  [{hit['score']:.3f}] {hit['regulation_no']}: {hit['title']}")
