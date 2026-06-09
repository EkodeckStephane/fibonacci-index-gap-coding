from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.transform import reduce_indices, zeckendorf_indices
from fibcodec.universal_codes import (
    delta_bits,
    fibonacci_code_bits,
    gamma_bits,
    leb128_bits,
    rice_bits,
)


def main() -> None:
    rows = []
    for corpus in ("canterbury", "silesia_sample"):
        directory = ROOT / "data" / corpus
        for path in sorted(directory.iterdir()):
            if not path.is_file():
                continue
            data = path.read_bytes()
            for block_size in (64, 256, 512):
                gaps = []
                for start in range(0, len(data), block_size):
                    value = int.from_bytes(data[start : start + block_size], "big")
                    gaps.extend(reduce_indices(zeckendorf_indices(value)))
                original_bits = len(data) * 8
                methods = {
                    "fixed_binary_no_delimiters": sum(
                        max(1, value.bit_length()) for value in gaps
                    ),
                    "elias_gamma": sum(gamma_bits(value) for value in gaps),
                    "elias_delta": sum(delta_bits(value) for value in gaps),
                    "fibonacci_universal": sum(
                        fibonacci_code_bits(value) for value in gaps
                    ),
                    "leb128": sum(leb128_bits(value) for value in gaps),
                }
                rice_candidates = {
                    parameter: sum(rice_bits(value, parameter) for value in gaps)
                    for parameter in range(0, 17)
                }
                best_k = min(rice_candidates, key=rice_candidates.get) if gaps else 0
                methods[f"rice_oracle_k{best_k}"] = rice_candidates.get(best_k, 0)
                for method, bits in methods.items():
                    rows.append(
                        {
                            "corpus": corpus,
                            "file": path.name,
                            "block_size": block_size,
                            "method": method,
                            "symbols": len(gaps),
                            "coded_bits": bits,
                            "original_bits": original_bits,
                            "ratio": bits / original_bits if original_bits else 0,
                        }
                    )
                print(corpus, path.name, block_size, flush=True)
    output = ROOT / "results" / "universal_codes.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    import pandas as pd

    frame = pd.DataFrame(rows)
    summary = (
        frame.groupby(["corpus", "block_size", "method"], as_index=False)["ratio"]
        .mean()
        .sort_values(["corpus", "block_size", "ratio"])
    )
    summary.to_csv(ROOT / "results" / "universal_codes_summary.csv", index=False)
    (ROOT / "reports" / "06_universal_code_baselines.md").write_text(
        "# Universal-Code Baselines\n\n"
        "These are optimistic payload-only lengths on the same reduced-gap "
        "sequences. They exclude block framing and, for the Rice oracle, the "
        "parameter signalling cost. They therefore cannot be reported as "
        "complete compressor sizes.\n\n"
        + summary.to_markdown(index=False)
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

