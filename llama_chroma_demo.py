"""
LlamaIndex integration with ChromaDB.

This script demonstrates how to:
1. Load PDF documents from the ``AI Reference`` directory.
2. Embed them using a ``SentenceTransformer`` model.
3. Store the embeddings in a persistent Chroma collection.
4. Perform a similarity search via LlamaIndex's query engine.

Run it as:
    python llama_chroma_demo.py ingest          # build the vector store
    python llama_chroma_demo.py query "your question"

The script expects the ``OPENAI_API_KEY`` (or other required env vars) to be set
if you later switch to an LLM‑based query engine. For pure embedding search the
environment variables are not required.
"""

from __future__ import annotations

import os
import sys
import json
from urllib import response
import requests
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import chromadb

# LlamaIndex imports – these are optional dependencies that the user can install:
# ``pip install llama-index llama-index-vector-stores-chroma``
try:
    # Core classes are now located under ``llama_index.core``
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        load_index_from_storage,
        Settings,
    )
    from llama_index.core.embeddings import BaseEmbedding

    # The Chroma vector store class is named ``ChromaVectorStore``
    from llama_index.vector_stores.chroma import ChromaVectorStore

    # Import the Ollama LLM class
    from llama_index.llms.ollama import Ollama
except ImportError as e:  # pragma: no cover – guidance for missing deps
    raise ImportError(
        "LlamaIndex packages are required. Install with: "
        "pip install llama-index llama-index-vector-stores-chroma"
    ) from e

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()  # Load .env if present

# A dummy OpenAI API key is set to satisfy LlamaIndex's default embedding model
# configuration. The script relies on Ollama embeddings, so the key is never used.
os.environ.setdefault("OPENAI_API_KEY", "dummy-key")

# Directory containing the source PDF documents for ingestion.
PDF_DIRECTORY = Path("AI Reference Pdf")
CHROMA_PERSIST_DIR = Path("chroma_db_llama")
CHROMA_COLLECTION = "ai_references"
# Use Ollama models for both embeddings and LLM generation.
# The embedding model should support the /api/embeddings endpoint.
# A common choice is "nomic-embed-text".
EMBEDDING_MODEL = "nomic-embed-text"
# Default LLM model for answering queries.
LLM_MODEL = "gpt-oss:120b-cloud"


def _ollama_embed(texts: list[str]) -> list[list[float]]:
    """Obtain embeddings from a local Ollama server.

    The Ollama API expects a single ``prompt`` per request, so we perform a
    request for each piece of text. The function returns a list of embedding
    vectors matching the input order.
    """
    url = "http://localhost:11434/api/embeddings"
    embeddings: list[list[float]] = []
    for txt in texts:
        # Ollama expects JSON with ``model`` and ``prompt`` fields.
        payload = {"model": EMBEDDING_MODEL, "prompt": txt}
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            embeddings.append(data.get("embedding", []))
        except Exception as exc:
            print(f"⚠️  Ollama embedding failed: {exc}")
            embeddings.append([])
    return embeddings


class OllamaEmbedding(BaseEmbedding):
    """Custom Ollama embedding model for LlamaIndex."""

    def _get_text_embedding(self, text: str) -> list[float]:
        """Get text embedding."""
        return _ollama_embed([text])[0]

    def _get_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get text embeddings."""
        return _ollama_embed(texts)

    def _get_query_embedding(self, query: str) -> list[float]:
        """Get query embedding."""
        return _ollama_embed([query])[0]

    async def _aget_query_embedding(self, query: str) -> list[float]:
        """Get query embedding async."""
        return self._get_query_embedding(query)

def _get_chroma_collection() -> Any:
    """Create (or retrieve) a persistent Chroma collection.

    ``ChromaVectorStore`` can accept an already‑instantiated collection via the
    ``chroma_collection`` argument. We use a ``PersistentClient`` so that the
    data survives across runs.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    collection = client.get_or_create_collection(name=CHROMA_COLLECTION)
    return collection

def ingest() -> None:
    """Read PDFs, embed them, and store in Chroma via LlamaIndex.

    The function is idempotent – if the collection already contains
    documents the script will skip re‑ingestion.
    """
    collection = _get_chroma_collection()

    # Set up the vector store wrapper for LlamaIndex using the existing
    # collection.
    vector_store = ChromaVectorStore(chroma_collection=collection)

    # Build a storage context that points to the vector store.
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Load documents from the PDF directory.
    if not PDF_DIRECTORY.is_dir():
        print(f"⚠️  PDF directory '{PDF_DIRECTORY}' not found.")
        sys.exit(1)

    documents = SimpleDirectoryReader(input_dir=str(PDF_DIRECTORY)).load_data()
    if not documents:
        print("⚠️  No documents loaded – check the PDF folder.")
        sys.exit(1)

    # Create the index – this will automatically add embeddings to Chroma.
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context
    )
    # Persist the index metadata (the vector store itself is already persisted).
    index.storage_context.persist(persist_dir=str(CHROMA_PERSIST_DIR))
    print(
        f"✅  Ingested {len(documents)} "
        f"documents into Chroma collection '{CHROMA_COLLECTION}'."
    )

def query_user(query: str) -> None:
    """Load the persisted index and run a similarity query.

    The query engine returns ``Response`` objects – we print the source and
    a snippet of each matching document.
    """
    collection = _get_chroma_collection()
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=str(CHROMA_PERSIST_DIR)
    )
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    # Use the previously configured Ollama LLM for the query engine
    query_engine = index.as_query_engine(llm=Settings.llm)
    response = query_engine.query(query)
    print(response)

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python llama_chroma_demo.py <ingest|query> [args]")
        sys.exit(1)

    Settings.embed_model = OllamaEmbedding()
    Settings.llm = Ollama(model=LLM_MODEL, request_timeout=120.0,temperature=0.7)

    command = sys.argv[1].lower()
    if command == "ingest":
        ingest()
    elif command == "query":
        if len(sys.argv) < 3:
            print("Please provide a query string after 'query'.")
            sys.exit(1)
        user_query = " ".join(sys.argv[2:])
        query_user(user_query)
    else:
        print(f"Unknown command '{command}'. Use 'ingest' or 'query'.")
        sys.exit(1)


if __name__ == "__main__":
    main()