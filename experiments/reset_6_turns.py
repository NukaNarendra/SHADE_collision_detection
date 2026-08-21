import pandas as pd
from pathlib import Path

def reset_condition():
    csv_path = Path("results/metrics/massive_scaling_raw_results.csv")
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        # Drop all rows where turns == 6
        df_cleaned = df[df["turns"] != 6]
        df_cleaned = df[df["turns"] != 4]
        df_cleaned.to_csv(csv_path, index=False)
        print(f"Successfully deleted bad 6-turn data.")
        print(f"Preserved {len(df_cleaned)} trials for the 2-turn and 4-turn conditions.")
    else:
        print("Could not find the CSV file.")

if __name__ == "__main__":
    reset_condition()