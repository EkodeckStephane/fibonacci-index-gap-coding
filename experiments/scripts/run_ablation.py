from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.codec import _encode_fib_payload
from fibcodec.transform import reduce_indices, zeckendorf_indices


def main() -> None:
    rows = []
    for corpus in ("synthetic", "canterbury", "silesia_sample"):
        corpus_root = ROOT / "data" / corpus
        if not corpus_root.exists():
            continue
        for path in sorted(corpus_root.iterdir()):
            if not path.is_file():
                continue
            data = path.read_bytes()
            for block_size in (16, 64, 256, 512):
                totals = {
                    "direct_binary_bits": 0,
                    "index_bits": 0,
                    "gap_bits": 0,
                    "complete_payload_bits": 0,
                }
                blocks = 0
                for start in range(0, len(data), block_size):
                    block = data[start : start + block_size]
                    value = int.from_bytes(block, "big")
                    indices = zeckendorf_indices(value)
                    gaps = reduce_indices(indices)
                    totals["direct_binary_bits"] += len(block) * 8
                    totals["index_bits"] += sum(max(1, value.bit_length()) for value in indices)
                    totals["gap_bits"] += sum(max(1, value.bit_length()) for value in gaps)
                    totals["complete_payload_bits"] += len(_encode_fib_payload(block)) * 8
                    blocks += 1
                original = totals["direct_binary_bits"]
                rows.append(
                    {
                        "corpus": corpus,
                        "file": path.name,
                        "block_size": block_size,
                        "blocks": blocks,
                        **totals,
                        "index_ratio": totals["index_bits"] / original if original else 0,
                        "gap_ratio": totals["gap_bits"] / original if original else 0,
                        "complete_payload_ratio": (
                            totals["complete_payload_bits"] / original if original else 0
                        ),
                    }
                )
                print(corpus, path.name, block_size, flush=True)
    output = ROOT / "results" / "ablation.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()

