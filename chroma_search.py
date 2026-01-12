import os
import sys
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import ollama

# --- Constants ---
EMBEDDING_MODEL_NAME = "all-minilm-l6-v2"
LLM_MODEL = "gpt-oss:120b-cloud"
CHROMA_PERSIST_DIR = "chroma_db"
CHROMA_COLLECTION = "ai_references"
PDF_DIRECTORY = "AI Reference Pdf"

# --- Embedding Function ---
# Use a consistent embedding function for both ingestion and querying
SENTENCE_TRANSFORMER_EF = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL_NAME
)

# --- PDF Processing ---
def extract_text_from_pdf(file_path):
    """Extracts text from a single PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# --- Ingestion ---
def ingest_data():
    """Sets up ChromaDB, and ingests data from PDF files."""
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION, embedding_function=SENTENCE_TRANSFORMER_EF
    )

    if collection.count() > 0:
        print("Data has already been ingested. Skipping ingestion.")
        print("If you want to re-ingest, please delete the chroma_db directory.")
        return

    print("Ingesting data...")
    documents = []
    metadatas = []
    ids = []
    for i, filename in enumerate(os.listdir(PDF_DIRECTORY)):
        if filename.endswith(".pdf"):
            file_path = os.path.join(PDF_DIRECTORY, filename)
            text = extract_text_from_pdf(file_path)
            if text:
                documents.append(text)
                metadatas.append({"source": filename})
                ids.append(str(i))
    
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Data ingestion complete.")
    else:
        print("No documents found to ingest.")

# --- Search ---
def perform_search(query: str):
    """Performs a search in ChromaDB and generates a response."""
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    try:
        collection = client.get_collection(
            name=CHROMA_COLLECTION, embedding_function=SENTENCE_TRANSFORMER_EF
        )
    except ValueError:
        print("Database not found. Please run 'python chroma_search.py ingest' first.")
        sys.exit(1)

    # The original search.py used a different model for query, which is likely a bug.
    # Using the same embedding function for query and ingestion.
    query_embedding = SENTENCE_TRANSFORMER_EF([query])[0]

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

    response = ollama.generate(model=LLM_MODEL, prompt=prompt)
    print(response['response'])


# --- Main ---
def main():
    """Main function to ingest data or perform a search."""
    if len(sys.argv) < 2 or sys.argv[1] not in ["ingest", "search"]:
        print("Usage: python chroma_search.py [ingest|search] [query]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "ingest":
        ingest_data()
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python chroma_search.py search <query>")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        perform_search(query)

if __name__ == "__main__":
    main()