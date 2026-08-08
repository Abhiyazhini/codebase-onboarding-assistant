import chromadb
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from git_extractor import clone_repo, get_python_files, get_recent_commits_for_file
from ast_parser import parse_python_file

# Loads a small embedding model locally — first run downloads ~80MB, then it's cached
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Creates a local folder-based vector database — no server, no cost
client = chromadb.PersistentClient(path="./chroma_db")


def process_file(repo_path: str, file_path: str):
    chunks = parse_python_file(file_path)
    if not chunks:
        return file_path, [], []
    commits = get_recent_commits_for_file(repo_path, file_path, max_count=3)
    return file_path, chunks, commits


def index_repo(github_url: str):
    """
    Clones a GitHub repo, parses every .py file into function/class chunks,
    attaches git commit history to each chunk, embeds everything in one
    batch (fast), and stores it all in ChromaDB in a single insert (fast).
    """
    repo_path = clone_repo(github_url)
    collection = client.get_or_create_collection(name="codebase")

    # Clear old data so re-indexing doesn't duplicate/stack old results
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    py_files = get_python_files(repo_path)
    print(f"Found {len(py_files)} Python files. Parsing...")

    # Step 1: collect everything first (fast, no network/model calls yet)
    all_texts = []
    all_ids = []
    all_metadatas = []
    all_documents = []
    doc_id = 0

    max_workers = min(8, os.cpu_count() or 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_file, repo_path, file_path) for file_path in py_files]
        for future in as_completed(futures):
            _, chunks, commits = future.result()
            if not chunks:
                continue

            for chunk in chunks:
                enriched_text = f"{chunk['type']} {chunk['name']} in {chunk['file_path']}:\n{chunk['code']}"

                all_texts.append(enriched_text)
                all_ids.append(str(doc_id))
                all_documents.append(chunk["code"])
                all_metadatas.append({
                    "file_path": chunk["file_path"],
                    "name": chunk["name"],
                    "type": chunk["type"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "commits": str(commits),  # Chroma metadata must be strings, not nested lists/dicts
                })
                doc_id += 1

    if not all_texts:
        return {"status": "no_chunks_found", "chunks": 0, "files": len(py_files)}

    # Step 2: embed everything in ONE batched call (this is the big speedup —
    # embedding 300 chunks one-by-one vs. in batches of 32 can be 5-10x slower)
    print(f"Embedding {len(all_texts)} chunks in batches...")
    embeddings = embedder.encode(
        all_texts,
        batch_size=32,
        show_progress_bar=True
    ).tolist()

    # Step 3: insert everything into ChromaDB in ONE call instead of hundreds
    print("Writing to ChromaDB...")
    collection.add(
        ids=all_ids,
        embeddings=embeddings,
        documents=all_documents,
        metadatas=all_metadatas,
    )

    print("Indexing complete.")
    return {"status": "indexed", "chunks": doc_id, "files": len(py_files)}


def search_codebase(query: str, top_k: int = 4):
    """
    Embeds the user's question and finds the top_k most semantically
    similar code chunks from ChromaDB.
    """
    collection = client.get_or_create_collection(name="codebase")
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    matches = []
    for i in range(len(results["ids"][0])):
        matches.append({
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
        })
    return matches


if __name__ == "__main__":
    import time

    print("Indexing repo... this may take 1-3 minutes")
    start = time.time()
    result = index_repo("https://github.com/tiangolo/full-stack-fastapi-template")
    elapsed = time.time() - start

    print(f"\n{result}")
    print(f"Took {elapsed:.1f} seconds")

    print("\nSearching for: 'where is authentication handled'")
    matches = search_codebase("where is authentication handled")
    for m in matches:
        meta = m["metadata"]
        print(f"- {meta['file_path']} -> {meta['name']} ({meta['type']}, lines {meta['start_line']}-{meta['end_line']})")