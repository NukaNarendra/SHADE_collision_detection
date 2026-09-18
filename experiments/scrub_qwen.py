"""
SHADE Project - Qwen/Groq Data Scrubber
=========================================
Removes all rows containing "Qwen" or "Groq" from cross-architecture CSVs.
The Groq free-tier API collapsed under sustained 429 rate limiting during
the N=50 scaling sweep, producing unreliable partial data that must be excised
before final publication analysis.

Usage:
    python experiments/scrub_qwen.py
"""
import pandas as pd
from pathlib import Path

METRICS_DIR = Path("results/metrics")

TARGET_FILES = [
    METRICS_DIR / "cross_architecture_results.csv",
    METRICS_DIR / "final_v3_cross_architecture_metrics.csv",
]


def contains_qwen_or_groq(architecture_value: str) -> bool:
    """Returns True if the architecture string references Qwen or Groq."""
    val = str(architecture_value).lower()
    return "qwen" in val or "groq" in val


def scrub_file(filepath: Path) -> None:
    if not filepath.exists():
        print(f"  [SKIP] {filepath} does not exist.")
        return

    df = pd.read_csv(filepath)
    before_count = len(df)

    mask = df["Architecture"].apply(contains_qwen_or_groq)
    removed_count = mask.sum()

    clean_df = df[~mask]
    clean_df.to_csv(filepath, index=False)

    print(f"  [DONE] {filepath.name}")
    print(f"         Rows before: {before_count}")
    print(f"         Qwen/Groq rows removed: {removed_count}")
    print(f"         Rows after:  {len(clean_df)}")
    print()


def main():
    print("=" * 60)
    print("SHADE DATA SCRUBBER: Excising all Qwen/Groq contamination")
    print("=" * 60)
    print()

    for f in TARGET_FILES:
        scrub_file(f)

    # Verification pass
    print("=" * 60)
    print("VERIFICATION: Architecture distribution after scrub")
    print("=" * 60)
    primary = METRICS_DIR / "cross_architecture_results.csv"
    if primary.exists():
        df = pd.read_csv(primary)
        print(df["Architecture"].value_counts().to_string())
        print(f"\nTotal clean rows: {len(df)}")
    print("\nScrub complete. Qwen/Groq fully excised.")


if __name__ == "__main__":
    main()
