from dotenv import load_dotenv
import chromadb
from openai import OpenAI

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
DB_DIR      = "chroma_db"
COLLECTION  = "digital_twin"
EMBED_MODEL = "text-embedding-3-small"
TOP_K       = 4  # number of chunks to retrieve per query

client     = OpenAI()
chroma     = chromadb.PersistentClient(path=DB_DIR)
collection = chroma.get_or_create_collection(COLLECTION)

# ── Helpers ───────────────────────────────────────────────────────────────────
def embed_query(query: str) -> list[float]:
    """Embed the user query using the same model as ingestion."""
    response = client.embeddings.create(
        input=query,
        model=EMBED_MODEL
    )
    return response.data[0].embedding


def format_chunks(results: dict) -> str:
    """
    Format retrieved chunks into a single string block
    to be injected into the prompt.
    """
    chunks = []
    for doc, metadata in zip(results["documents"][0], 
                             results["metadatas"][0]):
        source = metadata.get("source_type", "general")
        section = metadata.get("section", "")
        chunk = f"[{source.upper()} — {section}]\n{doc}"
        chunks.append(chunk)
    
    return "\n\n---\n\n".join(chunks)


# ── Main Retrieval ────────────────────────────────────────────────────────────
def retrieve(query: str, top_k: int = TOP_K) -> str:
    """
    Embed query, search ChromaDB for top-K relevant chunks,
    and return formatted string ready for prompt injection.
    """
    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    if not results["documents"][0]:
        return "No relevant context found."

    # Log retrieved chunks for transparency (useful for Phase 2 evals)
    print(f"\n📚 Retrieved {len(results['documents'][0])} chunks:")
    for metadata, distance in zip(results["metadatas"][0], 
                                  results["distances"][0]):
        print(f"  [{metadata['source_type']}] "
              f"{metadata['section'][:50]} "
              f"(distance={distance:.3f})")

    return format_chunks(results)


# ── Optional: Source-Filtered Retrieval ───────────────────────────────────────
def retrieve_by_type(query: str, 
                     source_type: str, 
                     top_k: int = TOP_K) -> str:
    """
    Retrieve chunks filtered by source type.
    Useful for targeted retrieval e.g. only personality
    chunks for casual questions, only project chunks for
    technical questions.
    
    source_type: 'personality' | 'project' | 'opinion'
    """
    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"source_type": source_type},
        include=["documents", "metadatas", "distances"]
    )

    if not results["documents"][0]:
        return f"No relevant {source_type} context found."

    return format_chunks(results)


if __name__ == "__main__":
    # Quick test
    test_query = "Tell me about Thomas's autonomous driving research"
    print(f"Query: {test_query}")
    context = retrieve(test_query)
    print(f"\nRetrieved Context:\n{context}")