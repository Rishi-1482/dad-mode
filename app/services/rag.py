from pathlib import Path

import chromadb

from app.services.dad import client


CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "dad_mode_knowledge"
EMBEDDING_MODEL = "text-embedding-3-small"


# Persistent local Chroma database
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:
    """
    Split text into overlapping character chunks.
    """
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate OpenAI embeddings for a list of text chunks.
    """
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    return [item.embedding for item in response.data]


def ingest_document(file_path: str) -> int:
    """
    Read a text/markdown/PDF document, chunk it,
    generate embeddings, and store it in ChromaDB.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))

        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif path.suffix.lower() in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8")

    else:
        raise ValueError(
            "Supported file types are .txt, .md, and .pdf"
        )

    text = text.strip()

    if not text:
        raise ValueError(f"No text found in {file_path}")

    chunks = chunk_text(text)

    embeddings = create_embeddings(chunks)

    ids = [
        f"{path.name}-{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "source": path.name,
            "chunk_index": index,
        }
        for index in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    return len(chunks)


def ingest_directory(directory: str = "knowledge") -> int:
    """
    Ingest all supported documents in a directory.
    """
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge directory not found: {directory}"
        )

    total_chunks = 0

    for file_path in path.iterdir():

        if file_path.suffix.lower() in {
            ".txt",
            ".md",
            ".pdf",
        }:
            total_chunks += ingest_document(
                str(file_path)
            )

    return total_chunks


def retrieve(
    query: str,
    n_results: int = 3,
) -> list[dict]:
    """
    Retrieve the most relevant chunks for a query.
    """
    query_embedding = create_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        retrieved.append(
            {
                "document": document,
                "source": metadata.get("source", "unknown"),
                "chunk_index": metadata.get(
                    "chunk_index"
                ),
                "distance": distance,
            }
        )

    return retrieved