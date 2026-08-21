import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datasets import load_dataset

load_dotenv()


class ProjectConfig:
    def __init__(self):
        self.mode = os.getenv("PROJECT_MODE", "dev")
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.models = {
            "lead_agent": {
                "dev": "nvidia/nemotron-3-super-120b-a12b",
                "prod": "nvidia/nemotron-3-ultra-550b-a55b",
                "enable_thinking": True,
            },
            "subagent": {
                "dev": "nvidia/nemotron-3-super-120b-a12b",
                "prod": "nvidia/nemotron-3-super-120b-a12b",
                "enable_thinking": False,
            },
            "oracle": {
                "dev": "nvidia/nemotron-3-super-120b-a12b",
                "prod": "nvidia/nemotron-3-ultra-550b-a55b",
                "enable_thinking": True,
            }
        }
        self.max_turns = 4
        self.data_dir = Path("data")
        self.logs_dir = Path("results/logs")
        self.metrics_dir = Path("results/metrics")
        self.raw_data_path = self.data_dir / "raw_tasks.json"
        self.test_data_path = self.data_dir / "test_tasks.json"

    def get_model_config(self, role):
        role_config = self.models.get(role, self.models["subagent"])
        model_name = role_config[self.mode]
        return {
            "model": model_name,
            "enable_thinking": role_config["enable_thinking"]
        }


class DataProcessor:
    def __init__(self, config):
        self.config = config

    def download_and_preprocess(self):
        dataset = load_dataset("openai/gsm8k", "main", split="train[:100]")
        processed_data = []
        for row in dataset:
            processed_data.append({
                "id": str(hash(row["question"])),
                "question": row["question"],
                "answer": row["answer"].split("####")[-1].strip(),
                "full_context": row["answer"]
            })

        train_split = processed_data[:80]
        test_split = processed_data[80:]

        with open(self.config.raw_data_path, "w", encoding="utf-8") as f:
            json.dump(train_split, f, indent=4)

        with open(self.config.test_data_path, "w", encoding="utf-8") as f:
            json.dump(test_split, f, indent=4)

        return train_split, test_split

    def load_test_data(self):
        if not self.config.test_data_path.exists():
            self.download_and_preprocess()
        with open(self.config.test_data_path, "r", encoding="utf-8") as f:
            return json.load(f)