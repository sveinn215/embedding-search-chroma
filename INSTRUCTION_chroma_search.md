
# AI Search Instruction

When you are asked a question, you should use the `search.py` script to query the local ChromaDB of AI research papers.

## Command

To get information from the database, you must use the following shell command:

```bash
python search.py "YOUR SEARCH QUERY"
```

Replace `"YOUR SEARCH QUERY"` with the question you want to ask the database.

## Example

If the user asks: "What are the latest techniques in multi-modal understanding?", you should run the following command:

```bash
python search.py "latest techniques in multi-modal understanding"
```

The script will return the most relevant documents from the database, along with the time it took to perform the search. Use this information to answer the user's question.