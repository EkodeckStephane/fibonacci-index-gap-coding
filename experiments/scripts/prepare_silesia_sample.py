from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "silesia"
TARGET = ROOT / "data" / "silesia_sample"
SAMPLE_BYTES = 65_536


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for source in sorted(SOURCE.iterdir()):
        if source.is_file():
            payload = source.read_bytes()[:SAMPLE_BYTES]
            (TARGET / source.name).write_bytes(payload)
            print(source.name, len(payload))


if __name__ == "__main__":
    main()
