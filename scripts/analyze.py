"""
LAB-05: GraphQL vs REST — Statistical Analysis
=============================================
Sprint 2 — Results Analysis

Loads collected data (data/results.csv) and produces:
  - Descriptive statistics by API
  - Hypothesis test (Mann-Whitney U) for RQ1 and RQ2
  - Results table saved to data/analysis_summary.txt

Usage:
    Run python scripts/analyze.py
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

DATA_FILE = Path(__file__).parent.parent / "data" / "results.csv"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "analysis_summary.txt"


def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Data file not found: {DATA_FILE}\n"
            "Run first: python scripts/collect_data.py"
        )
    df = pd.read_csv(DATA_FILE)
    # Remove failed requests (status != 200)
    before = len(df)
    df = df[df["http_status"] == 200].copy()
    removed = before - len(df)
    if removed > 0:
        print(f"[!] {removed} row(s) removed due to HTTP status != 200")
    return df


def descriptive_stats(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Returns descriptive statistics separated by API."""
    grouped = df.groupby("api_type")[metric]
    result = grouped.agg(
        n="count",
        mean="mean",
        median="median",
        std="std",
        min="min",
        max="max",
        q25=lambda x: x.quantile(0.25),
        q75=lambda x: x.quantile(0.75),
    ).round(3)
    return result


def mann_whitney_test(df: pd.DataFrame, metric: str):
    """Performs Mann-Whitney U test (two-tailed) between GraphQL and REST."""
    graphql_vals = df[df["api_type"] == "GraphQL"][metric].values
    rest_vals = df[df["api_type"] == "REST"][metric].values
    statistic, p_value = stats.mannwhitneyu(
        graphql_vals, rest_vals, alternative="two-sided"
    )
    return statistic, p_value, graphql_vals, rest_vals


def effect_size_rank_biserial(u_stat: float, n1: int, n2: int) -> float:
    """Rank-Biserial correlation r (effect size for Mann-Whitney)."""
    return 1 - (2 * u_stat) / (n1 * n2)


def interpret_p(p: float) -> str:
    if p < 0.001:
        return "p < 0.001 *** (highly significant)"
    elif p < 0.01:
        return f"p = {p:.4f} ** (very significant)"
    elif p < 0.05:
        return f"p = {p:.4f} * (significant)"
    else:
        return f"p = {p:.4f} (not significant — H₀ not rejected)"


def interpret_effect(r: float) -> str:
    abs_r = abs(r)
    if abs_r < 0.1:
        return "negligible"
    elif abs_r < 0.3:
        return "small"
    elif abs_r < 0.5:
        return "medium"
    else:
        return "large"


def analyze():
    df = load_data()
    lines = []

    def log(msg=""):
        print(msg)
        lines.append(msg)

    log("=" * 70)
    log("LAB-05: GraphQL vs REST — Statistical Analysis Results")
    log("=" * 70)
    log(f"\nTotal valid measurements: {len(df)}")
    log(f"  GraphQL: {len(df[df['api_type'] == 'GraphQL'])}")
    log(f"  REST   : {len(df[df['api_type'] == 'REST'])}")

    # ------------------------------------------------------------------
    # RQ1 — Response time
    # ------------------------------------------------------------------
    log("\n" + "─" * 70)
    log("RQ1: Are GraphQL responses faster than REST?")
    log("─" * 70)

    metric = "response_time_ms"
    desc = descriptive_stats(df, metric)
    log("\nDescriptive Statistics — Response Time (ms):")
    log(desc.to_string())

    u_stat, p_val, gql_vals, rest_vals = mann_whitney_test(df, metric)
    r = effect_size_rank_biserial(u_stat, len(gql_vals), len(rest_vals))

    gql_median = np.median(gql_vals)
    rest_median = np.median(rest_vals)
    pct_diff = (rest_median - gql_median) / rest_median * 100

    log(f"\nMann-Whitney U Test")
    log(f"  U = {u_stat:.0f}")
    log(f"  {interpret_p(p_val)}")
    log(f"  Effect size (rank-biserial r) = {r:.4f} ({interpret_effect(r)})")
    log(f"\nMedian GraphQL: {gql_median:.2f} ms")
    log(f"Median REST   : {rest_median:.2f} ms")
    log(f"Relative difference: {pct_diff:.1f}% {'(GraphQL faster)' if pct_diff > 0 else '(REST faster)'}")

    if p_val < 0.05:
        if gql_median < rest_median:
            log("\nConclusion RQ1: H₀ rejected — GraphQL is significantly FASTER than REST.")
        else:
            log("\nConclusion RQ1: H₀ rejected — REST is significantly FASTER than GraphQL.")
    else:
        log("\nConclusion RQ1: H₀ not rejected — no significant difference in time.")

    # ------------------------------------------------------------------
    # RQ2 — Response size
    # ------------------------------------------------------------------
    log("\n" + "─" * 70)
    log("RQ2: Do GraphQL responses have smaller size than REST?")
    log("─" * 70)

    metric = "response_size_bytes"
    desc2 = descriptive_stats(df, metric)
    log("\nDescriptive Statistics — Response Size (bytes):")
    log(desc2.to_string())

    u_stat2, p_val2, gql_vals2, rest_vals2 = mann_whitney_test(df, metric)
    r2 = effect_size_rank_biserial(u_stat2, len(gql_vals2), len(rest_vals2))

    gql_median2 = np.median(gql_vals2)
    rest_median2 = np.median(rest_vals2)
    pct_diff2 = (rest_median2 - gql_median2) / rest_median2 * 100

    log(f"\nMann-Whitney U Test")
    log(f"  U = {u_stat2:.0f}")
    log(f"  {interpret_p(p_val2)}")
    log(f"  Effect size (rank-biserial r) = {r2:.4f} ({interpret_effect(r2)})")
    log(f"\nMedian GraphQL: {gql_median2:.0f} bytes")
    log(f"Median REST   : {rest_median2:.0f} bytes")
    log(f"Relative reduction: {pct_diff2:.1f}% {'(GraphQL smaller)' if pct_diff2 > 0 else '(REST smaller)'}")

    if p_val2 < 0.05:
        if gql_median2 < rest_median2:
            log("\nConclusion RQ2: H₀ rejected — GraphQL produces significantly SMALLER responses than REST.")
        else:
            log("\nConclusion RQ2: H₀ rejected — REST produces significantly SMALLER responses than GraphQL.")
    else:
        log("\nConclusion RQ2: H₀ not rejected — no significant difference in size.")

    log("\n" + "=" * 70)

    # Save results to text file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSummary saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    analyze()
