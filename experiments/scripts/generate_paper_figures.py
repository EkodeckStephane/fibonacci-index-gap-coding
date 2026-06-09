from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "paper" / "artwork"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": 10,
    }
)


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def range_scaling() -> None:
    frame = pd.read_csv(ROOT / "results" / "integer_scaling.csv")
    frame = frame[frame["scope"] == "cumulative"]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    x = frame["end"] / 1_000_000
    ax.plot(
        x,
        100 * frame["gain_fraction"],
        marker="o",
        linestyle="-",
        color="#0072B2",
        label="Reduced",
    )
    ax.plot(
        x,
        100 * frame["equal_fraction"],
        marker="s",
        linestyle=":",
        color="#666666",
        label="Equal",
    )
    ax.plot(
        x,
        100 * frame["expansion_fraction"],
        marker="^",
        linestyle="--",
        color="#D55E00",
        label="Expanded",
    )
    ax.set_xlabel("Enumerated upper limit (millions)")
    ax.set_ylabel("Share of integers (%)")
    ax.legend(frameon=False, ncol=3)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "Figure_2_Range_Scaling")


def structural_controls() -> None:
    sparse = pd.read_csv(ROOT / "results" / "sparse_structure_baselines.csv")
    by_size = (
        sparse.groupby(["corpus", "block_size", "method"], as_index=False)
        .apply(
            lambda group: pd.Series(
                {
                    "ratio": group["encoded_bytes"].sum()
                    / group["original_bytes"].sum()
                }
            ),
            include_groups=False,
        )
    )
    summary = (
        by_size.sort_values("ratio")
        .groupby(["corpus", "method"], as_index=False)
        .first()
    )
    methods = ["fisa", "zero_block_bitmap", "zero_trim"]
    labels = ["FISA", "Zero bitmap", "Zero trim"]
    colors = ["#D55E00", "#0072B2", "#009E73"]
    hatches = ["///", "\\\\\\", "..."]
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    x = np.arange(2)
    width = 0.24
    for index, (method, label, color, hatch) in enumerate(
        zip(methods, labels, colors, hatches)
    ):
        method_rows = [
            summary[
                (summary["corpus"] == corpus)
                & (summary["method"] == method)
            ].iloc[0]
            for corpus in ("canterbury", "silesia")
        ]
        values = [float(row["ratio"]) for row in method_rows]
        bars = ax.bar(
            x + (index - 1) * width,
            values,
            width,
            label=label,
            color=color,
            edgecolor="black",
            hatch=hatch,
        )
        for bar, row in zip(bars, method_rows):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.001,
                f'{int(row["block_size"])} B',
                ha="center",
                va="bottom",
                fontsize=7,
            )
    ax.axhline(1.0, color="black", linewidth=0.9, linestyle="--")
    ax.set_xticks(x, ["Canterbury", "Silesia"])
    ax.set_ylabel("Weighted ratio")
    ax.set_ylim(0.88, 1.015)
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "Figure_4_Structural_Controls")


def gap_coding_comparison() -> None:
    frame = pd.read_csv(ROOT / "results" / "advanced_gap_codes_summary.csv")
    methods = [
        "shared_alphabet_hybrid",
        "huffman_complete",
        "rice_complete",
        "fipb_per_block",
    ]
    labels = ["Shared alphabet", "Huffman", "Rice", "Per-block FIPB"]
    colors = ["#009E73", "#0072B2", "#F0E442", "#D55E00"]
    hatches = ["", "///", "\\\\\\", "..."]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    x = np.arange(2)
    width = 0.19
    for index, (method, label, color, hatch) in enumerate(
        zip(methods, labels, colors, hatches)
    ):
        values = [
            float(
                frame[
                    (frame["corpus"] == corpus)
                    & (frame["method"] == method)
                ]["weighted_ratio"].iloc[0]
            )
            for corpus in ("canterbury", "silesia_sample")
        ]
        ax.bar(
            x + (index - 1.5) * width,
            values,
            width,
            label=label,
            color=color,
            edgecolor="black",
            hatch=hatch,
        )
    ax.axhline(1.0, color="black", linewidth=0.9, linestyle="--")
    ax.set_xticks(x, ["Canterbury", "Silesia sample"])
    ax.set_ylabel("Weighted encoded/original ratio")
    ax.set_ylim(0.85, 1.7)
    ax.legend(ncol=2, frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "Figure_3_Gap_Coding_Comparison")


def main() -> None:
    range_scaling()
    gap_coding_comparison()
    structural_controls()
    print(f"Wrote paper figures to {OUT}")


if __name__ == "__main__":
    main()
