from __future__ import annotations

import csv
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
SOURCE = ROOT / "native" / "java" / "FisaBenchmark.java"
BUILD = ROOT / "native" / "java" / "build"
OUTPUT = ROOT / "results" / "native_fisa.csv"


def compile_java() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["javac", "--release", "8", "-d", str(BUILD), str(SOURCE)],
        check=True,
    )


def datasets() -> list[tuple[str, Path]]:
    selected: list[tuple[str, Path]] = []
    for corpus in ("canterbury", "silesia"):
        for path in sorted((ROOT / "data" / corpus).iterdir()):
            if path.is_file():
                selected.append((corpus, path))
    enwik8 = ROOT / "data" / "enwik8" / "enwik8"
    if enwik8.exists():
        selected.append(("enwik8", enwik8))
    return selected


def benchmark(corpus: str, path: Path, block_size: int) -> dict[str, object]:
    process = subprocess.run(
        [
            "java",
            "-Xmx6g",
            "-cp",
            str(BUILD),
            "FisaBenchmark",
            str(path),
            str(block_size),
            "0",
        ],
        check=True,
        text=True,
        capture_output=True,
        env={**os.environ, "LC_ALL": "C"},
    )
    lines = [line for line in process.stdout.splitlines() if line.strip()]
    if len(lines) != 2:
        raise RuntimeError(f"unexpected benchmark output for {path}: {process.stdout}")
    values = next(csv.DictReader(lines))
    return {"corpus": corpus, **values}


def main() -> None:
    compile_java()
    rows = []
    for corpus, path in datasets():
        row = benchmark(corpus, path, 256)
        rows.append(row)
        print(
            corpus,
            path.name,
            row["ratio"],
            row["encode_mib_s"],
            row["decode_mib_s"],
            flush=True,
        )
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
