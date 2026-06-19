"""
LAB-05: GraphQL vs REST — Visualization Dashboard
====================================================
Sprint 3 — Dashboard

Loads data from data/results.csv and generates visualizations with
Pandas, Matplotlib and Seaborn to compare REST and GraphQL on
metrics for RQ1 (response time) and RQ2 (response size).

Usage:
    python scripts/dashboard.py

Graphs are displayed on screen and saved to dashboard/output/
"""

from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats

# ---------------------------------------------------------------------------
# Visual settings
# ---------------------------------------------------------------------------
matplotlib.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.dpi": 120,
})
sns.set_theme(style="whitegrid", palette="Set2")

PALETTE = {"REST": "#E07B54", "GraphQL": "#5B8DB8"}

DATA_FILE = Path(__file__).parent.parent / "data" / "raw" / "results.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "report" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {DATA_FILE}\n"
            "Run first: python scripts/collect_data.py"
        )
    df = pd.read_csv(DATA_FILE)
    df = df[df["http_status"] == 200].copy()
    return df


def summary_table(df: pd.DataFrame, metric: str, unit: str) -> pd.DataFrame:
    g = df.groupby("api_type")[metric]
    tbl = g.agg(
        N="count",
        Mean="mean",
        Median="median",
        SD="std",
        Min="min",
        Max="max",
        Q25=lambda x: x.quantile(0.25),
        Q75=lambda x: x.quantile(0.75),
    ).round(2)
    tbl.columns = [f"{c} ({unit})" if c not in ("N",) else c for c in tbl.columns]
    return tbl


def mann_whitney(df: pd.DataFrame, metric: str):
    gql = df[df["api_type"] == "GraphQL"][metric].values
    rest = df[df["api_type"] == "REST"][metric].values
    u, p = stats.mannwhitneyu(gql, rest, alternative="two-sided")
    r = 1 - (2 * u) / (len(gql) * len(rest))
    return u, p, r, gql, rest


def add_stat_annotation(ax, x1, x2, y, p_val):
    """Add significance line between two groups."""
    if p_val < 0.001:
        sig = "***"
    elif p_val < 0.01:
        sig = "**"
    elif p_val < 0.05:
        sig = "*"
    else:
        sig = "ns"
    h = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.03
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.2, color="black")
    ax.text((x1 + x2) / 2, y + h * 1.1, sig, ha="center", va="bottom", fontsize=12)


# ---------------------------------------------------------------------------
# Figure 1: Side by side box plots (RQ1 and RQ2)
# ---------------------------------------------------------------------------

def fig_boxplots(df: pd.DataFrame):
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)
    fig.suptitle("GraphQL vs REST — Distribution of Metrics", fontsize=14, fontweight="bold")

    # Row 1: RQ1 (Response Time) - side by side with both APIs
    ax_rq1 = fig.add_subplot(gs[0, :])
    sns.boxplot(
        data=df,
        x="api_type",
        y="response_time_ms",
        order=["REST", "GraphQL"],
        palette=PALETTE,
        width=0.45,
        flierprops={"marker": "o", "markersize": 3, "alpha": 0.4},
        ax=ax_rq1,
    )
    _, p_rq1, _, _, _ = mann_whitney(df, "response_time_ms")
    y_annot_rq1 = df["response_time_ms"].quantile(0.97)
    add_stat_annotation(ax_rq1, 0, 1, y_annot_rq1, p_rq1)
    ax_rq1.set_title("RQ1 — Response Time (ms)", fontweight="bold")
    ax_rq1.set_xlabel("API Type")
    ax_rq1.set_ylabel("Response Time (ms)")

    # Row 2: RQ2 (Response Size) - separate subplots for each API with optimized scales
    ax_rq2_gql = fig.add_subplot(gs[1, 0])
    sns.boxplot(
        data=df[df["api_type"] == "GraphQL"],
        y="response_size_bytes",
        color=PALETTE["GraphQL"],
        width=0.3,
        flierprops={"marker": "o", "markersize": 3, "alpha": 0.4},
        ax=ax_rq2_gql,
    )
    ax_rq2_gql.set_title("RQ2 — GraphQL Response Size", fontweight="bold")
    ax_rq2_gql.set_ylabel("Response Size (bytes)")
    ax_rq2_gql.set_xlabel("")
    ax_rq2_gql.set_xticklabels([])

    ax_rq2_rest = fig.add_subplot(gs[1, 1])
    sns.boxplot(
        data=df[df["api_type"] == "REST"],
        y="response_size_bytes",
        color=PALETTE["REST"],
        width=0.3,
        flierprops={"marker": "o", "markersize": 3, "alpha": 0.4},
        ax=ax_rq2_rest,
    )
    ax_rq2_rest.set_title("RQ2 — REST Response Size", fontweight="bold")
    ax_rq2_rest.set_ylabel("Response Size (bytes)")
    ax_rq2_rest.set_xlabel("")
    ax_rq2_rest.set_xticklabels([])

    path = OUTPUT_DIR / "fig1_boxplots.png"
    plt.savefig(path, bbox_inches="tight")
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Figure 2: Violin plots
# ---------------------------------------------------------------------------

def fig_violins(df: pd.DataFrame):
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)
    fig.suptitle("GraphQL vs REST — Probability Distribution", fontsize=14, fontweight="bold")

    # Row 1: RQ1 (Response Time) - side by side with both APIs
    ax_rq1 = fig.add_subplot(gs[0, :])
    sns.violinplot(
        data=df,
        x="api_type",
        y="response_time_ms",
        order=["REST", "GraphQL"],
        palette=PALETTE,
        inner="box",
        cut=0,
        ax=ax_rq1,
    )
    ax_rq1.set_title("RQ1 — Response Time (ms)", fontweight="bold")
    ax_rq1.set_xlabel("API Type")
    ax_rq1.set_ylabel("Response Time (ms)")

    # Row 2: RQ2 (Response Size) - separate subplots for each API with optimized scales
    ax_rq2_gql = fig.add_subplot(gs[1, 0])
    sns.violinplot(
        data=df[df["api_type"] == "GraphQL"],
        y="response_size_bytes",
        color=PALETTE["GraphQL"],
        inner="box",
        cut=0,
        ax=ax_rq2_gql,
    )
    ax_rq2_gql.set_title("RQ2 — GraphQL Response Size", fontweight="bold")
    ax_rq2_gql.set_ylabel("Response Size (bytes)")
    ax_rq2_gql.set_xlabel("")
    ax_rq2_gql.set_xticklabels([])

    ax_rq2_rest = fig.add_subplot(gs[1, 1])
    sns.violinplot(
        data=df[df["api_type"] == "REST"],
        y="response_size_bytes",
        color=PALETTE["REST"],
        inner="box",
        cut=0,
        ax=ax_rq2_rest,
    )
    ax_rq2_rest.set_title("RQ2 — REST Response Size", fontweight="bold")
    ax_rq2_rest.set_ylabel("Response Size (bytes)")
    ax_rq2_rest.set_xlabel("")
    ax_rq2_rest.set_xticklabels([])

    plt.tight_layout()
    path = OUTPUT_DIR / "fig2_violins.png"
    plt.savefig(path, bbox_inches="tight")
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Figure 3: Median bars by repository
# ---------------------------------------------------------------------------

def fig_bar_by_repo(df: pd.DataFrame):
    fig, axes = plt.subplots(2, 1, figsize=(16, 12))
    fig.suptitle("Median by Repository — GraphQL vs REST", fontsize=14, fontweight="bold")

    metrics = [
        ("response_time_ms", "Median Response Time (ms)", "RQ1"),
        ("response_size_bytes", "Median Response Size (bytes)", "RQ2"),
    ]

    for ax, (metric, ylabel, rq) in zip(axes, metrics):
        pivot = (
            df.groupby(["repo", "api_type"])[metric]
            .median()
            .unstack("api_type")
            .sort_values("REST", ascending=False)
        )
        pivot.plot(
            kind="bar",
            ax=ax,
            color=[PALETTE.get(c, "#888") for c in pivot.columns],
            width=0.7,
            edgecolor="white",
        )
        ax.set_title(f"{rq} — {ylabel}", fontweight="bold")
        ax.set_xlabel("Repository")
        ax.set_ylabel(ylabel)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
        ax.legend(title="API")

    plt.tight_layout()
    path = OUTPUT_DIR / "fig3_bars_by_repo.png"
    plt.savefig(path, bbox_inches="tight")
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Figure 4: Summary statistics tables
# ---------------------------------------------------------------------------

def fig_summary_tables(df: pd.DataFrame):
    fig, axes = plt.subplots(2, 1, figsize=(14, 7))
    fig.suptitle("Descriptive Statistics Tables", fontsize=14, fontweight="bold")

    configs = [
        ("response_time_ms", "ms", "RQ1 — Response Time"),
        ("response_size_bytes", "bytes", "RQ2 — Response Size"),
    ]

    for ax, (metric, unit, title) in zip(axes, configs):
        tbl = summary_table(df, metric, unit)
        ax.axis("off")
        col_labels = ["API"] + list(tbl.columns)
        cell_data = [[idx] + list(row) for idx, row in tbl.iterrows()]
        table = ax.table(
            cellText=cell_data,
            colLabels=col_labels,
            cellLoc="center",
            loc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.6)
        # Color header
        for j in range(len(col_labels)):
            table[(0, j)].set_facecolor("#4C72B0")
            table[(0, j)].set_text_props(color="white", fontweight="bold")
        # Color rows by API
        for i, (idx, _) in enumerate(tbl.iterrows(), start=1):
            color = PALETTE.get(idx, "#f0f0f0")
            for j in range(len(col_labels)):
                table[(i, j)].set_facecolor(color + "55")  # semi-transparent

        ax.set_title(title, fontweight="bold", pad=12)

    plt.tight_layout()
    path = OUTPUT_DIR / "fig4_summary_tables.png"
    plt.savefig(path, bbox_inches="tight")
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Figure 5: Temporal evolution (median by trial)
# ---------------------------------------------------------------------------

def fig_temporal_evolution(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle("Median Evolution by Trial (stability of measurements)", fontsize=14, fontweight="bold")

    metrics = [
        ("response_time_ms", "Median Response Time (ms)", "RQ1"),
        ("response_size_bytes", "Median Response Size (bytes)", "RQ2"),
    ]

    for ax, (metric, ylabel, rq) in zip(axes, metrics):
        trial_med = (
            df.groupby(["trial", "api_type"])[metric]
            .median()
            .unstack("api_type")
        )
        for api, color in PALETTE.items():
            if api in trial_med.columns:
                ax.plot(trial_med.index, trial_med[api], label=api, color=color, linewidth=1.8)

        ax.set_title(f"{rq} — Median by Trial", fontweight="bold")
        ax.set_xlabel("Trial")
        ax.set_ylabel(ylabel)
        ax.legend(title="API")

    plt.tight_layout()
    path = OUTPUT_DIR / "fig5_temporal.png"
    plt.savefig(path, bbox_inches="tight")
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Figure 6: Heatmap of medians by repository
# ---------------------------------------------------------------------------

def fig_heatmap(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle("Heatmap — Median by Repository and API", fontsize=14, fontweight="bold")

    metrics = [
        ("response_time_ms", "Response Time (ms)", "RQ1"),
        ("response_size_bytes", "Response Size (bytes)", "RQ2"),
    ]

    for ax, (metric, title, rq) in zip(axes, metrics):
        pivot = (
            df.groupby(["repo", "api_type"])[metric]
            .median()
            .unstack("api_type")
            .sort_values("REST", ascending=False)
        )
        sns.heatmap(
            pivot,
            annot=True,
            fmt=".0f",
            cmap="YlOrRd",
            linewidths=0.5,
            ax=ax,
            cbar_kws={"label": title},
        )
        ax.set_title(f"{rq} — {title}", fontweight="bold")
        ax.set_xlabel("API")
        ax.set_ylabel("Repository")

    plt.tight_layout()
    path = OUTPUT_DIR / "fig6_heatmap.png"
    plt.savefig(path, bbox_inches="tight")
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Figure 7: Consolidated panel with statistical results
# ---------------------------------------------------------------------------

def fig_statistical_panel(df: pd.DataFrame):
    fig = plt.figure(figsize=(14, 8))
    fig.suptitle(
        "GraphQL vs REST — Statistical Results (Mann-Whitney U, α = 0.05)",
        fontsize=14,
        fontweight="bold",
    )

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # Box plot RQ1
    ax1 = fig.add_subplot(gs[0, 0])
    sns.boxplot(data=df, x="api_type", y="response_time_ms", order=["REST", "GraphQL"],
                palette=PALETTE, width=0.5, ax=ax1,
                flierprops={"marker": "o", "markersize": 2, "alpha": 0.3})
    ax1.set_title("RQ1 — Time (ms)")
    ax1.set_xlabel("")
    ax1.set_ylabel("ms")

    # Box plot RQ2
    ax2 = fig.add_subplot(gs[1, 0])
    sns.boxplot(data=df, x="api_type", y="response_size_bytes", order=["REST", "GraphQL"],
                palette=PALETTE, width=0.5, ax=ax2,
                flierprops={"marker": "o", "markersize": 2, "alpha": 0.3})
    ax2.set_title("RQ2 — Size (bytes)")
    ax2.set_xlabel("")
    ax2.set_ylabel("bytes")

    # Text statistics RQ1
    ax3 = fig.add_subplot(gs[0, 1:])
    ax3.axis("off")
    u1, p1, r1, gql1, rest1 = mann_whitney(df, "response_time_ms")
    gql_med1 = np.median(gql1)
    rest_med1 = np.median(rest1)
    diff1 = (rest_med1 - gql_med1) / rest_med1 * 100
    sig1 = "SIGNIFICANT ✓" if p1 < 0.05 else "NOT significant"
    text_rq1 = (
        f"RQ1 — Response Time\n\n"
        f"  Median REST:    {rest_med1:.1f} ms\n"
        f"  Median GraphQL: {gql_med1:.1f} ms\n"
        f"  Difference:     {abs(diff1):.1f}%  ({'GraphQL faster' if diff1 > 0 else 'REST faster'})\n\n"
        f"  Mann-Whitney U = {u1:.0f}\n"
        f"  p-value = {p1:.4e}\n"
        f"  Effect size r = {r1:.4f}\n\n"
        f"  Result: {sig1}\n"
        f"  {'H₀ rejected — significant difference in time.' if p1 < 0.05 else 'H₀ not rejected — no significant difference.'}"
    )
    ax3.text(0.05, 0.95, text_rq1, transform=ax3.transAxes, fontsize=10.5,
             verticalalignment="top", fontfamily="monospace",
             bbox={"boxstyle": "round", "facecolor": "#EEF4FB", "alpha": 0.8})

    # Text statistics RQ2
    ax4 = fig.add_subplot(gs[1, 1:])
    ax4.axis("off")
    u2, p2, r2, gql2, rest2 = mann_whitney(df, "response_size_bytes")
    gql_med2 = np.median(gql2)
    rest_med2 = np.median(rest2)
    diff2 = (rest_med2 - gql_med2) / rest_med2 * 100
    sig2 = "SIGNIFICANT ✓" if p2 < 0.05 else "NOT significant"
    text_rq2 = (
        f"RQ2 — Response Size\n\n"
        f"  Median REST:    {rest_med2:.0f} bytes\n"
        f"  Median GraphQL: {gql_med2:.0f} bytes\n"
        f"  Reduction:      {abs(diff2):.1f}%  ({'GraphQL smaller' if diff2 > 0 else 'REST smaller'})\n\n"
        f"  Mann-Whitney U = {u2:.0f}\n"
        f"  p-value = {p2:.4e}\n"
        f"  Effect size r = {r2:.4f}\n\n"
        f"  Result: {sig2}\n"
        f"  {'H₀ rejected — significant difference in size.' if p2 < 0.05 else 'H₀ not rejected — no significant difference.'}"
    )
    ax4.text(0.05, 0.95, text_rq2, transform=ax4.transAxes, fontsize=10.5,
             verticalalignment="top", fontfamily="monospace",
             bbox={"boxstyle": "round", "facecolor": "#FEF5EC", "alpha": 0.8})

    path = OUTPUT_DIR / "fig7_statistical_panel.png"
    plt.savefig(path, bbox_inches="tight")
    print(f"Saved: {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("Loading data...")
    df = load_data()
    print(f"  {len(df)} valid measurements loaded.\n")

    print("Generating visualizations...\n")
    fig_boxplots(df)
    fig_violins(df)
    fig_bar_by_repo(df)
    fig_summary_tables(df)
    fig_temporal_evolution(df)
    fig_heatmap(df)
    fig_statistical_panel(df)

    print(f"\nAll figures saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
