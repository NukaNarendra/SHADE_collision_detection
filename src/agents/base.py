import time
import json
from openai import OpenAI


class NemotronClient:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key
        )

    def generate_response(self, model, messages, enable_thinking=False, temperature=0.3):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                extra_body = {}
                if enable_thinking:
                    extra_body = {
                        "chat_template_kwargs": {"enable_thinking": True},
                        "reasoning_budget": 8192
                    }

                completion = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    top_p=0.9,
                    max_tokens=8192,
                    extra_body=extra_body if extra_body else None,
                    stream=True
                )

                full_reasoning = ""
                full_content = ""

                for chunk in completion:
                    if not chunk.choices:
                        continue

                    delta = chunk.choices[0].delta
                    reasoning = getattr(delta, "reasoning_content", None)

                    if reasoning:
                        full_reasoning += reasoning
                    if delta.content is not None:
                        full_content += delta.content

                duration = time.time() - start_time
                return {
                    "content": full_content,
                    "reasoning": full_reasoning,
                    "duration": duration,
                    "status": "success"
                }

            except Exception as e:
                if attempt == max_retries - 1:
                    return {"content": "", "reasoning": "", "duration": 0, "status": "error", "error": str(e)}
                time.sleep(2 ** attempt)


class BaseAgent:
    def __init__(self, name, role, config, llm_client, temperature=0.3):
        self.name = name
        self.role = role
        self.config = config
        self.llm = llm_client

        role_config = config.get_model_config(role)
        self.model = role_config["model"]
        self.enable_thinking = role_config["enable_thinking"]
        self.temperature = temperature
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_response(self):
        response = self.llm.generate_response(
            self.model,
            self.history,
            self.enable_thinking,
            self.temperature
        )
        if response["status"] == "success":
            self.add_message("assistant", response["content"])
        return response

    def parse_json_response(self, content):
        try:
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            if start_idx != -1 and end_idx != -1:
                clean_content = content[start_idx:end_idx]
                return json.loads(clean_content)
            return json.loads(content)
        except:
            return None