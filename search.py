
import chromadb
from chromadb.utils import embedding_functions
import sys
import ollama


EMBEDDING_MODEL = "chroma/all-minilm-l6-v2-f32"
LLM_MODEL = "gpt-oss:120b-cloud"
CHROMA_PERSIST_DIR = "chroma_db"
CHROMA_COLLECTION = "ai_references"

def main():
    """Main function to perform a search in ChromaDB."""
    if len(sys.argv) < 2:
        print("Usage: python search.py <query>")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    try:
        collection = client.get_collection(
            name=CHROMA_COLLECTION, embedding_function=sentence_transformer_ef
        )
    except ValueError:
        print("Database not found. Please run ingest.py first.")
        sys.exit(1)
    response = user_query(query, collection)
    print(response)

def user_query(query: str, collection: chromadb.Collection) -> str:
    """Run a similarity query against the ChromaDB collection."""

    query_embedding = ollama.embeddings(
        model=EMBEDDING_MODEL, 
        prompt=query
    )["embedding"]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    context = "\n\n".join(results['documents'][0])

    prompt = f"""
    You are a helpful assistant. Use the provided context to answer the question.
    If the answer isn't in the context, say you don't know.

    Context:
    {context}

    Question: 
    {query}

    Answer:
    """

    # 5. Generate response using your gpt-oss model
    response = ollama.generate(model=LLM_MODEL, prompt=prompt)
    return response['response']

if __name__ == "__main__":
    main()
