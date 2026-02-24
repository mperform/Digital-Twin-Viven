import os
import re
import hashlib
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from openai import OpenAI

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR    = "Profile"           # folder containing the .md files
DB_DIR      = "chroma_db"      # persisted ChromaDB directory
COLLECTION  = "digital_twin"
EMBED_MODEL = "text-embedding-3-small"

client    = OpenAI()
chroma    = chromadb.PersistentClient(path=DB_DIR)
collection = chroma.get_or_create_collection(COLLECTION)

# ── Helpers ───────────────────────────────────────────────────────────────────
def chunk_by_headers(text: str) -> list[dict]:
    """
    Split markdown text into chunks at every ## or ### header.
    Returns list of {"header": str, "content": str}
    """
    # Split on ## or ### headers, keeping the header in the chunk
    pattern = r'(?=^#{2,3}\s+.+$)'
    sections = re.split(pattern, text, flags=re.MULTILINE)
    
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # Extract the header line
        lines = section.split('\n')
        header = lines[0].strip('#').strip()
        content = '\n'.join(lines[1:]).strip()
        
        if not content:
            continue
            
        chunks.append({
            "header": header,
            "content": content
        })
    
    return chunks


def get_source_type(filename: str) -> str:
    """Map filename to a source type label."""
    mapping = {
        "profile.md":   "personality",
        "projects.md":  "project",
        "opinions.md":  "opinion"
    }
    return mapping.get(filename, "general")


def embed(text: str) -> list[float]:
    """Get OpenAI embedding for a text string."""
    response = client.embeddings.create(
        input=text,
        model=EMBED_MODEL
    )
    return response.data[0].embedding


def make_id(filename: str, header: str) -> str:
    """Generate a stable unique ID for a chunk."""
    raw = f"{filename}::{header}"
    return hashlib.md5(raw.encode()).hexdigest()


# ── Main Ingestion ────────────────────────────────────────────────────────────
def ingest_file(filepath: str):
    filename = os.path.basename(filepath)
    source_type = get_source_type(filename)

    print(f"\nIngesting: {filename} (type={source_type})")

    with open(filepath, "r") as f:
        text = f.read()

    chunks = chunk_by_headers(text)
    print(f"  Found {len(chunks)} chunks")

    for chunk in chunks:
        # Prepend header to content so the embedding is self-contained
        full_text = f"{chunk['header']}\n\n{chunk['content']}"
        
        chunk_id  = make_id(filename, chunk["header"])
        embedding = embed(full_text)
        
        metadata = {
            "source_file":   filename,
            "source_type":   source_type,   # personality | project | opinion
            "section":       chunk["header"],
        }

        collection.upsert(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[full_text],
            metadatas=[metadata]
        )

        print(f"  ✓ {chunk['header'][:60]}")


def ingest_all():
    md_files = [
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.endswith(".md")
    ]

    if not md_files:
        print(f"No markdown files found in '{DATA_DIR}/'")
        return

    for filepath in md_files:
        ingest_file(filepath)

    print(f"\n✅ Ingestion complete. {collection.count()} chunks in DB.")


if __name__ == "__main__":
    ingest_all()