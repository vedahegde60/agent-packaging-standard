# RAG Agent (APS Example)

# RAG Agent (TF-IDF) — APS Example

A minimal, Torch-free RAG agent using TF-IDF + cosine similarity over local `docs_src/*.txt`.

## Install

```bash
# Install CLI
pip install apstool

# Install agent dependencies
pip install -r requirements.txt
```

## Run

```bash
echo '{"query":"What is APS?"}' | aps run .
