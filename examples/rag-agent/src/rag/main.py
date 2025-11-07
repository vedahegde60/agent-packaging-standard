import sys, os, json
from pathlib import Path
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _agent_root() -> Path:
    # src/rag/main.py -> src -> root
    return Path(__file__).resolve().parents[2]

def _load_corpus(root: Path) -> List[Tuple[str, str]]:
    assets = root / "assets"
    docs = []
    for p in assets.rglob("*.txt"):
        try:
            docs.append((p.name, p.read_text(encoding="utf-8")))
        except Exception:
            pass
    if not docs:
        # fallback: single doc
        docs = [("sample.txt", "Empty corpus. Add .txt files under assets/.")]
    return docs

def _parse_envelope(raw: str):
    try:
        obj = json.loads(raw) if raw.strip() else {}
    except Exception:
        obj = {}
    if isinstance(obj, dict) and "inputs" in obj:
        q = obj["inputs"].get("query", "")
        k = int(obj["inputs"].get("top_k", 3) or 3)
        return q, k
    # fallback if raw inputs
    q = obj.get("query", "") if isinstance(obj, dict) else str(obj)
    k = 3
    return q, k

def main():
    # Read request once
    raw = sys.stdin.read() or ""
    query, top_k = _parse_envelope(raw)
    top_k = max(1, min(int(top_k or 3), 10))

    # Build tiny index in-process (fast for small corpora)
    root = _agent_root()
    docs = _load_corpus(root)
    filenames, texts = zip(*docs)
    vec = TfidfVectorizer().fit(texts)
    D = vec.transform(texts)

    # Streaming logs (optional)
    if os.environ.get("APS_STREAM") == "1":
        print(f"[rag] loaded {len(texts)} docs", flush=True)
        print(f"[rag] querying: {query}", flush=True)

    # Query
    qv = vec.transform([query])
    sims = cosine_similarity(qv, D).ravel()
    order = sims.argsort()[::-1][:top_k]

    matches = []
    for idx in order:
        matches.append({
            "text": texts[idx][:400],
            "score": float(sims[idx]),
            "file": filenames[idx],
        })

    # Naive answer: best snippet (or empty)
    best = matches[0]["text"] if matches else ""
    answer = best if best else ""

    # Final JSON (APS contract)
    out = {
        "aps_version": "0.1",
        "status": "ok",
        "outputs": {
            "answer": answer,
            "matches": matches
        }
    }
    print(json.dumps(out))

if __name__ == "__main__":
    main()
