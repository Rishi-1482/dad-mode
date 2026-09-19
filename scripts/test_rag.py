from app.services.rag import retrieve


question = "What is Retrieval-Augmented Generation?"

results = retrieve(question, n_results=3)

for result in results:
    print("\n---")
    print("Source:", result["source"])
    print("Distance:", result["distance"])
    print("Content:")
    print(result["document"])