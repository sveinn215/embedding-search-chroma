import os
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

# Path to the directory containing the PDF files
PDF_DIRECTORY = "AI Reference"

# Function to extract text from a PDF file
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

def main():
    """Main function to set up ChromaDB, ingest data, and perform a search."""
    # Initialize ChromaDB client with persistence
    client = chromadb.PersistentClient(path="chroma_db")

    # Use the default embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Create or get the collection
    collection = client.get_or_create_collection(
        name="ai_references", embedding_function=sentence_transformer_ef
    )

    # Ingest data if the collection is empty
    if collection.count() == 0:
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
            return

    print("Database is ready.")

if __name__ == "__main__":
    main()
