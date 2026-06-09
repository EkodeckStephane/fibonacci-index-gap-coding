from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BLOCK_SIZE = 256


def block_features(data: bytes) -> dict[str, float]:
    blocks = [data[start : start + BLOCK_SIZE] for start in range(0, len(data), BLOCK_SIZE)]
    zero_blocks = 0
    leading = []
    trailing = []
    nonzero = []
    unique = []
    for block in blocks:
        zero_blocks += int(not any(block))
        first = next((index for index, value in enumerate(block) if value), len(block))
        last = next(
            (index for index, value in enumerate(reversed(block)) if value),
            len(block),
        )
        leading.append(first / len(block))
        trailing.append(last / len(block))
        nonzero.append(sum(value != 0 for value in block) / len(block))
        unique.append(len(set(block)))
    return {
        "zero_byte_fraction": data.count(0) / len(data),
        "zero_block_fraction": zero_blocks / len(blocks),
        "mean_leading_zero_fraction": float(np.mean(leading)),
        "mean_trailing_zero_fraction": float(np.mean(trailing)),
        "mean_nonzero_fraction": float(np.mean(nonzero)),
        "median_nonzero_fraction": float(np.median(nonzero)),
        "mean_unique_bytes": float(np.mean(unique)),
    }


def main() -> None:
    ratios = pd.read_csv(ROOT / "results" / "native_fisa.csv")
    rows = []
    for corpus in ("canterbury", "silesia"):
        for path in sorted((ROOT / "data" / corpus).iterdir()):
            if not path.is_file():
                continue
            ratio = float(
                ratios.loc[
                    (ratios["corpus"] == corpus) & (ratios["file"] == path.name),
                    "ratio",
                ].iloc[0]
            )
            rows.append(
                {
                    "corpus": corpus,
                    "file": path.name,
                    "ratio": ratio,
                    **block_features(path.read_bytes()),
                }
            )
    frame = pd.DataFrame(rows).sort_values("ratio")
    frame.to_csv(ROOT / "results" / "favorable_block_features.csv", index=False)
    correlations = (
        frame.drop(columns=["corpus", "file"])
        .corr(method="spearman")["ratio"]
        .drop("ratio")
        .sort_values()
    )
    report = [
        "# Block-Level Characterization of Favorable Files",
        "",
        "Features use the same 256-byte partition as the complete FISA stream.",
        "",
        "## Files ordered by FISA ratio",
        "",
        frame.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Spearman association with complete ratio",
        "",
        correlations.rename("rho").to_frame().to_markdown(floatfmt=".6f"),
        "",
        "The sample contains only 23 standard-corpus files. Correlations are",
        "descriptive and are used to formulate hypotheses, not as inferential",
        "evidence.",
        "",
    ]
    (ROOT / "reports" / "19_favorable_block_features.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print(frame.head(8).to_string(index=False))
    print(correlations.to_string())


if __name__ == "__main__":
    main()
