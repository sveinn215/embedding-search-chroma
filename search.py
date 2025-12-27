
import os
import chromadb
from chromadb.utils import embedding_functions
import sys

def main():
    """Main function to perform a search in ChromaDB."""
    if len(sys.argv) < 2:
        print("Usage: python search.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # Initialize ChromaDB client with persistence
    client = chromadb.PersistentClient(path="chroma_db")

    # Use the default embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Get the collection
    try:
        collection = client.get_collection(
            name="ai_references", embedding_function=sentence_transformer_ef
        )
    except ValueError:
        print("Database not found. Please run ingest.py first.")
        sys.exit(1)


    # Perform a search
    import time
    start_time = time.time()
    results = collection.query(
        query_texts=[query],
        n_results=5  # You can adjust the number of results
    )
    end_time = time.time()
    duration = end_time - start_time

    print(f"\nSearch completed in {duration:.4f} seconds.\n")

    if results['documents']:
        for i, doc in enumerate(results['documents'][0]):
            print(f"Result {i+1}:")
            print(f"  Source: {results['metadatas'][0][i]['source']}")
            print(f"  Content: {doc}")
            print("-" * 20)
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
