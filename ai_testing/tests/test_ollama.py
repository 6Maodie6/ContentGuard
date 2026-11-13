
import json

import pytest
import requests

from ai_testing.clients.ollama_client import OllamaClient


class FakeResponse:
    """模拟 requests.post 返回的 Response 对象。"""

    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


def test_classify_success(monkeypatch):
    """正常情况：成功解析模型返回的 JSON。"""

    def fake_post(url, json, timeout):
        assert url.endswith("/api/generate")
        assert json["stream"] is False
        assert json["format"] == "json"
        assert timeout == 180

        return FakeResponse({
            "response": '{"label": "pass", "reason": "正常内容"}'
        })

    monkeypatch.setattr(
        "ai_testing.clients.ollama_client.requests.post",
        fake_post
    )

    client = OllamaClient()
    result = client.classify("今天天气很好")

    assert result == {
        "label": "pass",
        "reason": "正常内容"
    }


@pytest.mark.parametrize(
    "exception",
    [
        requests.Timeout("请求超时"),
        requests.ConnectionError("连接失败"),
    ]
)
def test_classify_request_error(monkeypatch, exception):
    """请求超时或连接失败时，应转换为 RuntimeError。"""

    def fake_post(*args, **kwargs):
        raise exception

    monkeypatch.setattr(
        "ai_testing.clients.ollama_client.requests.post",
        fake_post
    )

    client = OllamaClient()

    with pytest.raises(RuntimeError, match="Ollama"):
        client.classify("测试内容")


def test_classify_http_error(monkeypatch):
    """HTTP 状态码异常时，应转换为 RuntimeError。"""

    class ErrorResponse:
        def raise_for_status(self):
            raise requests.HTTPError("500 Server Error")

    def fake_post(*args, **kwargs):
        return ErrorResponse()

    monkeypatch.setattr(
        "ai_testing.clients.ollama_client.requests.post",
        fake_post
    )

    client = OllamaClient()

    with pytest.raises(RuntimeError, match="Ollama"):
        client.classify("测试内容")


def test_classify_invalid_json(monkeypatch):
    """模型返回的内容不是合法 JSON。"""

    def fake_post(*args, **kwargs):
        return FakeResponse({
            "response": "这不是 JSON"
        })

    monkeypatch.setattr(
        "ai_testing.clients.ollama_client.requests.post",
        fake_post
    )

    client = OllamaClient()

    with pytest.raises(ValueError, match="JSON"):
        client.classify("测试内容")


def test_classify_invalid_label(monkeypatch):
    """模型返回了不支持的标签。"""

    def fake_post(*args, **kwargs):
        return FakeResponse({
            "response": json.dumps({
                "label": "unknown",
                "reason": "测试理由"
            })
        })

    monkeypatch.setattr(
        "ai_testing.clients.ollama_client.requests.post",
        fake_post
    )

    client = OllamaClient()

    with pytest.raises(ValueError, match="标签"):
        client.classify("测试内容")


def test_classify_invalid_reason(monkeypatch):
    """模型返回的 reason 不是字符串。"""

    def fake_post(*args, **kwargs):
        return FakeResponse({
            "response": json.dumps({
                "label": "pass",
                "reason": 123
            })
        })

    monkeypatch.setattr(
        "ai_testing.clients.ollama_client.requests.post",
        fake_post
    )

    client = OllamaClient()

    with pytest.raises(ValueError, match="reason"):
        client.classify("测试内容")


@pytest.mark.parametrize("text", [123, None, [], {}])
def test_classify_invalid_input_type(text):
    """输入内容不是字符串。"""

    client = OllamaClient()

    with pytest.raises(TypeError):
        client.classify(text)


@pytest.mark.parametrize("text", ["", " ", "\n\t"])
def test_classify_empty_input(text):
    """输入内容为空或只有空白字符。"""

    client = OllamaClient()

    with pytest.raises(ValueError):
        client.classify(text)
