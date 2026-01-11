# AI Search Instruction (LlamaIndex Demo)

When you are asked a question, you should use the `llama_chroma_demo.py` script to query the local ChromaDB of AI research papers using LlamaIndex.

## Command

To get information from the database, you must use the following shell command:

```bash
python llama_chroma_demo.py query "YOUR SEARCH QUERY"
```

Replace `"YOUR SEARCH QUERY"` with the question you want to ask the database.

## Example

If the user asks: "What are the latest techniques in multi-modal understanding?", you should run the following command:

```bash
python llama_chroma_demo.py query "latest techniques in multi-modal understanding"
```

The script will return the most relevant documents from the database and generate an answer. Use this information to answer the user's question.
