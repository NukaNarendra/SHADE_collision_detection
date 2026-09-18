import os
import time
import json
import random
import logging
from openai import OpenAI
from groq import Groq

# Polymorphic Mistral SDK Import (supports v1.x, v0.x, and namespace packages)
try:
    from mistralai.client import Mistral
except ImportError:
    try:
        from mistralai import Mistral
    except ImportError:
        try:
            from mistralai.client import MistralClient as Mistral
        except ImportError:
            Mistral = None

try:
    from google import genai
    from google.genai import types as genai_types
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class MultiProviderClient:
    """
    Intelligently routes traffic between NVIDIA APIs, Native SDKs (Groq, Mistral),
    and Google GenAI (Gemini).
    """

    def __init__(self, config):
        self.config = config

        # NVIDIA Client for Nemotron, DeepSeek, Llama, Laguna, StepFun, MiniMax, GPT-OSS
        self.nvidia_client = OpenAI(
            api_key=os.getenv("NVIDIA_API_KEY", ""),
            base_url="https://integrate.api.nvidia.com/v1"
        )

        # Native Clients for Groq (Multi-Key Round-Robin Rotation) and Mistral
        raw_groq_keys = [
            os.getenv("GROQ_API_KEY", ""),
            os.getenv("GROQ_API_KEY_2", ""),
            os.getenv("GROQ_API_KEY_3", ""),
            os.getenv("GROQ_API_KEY_1", "")
        ]
        self.groq_api_keys = []
        for k in raw_groq_keys:
            cleaned_k = k.strip() if k else ""
            if cleaned_k and cleaned_k not in self.groq_api_keys:
                self.groq_api_keys.append(cleaned_k)

        if not self.groq_api_keys:
            self.groq_api_keys = [""]

        self.groq_clients = [Groq(api_key=k) for k in self.groq_api_keys]
        self.groq_client = self.groq_clients[0]
        self._groq_client_idx = 0
        logger.info(f"Initialized MultiProviderClient with {len(self.groq_clients)} active Groq API key(s) for round-robin rotation.")
        
        mistral_key = os.getenv("MISTRAL_API_KEY", "")
        if Mistral is not None and mistral_key:
            try:
                self.mistral_client = Mistral(api_key=mistral_key)
            except Exception as e:
                logger.warning(f"Mistral client init fallback: {e}")
                self.mistral_client = None
        else:
            self.mistral_client = None

        # Google GenAI Client for Gemini 2.5 Pro
        gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        if GOOGLE_GENAI_AVAILABLE and gemini_api_key:
            self.google_client = genai.Client(api_key=gemini_api_key)
        else:
            self.google_client = None

        # TokenRouter Client for GLM and open models
        self.tokenrouter_client = OpenAI(
            api_key=os.getenv("TOKENROUTER_API_KEY", ""),
            base_url="https://api.tokenrouter.com/v1"
        )

    def _get_next_groq_client(self):
        """Returns the next Groq client in round-robin order with key index."""
        idx = self._groq_client_idx % len(self.groq_clients)
        client = self.groq_clients[idx]
        self._groq_client_idx = (self._groq_client_idx + 1) % len(self.groq_clients)
        return client, idx + 1

    def generate_response(self, provider, model, messages, enable_thinking=False, temperature=0.3):
        max_retries = 4
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                full_content = ""
                full_reasoning = ""

                # --- NVIDIA ROUTE (Nemotron & DeepSeek) ---
                if provider == "nvidia":
                    extra_body = {}
                    if enable_thinking:
                        extra_body = {"chat_template_kwargs": {"enable_thinking": True}}

                    completion = self.nvidia_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        stream=False,
                        extra_body=extra_body if extra_body else None
                    )
                    msg = completion.choices[0].message
                    full_content = msg.content or ""
                    full_reasoning = getattr(msg, "reasoning_content", "")

                # --- GROQ ROUTE (Standard + Compound Model Support with Round-Robin Rotation) ---
                elif provider == "groq":
                    groq_client, key_num = self._get_next_groq_client()
                    logger.info(f"[groq] Dispatching request with Groq API Key #{key_num}/{len(self.groq_clients)}")

                    # Context window management: retain system prompt + most recent 3 messages
                    if len(messages) > 4:
                        groq_messages = [messages[0]] + messages[-3:]
                    else:
                        groq_messages = messages

                    if "compound" in model:
                        # Groq Compound: streaming-only model with agentic tool support
                        completion = groq_client.chat.completions.create(
                            model=model,
                            messages=groq_messages,
                            temperature=temperature,
                            max_completion_tokens=2048,
                            stream=True,
                            compound_custom={"tools": {"enabled_tools": ["web_search", "code_interpreter"]}}
                        )
                        chunks = []
                        for chunk in completion:
                            delta = chunk.choices[0].delta
                            if delta and delta.content:
                                chunks.append(delta.content)
                        full_content = "".join(chunks)
                    else:
                        # Standard Groq models (non-streaming)
                        completion = groq_client.chat.completions.create(
                            model=model,
                            messages=groq_messages,
                            temperature=temperature,
                            max_completion_tokens=768,
                            stream=False
                        )
                        full_content = completion.choices[0].message.content or ""

                # --- MISTRAL ROUTE ---
                elif provider == "mistral":
                    completion = self.mistral_client.chat.complete(
                        model=model,
                        messages=messages,
                        temperature=temperature
                    )
                    full_content = completion.choices[0].message.content or ""

                # --- GOOGLE GENAI (GEMINI 2.5 PRO) ROUTE ---
                elif provider == "google":
                    if not self.google_client:
                        raise ValueError("Google GenAI client not initialized. Ensure GEMINI_API_KEY is set.")

                    # Format messages for Gemini
                    system_instruction = None
                    contents = []
                    for m in messages:
                        role = m.get("role")
                        content = m.get("content", "")
                        if role == "system":
                            system_instruction = content
                        elif role == "user":
                            contents.append(f"User: {content}")
                        elif role == "assistant":
                            contents.append(f"Assistant: {content}")

                    prompt_text = "\n\n".join(contents)
                    config_params = {"temperature": temperature}
                    if system_instruction:
                        config_params["system_instruction"] = system_instruction

                    response = self.google_client.models.generate_content(
                        model=model,
                        contents=prompt_text,
                        config=config_params
                    )
                    full_content = response.text or ""

                # --- TOKENROUTER (GLM-5.3) ROUTE ---
                elif provider == "tokenrouter":
                    stream = self.tokenrouter_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        stream=True,
                        stream_options={"include_usage": True},
                        extra_body={}
                    )
                    content_parts = []
                    for chunk in stream:
                        if chunk.choices:
                            delta = chunk.choices[0].delta
                            if delta and delta.content:
                                content_parts.append(delta.content)
                    full_content = "".join(content_parts)

                duration = time.time() - start_time
                return {
                    "content": full_content,
                    "reasoning": full_reasoning,
                    "duration": duration,
                    "status": "success"
                }

            except Exception as e:
                err_str = str(e)
                if attempt == max_retries - 1:
                    logger.error(f"[{provider}] Final failure after {max_retries} attempts: {err_str}")
                    return {"content": "", "reasoning": "", "duration": 0, "status": "error", "error": err_str}

                # Adaptive backoff specifically for Groq 429/413 rate limits
                if provider == "groq":
                    backoff = 6.0 * (2 ** attempt) + random.uniform(1.0, 3.0)
                    logger.warning(f"[groq] Encountered limit: {err_str[:120]}... Backing off for {backoff:.1f}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(backoff)
                else:
                    backoff = (3 ** attempt) + random.uniform(0.5, 2.0)
                    time.sleep(backoff)


class BaseAgent:
    def __init__(self, name, role, config, llm_client, temperature=0.3):
        self.name = name
        self.role = role
        self.config = config
        self.llm = llm_client

        role_config = config.get_model_config(role)
        self.model = role_config["model"]
        self.provider = role_config["provider"]
        self.enable_thinking = role_config["enable_thinking"]
        self.temperature = temperature
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_response(self):
        response = self.llm.generate_response(
            provider=self.provider,
            model=self.model,
            messages=self.history,
            enable_thinking=self.enable_thinking,
            temperature=self.temperature
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