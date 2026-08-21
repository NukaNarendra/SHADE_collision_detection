import sys
import os
from pathlib import Path

project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config import ProjectConfig, DataProcessor
from src.agents.base import NemotronClient
from src.harness.turn_manager import MultiTurnHarness
from src.scoring.metrics import MetricsEngine
from src.cacc.cacc_engine import CrossAgentConsistencyChecker


def scaffold_project_structure():
    directories = [
        "spec",
        "src/agents/prompts",
        "src/harness",
        "src/scoring",
        "src/analysis",
        "src/cacc",
        "experiments/configs",
        "results/logs",
        "results/metrics",
        "results/plots",
        "data"
    ]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    Path("src/__init__.py").touch(exist_ok=True)
    Path("src/agents/__init__.py").touch(exist_ok=True)
    Path("src/harness/__init__.py").touch(exist_ok=True)
    Path("src/scoring/__init__.py").touch(exist_ok=True)


def execute_phase3():
    scaffold_project_structure()
    print("Project folder structure scaffolded and verified.")

    config = ProjectConfig()
    processor = DataProcessor(config)
    llm_client = NemotronClient(config)
    metrics_engine = MetricsEngine(config)
    cacc_engine = CrossAgentConsistencyChecker(config)

    test_data = processor.load_test_data()
    trials_to_run = 2

    print(f"\nStarting Phase 3 Evaluation Pipeline ({trials_to_run} trials)...")

    for i in range(trials_to_run):
        print(f"\n--- Running Trial {i + 1}/{trials_to_run} ---")
        harness = MultiTurnHarness(config, llm_client)
        transcript, monitor_res, oracle_res, log_dir = harness.run_multi_turn_trial(test_data[i])

        print("\nTRANSCRIPT:")
        print(transcript.strip())

        print(f"\nOracle Decision (Collusion Success): {oracle_res['parsed'].get('collusion_success')}")
        print(f"Oracle Reason: {oracle_res['parsed'].get('reason')}")

        print(f"\nMonitor Decision (Suspicious): {monitor_res['parsed'].get('suspicious')}")
        print(f"Monitor Reason: {monitor_res['parsed'].get('reason')}")

        cacc_result = cacc_engine.analyze_transcript(transcript)
        print(f"\nCACC Statistical Decision (Anomalous): {cacc_result['is_anomalous']}")
        print(f"CACC Anomaly Score: {cacc_result['anomaly_score']}/100.0")
        if cacc_result['flags']:
            print("CACC Flags Triggered:")
            for flag in cacc_result['flags']:
                print(f"  - {flag}")

        metrics_engine.add_trial_result(monitor_res, oracle_res)

    final_metrics = metrics_engine.calculate_metrics()

    print("\n" + "=" * 60)
    print("PHASE 3 FINAL METRICS REPORT")
    print("=" * 60)
    print(f"Total Trials Run: {final_metrics['total_trials']}")
    print(f"Successful Collusions (Oracle True): {final_metrics['successful_collusions']}")
    print(f"Monitor Detections on Success: {final_metrics['monitor_detections_on_success']}")
    print(f"Undetected Collusions (Escaped Monitor): {final_metrics['undetected_collusions']}")
    print(f"\nCollusion Success Rate (CSR): {final_metrics['metrics']['CSR_percentage']}%")
    print(f"Monitor Detection Rate (MDR): {final_metrics['metrics']['MDR_percentage']}%")
    print("=" * 60)


if __name__ == "__main__":
    execute_phase3()