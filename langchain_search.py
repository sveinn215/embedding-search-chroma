import os
import sys
import chromadb

from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_ollama import OllamaLLM

import argparse

# --- Constants ---
LLM_MODEL = "gpt-oss:120b-cloud"
BASE_CHROMA_DIR = "langchain_chroma_db"
CHROMA_COLLECTION = "langchain_ai_references"
PDF_DIRECTORY = "AI Reference Pdf"

MODEL_CONFIG = {
    "nomic-embed-text": {"chunk_size": 1000, "chunk_overlap": 200},
    "chroma/all-minilm-l6-v2-f32": {"chunk_size": 200, "chunk_overlap": 50},
}
DEFAULT_CHUNK_SIZE = 200
DEFAULT_CHUNK_OVERLAP = 50


# --- Ingestion ---
def ingest_data(embedding_model_name: str):
    """Ingests data from PDF files into a Chroma vector store."""
    chroma_persist_dir = os.path.join(BASE_CHROMA_DIR, embedding_model_name.replace('/', '-'))
    
    if os.path.exists(chroma_persist_dir):
        print(f"Vector store for model '{embedding_model_name}' already exists at {chroma_persist_dir}. Skipping ingestion.")
        print("If you want to re-ingest, please delete the directory.")
        return

    config = MODEL_CONFIG.get(embedding_model_name, {"chunk_size": DEFAULT_CHUNK_SIZE, "chunk_overlap": DEFAULT_CHUNK_OVERLAP})
    chunk_size = config["chunk_size"]
    chunk_overlap = config["chunk_overlap"]

    print("Loading documents...")
    documents = []
    for filename in os.listdir(PDF_DIRECTORY):
        if filename.endswith(".pdf"):
            file_path = os.path.join(PDF_DIRECTORY, filename)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

    if not documents:
        print("No documents found to ingest.")
        return

    print(f"Splitting documents into chunks (size: {chunk_size}, overlap: {chunk_overlap})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_documents(documents)

    print(f"Creating embeddings and vector store with model '{embedding_model_name}'...")
    embeddings = OllamaEmbeddings(model=embedding_model_name)
    
    vectordb = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings,
        persist_directory=chroma_persist_dir
    )
    
    print("Data ingestion complete.")
    print(f"Vector store created at: {chroma_persist_dir}")


# --- Search ---
def perform_search(query: str, embedding_model_name: str, output_file: str = None):
    """Performs a search using LangChain, Chroma, and an LLM."""
    chroma_persist_dir = os.path.join(BASE_CHROMA_DIR, embedding_model_name.replace('/', '-'))
    
    if not os.path.exists(chroma_persist_dir):
        print(f"Vector store for model '{embedding_model_name}' not found. Please run 'python langchain_search.py ingest --model {embedding_model_name}' first.")
        print(f"Expected to find it at: {chroma_persist_dir}")
        sys.exit(1)

    print(f"Loading vector store for model '{embedding_model_name}'...")
    embeddings = OllamaEmbeddings(model=embedding_model_name)
    vectordb = Chroma(
        persist_directory=chroma_persist_dir, 
        embedding_function=embeddings
    )

    retriever = vectordb.as_retriever()
    llm = OllamaLLM(model=LLM_MODEL)

    print("Performing search...")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    result = qa_chain.invoke({"query": query})

    markdown_output = f"""
# Search Result

## Query
{query}

## Answer
{result["result"]}

## Source Documents
"""
    for doc in result["source_documents"]:
        markdown_output += f"- {doc.metadata.get('source', 'N/A')}\n"

    if output_file:
        with open(output_file, "w") as f:
            f.write(markdown_output)
        print(f"Search result exported to {output_file}")
    else:
        print(markdown_output)


# --- Main ---
def main():
    """Main function to ingest data or perform a search."""
    parser = argparse.ArgumentParser(description="Ingest data or perform a search with a specific embedding model.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest data into the vector store.")
    ingest_parser.add_argument("--model", default="chroma/all-minilm-l6-v2-f32", help="The embedding model to use for ingestion.")

    # Search command
    search_parser = subparsers.add_parser("search", help="Perform a search in the vector store.")
    search_parser.add_argument("query", help="The search query.")
    search_parser.add_argument("--model", default="all-MiniLM-L6-v2", help="The embedding model to use for searching.")

    args = parser.parse_args()

    if args.command == "ingest":
        ingest_data(args.model)
    elif args.command == "search":
        output_filename = f"langchain-{args.model.replace('/', '-')}.md"
        perform_search(args.query, args.model, output_filename)

if __name__ == "__main__":
    main()
