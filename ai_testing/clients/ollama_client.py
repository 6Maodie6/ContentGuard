import requests
import json

from ai_testing.prompts.prompt_v1 import SYSTEM_PROMPT


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "modelscope.cn/Qwen/Qwen3-8B-GGUF:Q4_K_M"
VALID_LABELS = {"pass", "review", "block"}


class OllamaClient:

    def __init__(
        self,
        model=MODEL_NAME,
        system_prompt=SYSTEM_PROMPT,
        temperature=0
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature

    def classify(self, text):

        if not isinstance(text, str):
            raise TypeError("待审核内容必须是字符串")

        if not text.strip():
            raise ValueError("待审核内容不能为空")

        prompt = f"""
{self.system_prompt}

现在请审核下面这段文本。

<待审核文本>
{text}
</待审核文本>
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": self.temperature
            }
        }

        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=180
            )
            response.raise_for_status()

        except requests.RequestException as e:
            raise RuntimeError(f"Ollama 请求失败：{e}") from e

        result = response.json()
        model_output = result.get("response", "")

        try:
            parsed = json.loads(model_output)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"模型没有返回有效 JSON：{model_output}"
            ) from e

        label = parsed.get("label")
        reason = parsed.get("reason")

        if label not in VALID_LABELS:
            raise ValueError(f"模型返回了无效审核标签：{label}")

        if not isinstance(reason, str):
            raise ValueError("模型返回的 reason 必须是字符串")

        return {
            "label": label,
            "reason": reason
        }