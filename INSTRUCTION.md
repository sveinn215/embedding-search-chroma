
# ChromaDB AI Reference Search

This project uses ChromaDB to create a persistent, searchable database of the AI reference documents in the `AI Referrence` folder.

## Setup

1.  **Install/Update Dependencies:**

    First, you need to install or update the required Python libraries. You can do this using `pip` and the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Ingest Data:**

    Next, you need to ingest the PDF documents from the `AI Referrence` directory into the ChromaDB. Run the following command:

    ```bash
    python ingest.py
    ```

    This will create a `chroma_db` directory to store the database and ingest the documents. This might take a few minutes depending on the number and size of the documents. You only need to run this script once, or when you add new documents to the `AI Referrence` folder.

## Searching

To search the database, use the `search.py` script with your query as a command-line argument.

For example, to search for information about "multi-modal understanding", you would run:

```bash
python search.py "multi-modal understanding"
```

The script will return the top 5 most relevant document snippets that match your query.

Refer to `INSTRUCTION_chroma_search.md` for instructions on how to integrate this with an AI.
