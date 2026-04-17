#!/usr/bin/env python3
"""Search theorems using a reranker API on slogan embeddings."""

import argparse
import pandas as pd
import requests
import sys

import os
BASE_DIR = os.path.expanduser("~/source/llm-retrieval/theorem-search")
RERANKER_URL = "http://10.10.10.76:5678/v1/rerank"
SLOGAN_CHUNK_SIZE = 5000  # batch slogans to keep payload manageable


def load_slogans():
    """Load slogan data, selecting only needed columns for efficiency."""
    print("Loading theorem_slogan.parquet ...", file=sys.stderr)
    df = pd.read_parquet(
        f"{BASE_DIR}/theorem_slogan.parquet",
        columns=["slogan_id", "theorem_id", "slogan"],
    )
    return df


def load_theorems():
    """Load theorem data, selecting only needed columns."""
    print("Loading theorem.parquet ...", file=sys.stderr)
    df = pd.read_parquet(
        f"{BASE_DIR}/theorem.parquet",
        columns=["theorem_id", "paper_id", "name", "body", "label", "link"],
    )
    return df


def rerank(query: str, documents: list[str], top_n: int) -> list[dict]:
    """Call the reranker API and return results."""
    payload = {
        "model": "reranker",
        "query": query,
        "documents": documents,
        "top_n": top_n,
    }
    resp = requests.post(RERANKER_URL, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["results"]


def search(query: str, top_n: int, slogan_df: pd.DataFrame):
    """Search for top matching theorems by reranking slogan chunks."""
    slogans = slogan_df["slogan"].tolist()
    slogan_to_theorem = dict(zip(slogan_df["slogan_id"], slogan_df["theorem_id"]))

    # We need a global top_n across all chunks; collect top candidates
    # from each chunk, then deduplicate and pick final top_n
    all_results: list[dict] = []

    num_chunks = (len(slogans) + SLOGAN_CHUNK_SIZE - 1) // SLOGAN_CHUNK_SIZE
    for i in range(num_chunks):
        start = i * SLOGAN_CHUNK_SIZE
        end = start + SLOGAN_CHUNK_SIZE
        chunk = slogans[start:end]
        print(
            f"Reranking chunk {i + 1}/{num_chunks} ({len(chunk)} slogans) ...",
            file=sys.stderr,
        )
        chunk_results = rerank(query, chunk, top_n=3)
        for r in chunk_results:
            slogan_idx = start + r["index"]
            # Map back to theorem_id via the original index
            all_results.append(
                {
                    "slogan_id": slogan_df.iloc[slogan_idx]["slogan_id"],
                    "theorem_id": slogan_df.iloc[slogan_idx]["theorem_id"],
                    "relevance_score": r["relevance_score"],
                }
            )
        # Free memory from large chunk
        del chunk

    # Sort by score descending and deduplicate by theorem_id
    all_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    seen = set()
    deduped = []
    for r in all_results:
        tid = r["theorem_id"]
        if tid not in seen:
            seen.add(tid)
            deduped.append(r)
        if len(deduped) >= top_n:
            break

    return deduped


def print_theorem(theorem_df: pd.DataFrame, theorem_id):
    """Print details for a single theorem."""
    row = theorem_df[theorem_df["theorem_id"] == theorem_id]
    if row.empty:
        print(
            f"  (theorem_id {theorem_id} not found in theorem.parquet)", file=sys.stderr
        )
        return
    r = row.iloc[0]
    print(f"  theorem_id: {r['theorem_id']}")
    print(f"  paper_id:   {r['paper_id']}")
    print(f"  name:       {r['name']}")
    print(f"  label:      {r['label']}")
    print(f"  link:       {r['link']}")
    print(f"  body:       {r['body']}")


def main():
    parser = argparse.ArgumentParser(description="Search theorems by slogan reranking")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument(
        "--top-n", type=int, default=5, help="Number of results to return (default: 5)"
    )
    args = parser.parse_args()

    slogan_df = load_slogans()
    theorem_df = load_theorems()

    print(f"Query: {args.query}", file=sys.stderr)
    print(f"Slogans indexed: {len(slogan_df):,}", file=sys.stderr)
    print(file=sys.stderr)

    results = search(args.query, args.top_n, slogan_df)

    print(f"\nTop {len(results)} matching theorems:\n")
    for i, r in enumerate(results, 1):
        print(f"--- Result {i} (score: {r['relevance_score']:.4f}) ---")
        print_theorem(theorem_df, r["theorem_id"])
        print()


if __name__ == "__main__":
    main()
