"""
LAB-05: GraphQL vs REST — Data Collection
==========================================
Sprint 2 — Experiment Execution

Measures response time (ms) and response size (bytes) for
equivalent requests via REST and GraphQL on the GitHub API.

Usage:
    1. Copy .env.example to .env
    2. Edit .env and add your GitHub token
    3. Run python scripts/collect_data.py

Results are saved to data/results.csv
"""

import os
import csv
import time
import random
import sys
from pathlib import Path

from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not GITHUB_TOKEN:
    print("Error: set the GITHUB_TOKEN environment variable before running.")
    sys.exit(1)

REST_BASE = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"

HEADERS_REST = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    # No Accept-Encoding to receive uncompressed data (fair comparison)
    "Accept-Encoding": "identity",
}

HEADERS_GRAPHQL = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
    "Accept-Encoding": "identity",
}

# Experimental object repositories (20 popular repositories)
REPOS = [
    ("facebook", "react"),
    ("vuejs", "vue"),
    ("microsoft", "vscode"),
    ("torvalds", "linux"),
    ("tensorflow", "tensorflow"),
    ("twbs", "bootstrap"),
    ("ohmyzsh", "ohmyzsh"),
    ("angular", "angular"),
    ("golang", "go"),
    ("kubernetes", "kubernetes"),
    ("nodejs", "node"),
    ("django", "django"),
    ("rails", "rails"),
    ("laravel", "laravel"),
    ("flutter", "flutter"),
    ("denoland", "deno"),
    ("rust-lang", "rust"),
    ("apple", "swift"),
    ("libp2p", "go-libp2p"),
    ("python", "cpython"),
]

TRIALS = 30          # Repetitions per repository × API
DELAY_BETWEEN = 1.0  # Seconds between requests (prevents rate limit and caching)

# GraphQL query — requests only necessary fields
GRAPHQL_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    name
    description
    stargazerCount
    forkCount
    issues(states: OPEN) {
      totalCount
    }
    updatedAt
    primaryLanguage {
      name
    }
  }
}
"""

OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "results.csv"

CSV_FIELDS = [
    "trial",
    "owner",
    "repo",
    "api_type",
    "response_time_ms",
    "response_size_bytes",
    "http_status",
]


# ---------------------------------------------------------------------------
# Measurement functions
# ---------------------------------------------------------------------------

def measure_rest(owner: str, repo: str) -> dict:
    """Performs a REST request and returns metrics."""
    url = f"{REST_BASE}/repos/{owner}/{repo}"
    start = time.perf_counter()
    response = requests.get(url, headers=HEADERS_REST, timeout=30)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "api_type": "REST",
        "response_time_ms": round(elapsed_ms, 3),
        "response_size_bytes": len(response.content),
        "http_status": response.status_code,
    }


def measure_graphql(owner: str, repo: str) -> dict:
    """Performs a GraphQL request and returns metrics."""
    payload = {
        "query": GRAPHQL_QUERY,
        "variables": {"owner": owner, "name": repo},
    }
    start = time.perf_counter()
    response = requests.post(
        GRAPHQL_URL,
        json=payload,
        headers=HEADERS_GRAPHQL,
        timeout=30,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "api_type": "GraphQL",
        "response_time_ms": round(elapsed_ms, 3),
        "response_size_bytes": len(response.content),
        "http_status": response.status_code,
    }


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def run_experiment():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = len(REPOS) * TRIALS * 2
    done = 0

    print(f"Starting collection: {len(REPOS)} repositories × {TRIALS} trials × 2 APIs = {total} requests")
    print(f"Results will be saved to: {OUTPUT_FILE}\n")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for trial in range(1, TRIALS + 1):
            print(f"=== Trial {trial}/{TRIALS} ===")

            for owner, repo in REPOS:
                # Randomize REST/GraphQL order per trial
                calls = [measure_rest, measure_graphql]
                random.shuffle(calls)

                for measure_fn in calls:
                    try:
                        metrics = measure_fn(owner, repo)
                    except requests.RequestException as exc:
                        print(f"  ERROR [{owner}/{repo}] {measure_fn.__name__}: {exc}")
                        continue

                    row = {
                        "trial": trial,
                        "owner": owner,
                        "repo": repo,
                        **metrics,
                    }
                    writer.writerow(row)
                    csvfile.flush()  # Persiste imediatamente

                    done += 1
                    pct = done / total * 100
                    print(
                        f"  [{pct:5.1f}%] {owner}/{repo:20s} "
                        f"{metrics['api_type']:8s} "
                        f"{metrics['response_time_ms']:8.1f} ms  "
                        f"{metrics['response_size_bytes']:6d} bytes  "
                        f"HTTP {metrics['http_status']}"
                    )

                    time.sleep(DELAY_BETWEEN)

    print(f"\nCollection completed! {done} measurements saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run_experiment()
