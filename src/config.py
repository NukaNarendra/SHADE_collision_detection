import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class ProjectConfig:
    def __init__(self):
        self.mode = os.getenv("PROJECT_MODE", "prod")

        # Multi-Provider Architecture:
        # NVIDIA NIM routes Nemotron, Laguna, GPT-OSS.
        # Mistral goes to Native SDK. Groq goes to Groq SDK. TokenRouter routes GLM.
        self.available_models = {
            "nemotron-120": {"model": "nvidia/nemotron-3-super-120b-a12b", "provider": "nvidia"},
            "mistral": {"model": "mistral-medium-latest", "provider": "mistral"},
            "laguna": {"model": "poolside/laguna-xs-2.1", "provider": "nvidia"},
            "nemetron-3.5": {"model": "nvidia/nemotron-3.5-lightning-30b-a3b", "provider": "nvidia"},
            "gpt-oss": {"model": "openai/gpt-oss-120b", "provider": "nvidia"},
            "groq-compound": {"model": "groq/compound", "provider": "groq"},
            "glm-5.3": {"model": "z-ai/glm-5.3-free", "provider": "tokenrouter"},
        }

        self.models = {
            # Nemotron remains our brilliant, free Monitor & Oracle
            "lead_agent": {"name": "nemotron-120", "enable_thinking": True},
            "oracle": {"name": "nemotron-120", "enable_thinking": True},
            "subagent": {"name": "mistral", "enable_thinking": False}
        }

        self.max_turns = 4
        self.data_dir = Path("data")
        self.logs_dir = Path("results/logs")
        self.metrics_dir = Path("results/metrics")

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.raw_data_path = self.data_dir / "raw_tasks.json"
        self.test_data_path = self.data_dir / "test_tasks.json"

    def get_model_config(self, role):
        role_config = self.models.get(role, self.models["subagent"])
        model_info = self.available_models[role_config["name"]]
        return {
            "model": model_info["model"],
            "provider": model_info["provider"],
            "enable_thinking": role_config["enable_thinking"]
        }


class DataProcessor:
    def __init__(self, config):
        self.config = config

    def download_and_preprocess(self):
        from datasets import load_dataset
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