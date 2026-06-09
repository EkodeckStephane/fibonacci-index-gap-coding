from __future__ import annotations

import csv
import argparse
import math
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fibcodec.advanced_codes import (
    best_rice,
    decode_elias_fano,
    decode_huffman,
    encode_elias_fano,
    encode_huffman,
)
from fibcodec.codec import _encode_fib_payload
from fibcodec.shared_codec import decode as shared_decode
from fibcodec.shared_codec import encode as shared_encode
from fibcodec.transform import reduce_indices, zeckendorf_indices
from fibcodec.varint import encode_uvarint


def entropy_bound_bytes(values: list[int]) -> int:
    if not values:
        return 0
    counts = Counter(values)
    bits = sum(-count * math.log2(count / len(values)) for count in counts.values())
    return math.ceil(bits / 8)


def benchmark_gap_codes() -> list[dict]:
    rows = []
    for corpus in ("canterbury", "silesia_sample"):
        for path in sorted((ROOT / "data" / corpus).iterdir()):
            if not path.is_file():
                continue
            data = path.read_bytes()
            # The advanced comparison uses the 256-byte configuration selected
            # for the main ablation; block-size sensitivity is measured
            # separately by run_ablation.py.
            for block_size in (256,):
                totals = {
                    "fipb_per_block": 0,
                    "huffman_complete": 0,
                    "rice_complete": 0,
                    "entropy_oracle_payload": 0,
                }
                blocks = 0
                for start in range(0, len(data), block_size):
                    block = data[start : start + block_size]
                    gaps = reduce_indices(
                        zeckendorf_indices(int.from_bytes(block, "big"))
                    )
                    huffman = encode_huffman(gaps)
                    _, rice = best_rice(gaps)
                    if decode_huffman(huffman) != gaps:
                        raise AssertionError("Huffman roundtrip failed")
                    totals["fipb_per_block"] += len(_encode_fib_payload(block))
                    totals["huffman_complete"] += len(huffman)
                    totals["rice_complete"] += len(rice)
                    totals["entropy_oracle_payload"] += entropy_bound_bytes(gaps)
                    blocks += 1
                shared_start = time.perf_counter()
                shared = shared_encode(data, block_size)
                shared_seconds = time.perf_counter() - shared_start
                if shared_decode(shared) != data:
                    raise AssertionError("shared-alphabet roundtrip failed")
                totals["shared_alphabet_hybrid"] = len(shared)
                for method, encoded_bytes in totals.items():
                    rows.append(
                        {
                            "corpus": corpus,
                            "file": path.name,
                            "block_size": block_size,
                            "method": method,
                            "blocks": blocks,
                            "original_bytes": len(data),
                            "encoded_bytes": encoded_bytes,
                            "ratio": encoded_bytes / len(data) if data else 0,
                            "seconds": shared_seconds
                            if method == "shared_alphabet_hybrid"
                            else "",
                        }
                    )
                print(corpus, path.name, block_size, flush=True)
    return rows


def benchmark_integer_sequences() -> list[dict]:
    rows = []
    directory = ROOT / "data" / "integer_sequences"
    for path in sorted(directory.glob("*.txt")):
        values = [int(line) for line in path.read_text(encoding="ascii").splitlines()]
        encoded = encode_elias_fano(values)
        if decode_elias_fano(encoded) != values:
            raise AssertionError("Elias-Fano roundtrip failed")
        gaps = [values[0] + 1] + [
            current - previous for previous, current in zip(values, values[1:])
        ]
        huffman = encode_huffman(gaps)
        _, rice = best_rice(gaps)
        raw_u64 = len(values) * 8
        varint = sum(len(encode_uvarint(value)) for value in gaps)
        for method, encoded_bytes in {
            "raw_u64": raw_u64,
            "elias_fano_complete": len(encoded),
            "gap_huffman_complete": len(huffman),
            "gap_rice_complete": len(rice),
            "gap_leb128": varint,
        }.items():
            rows.append(
                {
                    "dataset": path.stem,
                    "count": len(values),
                    "maximum": values[-1] if values else 0,
                    "method": method,
                    "encoded_bytes": encoded_bytes,
                    "bits_per_integer": 8 * encoded_bytes / len(values),
                    "ratio_to_u64": encoded_bytes / raw_u64,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gaps-only", action="store_true")
    parser.add_argument("--sequences-only", action="store_true")
    args = parser.parse_args()
    run_gaps = not args.sequences_only
    run_sequences = not args.gaps_only

    gap_rows = benchmark_gap_codes() if run_gaps else []
    sequence_rows = benchmark_integer_sequences() if run_sequences else []
    if gap_rows:
        write_csv(ROOT / "results" / "advanced_gap_codes.csv", gap_rows)
    if sequence_rows:
        write_csv(ROOT / "results" / "integer_sequence_codes.csv", sequence_rows)

    import pandas as pd

    gap_path = ROOT / "results" / "advanced_gap_codes.csv"
    sequence_path = ROOT / "results" / "integer_sequence_codes.csv"
    if gap_path.exists():
        gaps = pd.read_csv(gap_path)
        gap_summary = (
            gaps.groupby(["corpus", "block_size", "method"], as_index=False)
            .agg(
                mean_ratio=("ratio", "mean"),
                weighted_ratio=(
                    "encoded_bytes",
                    lambda values: values.sum()
                    / gaps.loc[values.index, "original_bytes"].sum(),
                ),
            )
            .sort_values(["corpus", "block_size", "weighted_ratio"])
        )
        gap_summary.to_csv(
            ROOT / "results" / "advanced_gap_codes_summary.csv", index=False
        )
    else:
        gap_summary = pd.DataFrame()
    sequences = pd.read_csv(sequence_path) if sequence_path.exists() else pd.DataFrame()
    if not gap_summary.empty and not sequences.empty:
        (ROOT / "reports" / "13_advanced_baselines.md").write_text(
            "# Advanced Fibonacci and Integer-Sequence Baselines\n\n"
            "All rows labelled `complete` include their local codebook or parameter "
            "metadata and are decoded in the test suite. The entropy-oracle row is "
            "payload-only and is reported solely as a lower bound.\n\n"
            "## Fibonacci-derived gap streams\n\n"
            + gap_summary.to_markdown(index=False)
            + "\n\n## Monotone integer sequences\n\n"
            + sequences.to_markdown(index=False)
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
