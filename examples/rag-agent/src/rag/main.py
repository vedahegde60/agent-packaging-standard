import sys, json, os
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[2]  # .../examples/rag-agent
DOCS = ROOT / "docs_src"

# Load docs
docs: List[str] = []
filenames: List[str] = []
for p in sorted(DOCS.glob("*.txt")):
    try:
        text = p.read_text(encoding="utf-8").strip()
        if text:
            docs.append(text)
            filenames.append(p.name)
    except Exception:
        pass

if not docs:
    docs = ["(No documents found in docs_src/)"]
    filenames = ["(none)"]

# Fit TF-IDF
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(docs)

def query_docs(q: str, top_k: int = 1) -> List[Tuple[str, float, str]]:
    qv = vectorizer.transform([q])
    sims = cosine_similarity(qv, X).ravel()
    idxs = sims.argsort()[::-1][:max(1, top_k)]
    results = []
    for i in idxs:
        results.append((docs[i], float(sims[i]), filenames[i]))
    return results

def handle_request(req: dict) -> dict:
    inputs = req.get("inputs", {})
    q = inputs.get("query", "").strip()
    top_k = int(inputs.get("top_k", 1))
    if not q:
        return {"status": "error", "message": "Missing 'query' in inputs"}
    matches = query_docs(q, top_k=top_k)
    answer = matches[0][0] if matches else ""
    return {
        "status": "ok",
        "outputs": {
            "answer": answer,
            "matches": [
                {"text": t, "score": s, "file": f} for (t, s, f) in matches
            ],
        },
    }

def main():
    # APS stdin->stdout JSON envelope
    raw = sys.stdin.read().strip()
    if not raw:
        print(json.dumps({"status": "error", "message": "Empty request"}))
        return
    try:
        req = json.loads(raw)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
        return
    resp = handle_request(req)
    print(json.dumps(resp))

if __name__ == "__main__":
    main()

