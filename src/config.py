import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class ProjectConfig:
    def __init__(self):
        # We exclusively use NVIDIA to keep this entirely free/accessible for you
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.mode = os.getenv("PROJECT_MODE", "dev")

        # Universal configuration for all agents using FREE NVIDIA NIM endpoints
        # We can now test Meta, Google, and DeepSeek for $0
        self.available_models = {
            "nemotron": "nvidia/nemotron-3-super-120b-a12b",
            "llama": "meta/llama-3.3-70b-instruct",
            "gemma": "google/gemma-4-31b-it",
            "deepseek": "deepseek-ai/deepseek-v4-flash-0731"
        }

        # Change these names to test different architectures against each other
        self.models = {
            "lead_agent": {
                "name": self.available_models["nemotron"],
                "enable_thinking": True,
            },
            "subagent": {
                "name": self.available_models["nemotron"],  # Try changing this to "llama" or "gemma" later!
                "enable_thinking": False,
            },
            "oracle": {
                "name": self.available_models["nemotron"],
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
        return {
            "model": role_config["name"],
            "provider": "nvidia",
            "enable_thinking": role_config["enable_thinking"]
        }