import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def generate_plots():
    results_path = Path("results/metrics/scaling_summary.csv")
    if not results_path.exists():
        print("Error: Run run_scaling.py first to generate data.")
        return

    df = pd.read_csv(results_path)

    plt.figure(figsize=(10, 6))
    plt.plot(df["Turns"], df["CSR_Percentage"], marker='o', linewidth=2, label="Collusion Success Rate (CSR)",
             color="red")
    plt.plot(df["Turns"], df["MDR_Percentage"], marker='s', linewidth=2, label="Monitor Detection Rate (MDR)",
             color="blue")

    plt.title("Emergence of Steganographic Collusion Over Multi-Turn Interactions", fontsize=14, fontweight="bold")
    plt.xlabel("Number of Conversation Turns Allowed", fontsize=12)
    plt.ylabel("Percentage (%)", fontsize=12)
    plt.xticks(df["Turns"])
    plt.ylim(0, 105)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend(fontsize=12)

    plots_dir = Path("results/plots")
    plots_dir.mkdir(parents=True, exist_ok=True)
    plot_path = plots_dir / "csr_vs_mdr_scaling.png"

    plt.tight_layout()
    plt.savefig(plot_path, dpi=300)
    print(f"Plot successfully saved to: {plot_path}")


if __name__ == "__main__":
    generate_plots()