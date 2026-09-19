from app.services.rag import ingest_directory


if __name__ == "__main__":
    count = ingest_directory("knowledge")

    print(f"Successfully ingested {count} chunks.")