from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.sparse_baselines import encode_zero_block_bitmap, encode_zero_trim


def main() -> None:
    native = pd.read_csv(ROOT / "results" / "native_fisa_block_sizes.csv")
    rows = []
    for record in native.itertuples(index=False):
        if record.corpus not in {"canterbury", "silesia"}:
            continue
        path = ROOT / "data" / record.corpus / record.file
        data = path.read_bytes()
        block_size = int(record.block_size)
        methods = {
            "fisa": int(record.encoded_bytes),
            "zero_block_bitmap": len(encode_zero_block_bitmap(data, block_size)),
            "zero_trim": len(encode_zero_trim(data, block_size)),
            "raw": len(data),
        }
        for method, encoded in methods.items():
            rows.append(
                {
                    "corpus": record.corpus,
                    "file": record.file,
                    "block_size": block_size,
                    "method": method,
                    "original_bytes": len(data),
                    "encoded_bytes": encoded,
                    "ratio": encoded / len(data),
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(ROOT / "results" / "sparse_structure_baselines.csv", index=False)
    summary = (
        frame.groupby(["corpus", "block_size", "method"], as_index=False)
        .apply(
            lambda group: pd.Series(
                {
                    "weighted_ratio": group["encoded_bytes"].sum()
                    / group["original_bytes"].sum()
                }
            ),
            include_groups=False,
        )
        .sort_values(["corpus", "block_size", "weighted_ratio"])
    )
    report = [
        "# Simple Sparse-Structure Baselines",
        "",
        "Both baselines are complete and exactly decodable. `zero_block_bitmap`",
        "stores a one-bit presence map and the raw nonzero blocks. `zero_trim`",
        "stores each block after removing its leading and trailing zero bytes.",
        "",
        "## Weighted corpus ratios",
        "",
        summary.to_markdown(index=False, floatfmt=".6f"),
        "",
        "## Favorable standard-corpus files",
        "",
        frame[
            frame["file"].isin(["ptt5", "mr", "mozilla"])
            & (frame["block_size"] == 256)
        ]
        .pivot(index=["corpus", "file"], columns="method", values="ratio")
        .reset_index()
        .to_markdown(index=False, floatfmt=".6f"),
        "",
    ]
    (ROOT / "reports" / "20_sparse_structure_baselines.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
