from app.services.rag import retrieve


question = "According to my AWS notes, what can trigger a Lambda function?"

results = retrieve(question, n_results=2)

# for result in results:
#     print("\n---")
#     print("Source:", result["source"])
#     print("Distance:", result["distance"])
#     print("Content:")
#     print(result["document"]) 

for i, result in enumerate(results, start=1):
    print(f"\n===== CHUNK {i} =====")
    print("Source:", result["source"])
    print("Distance:", result["distance"])
    print("Content:")
    print(result["document"])