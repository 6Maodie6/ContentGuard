
import json

import pytest

from ai_testing.stability import stability


class FakeOllamaClient:
    """模拟 OllamaClient，按顺序返回预设的预测结果。"""

    def __init__(self, results):
        self.results = results
        self.call_count = 0

    def classify(self, text):
        result = self.results[self.call_count]
        self.call_count += 1
        return result


def create_dataset(tmp_path, cases):
    """创建临时 Golden Dataset。"""

    path = tmp_path / "golden_dataset.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(cases, file, ensure_ascii=False)

    return path


def test_load_prompt_success():
    """支持加载 v1 到 v4 的 Prompt。"""

    assert isinstance(stability.load_prompt("v1"), str)
    assert isinstance(stability.load_prompt("v2"), str)
    assert isinstance(stability.load_prompt("v3"), str)
    assert isinstance(stability.load_prompt("v4"), str)


def test_load_prompt_invalid_version():
    """不支持的 Prompt 版本应抛出 ValueError。"""

    with pytest.raises(ValueError):
        stability.load_prompt("v5")


@pytest.mark.parametrize(
    "repeats, max_cases",
    [
        (1, 3),
        (0, 3),
        (3, 0),
        (3, -1),
    ]
)
def test_run_stability_test_invalid_parameters(repeats, max_cases):
    """重复次数和样本数量必须满足要求。"""

    with pytest.raises(ValueError):
        stability.run_stability_test(
            repeats=repeats,
            max_cases=max_cases
        )


def test_run_stability_test_no_valid_cases(
    tmp_path,
    monkeypatch
):
    """数据集没有有效三分类样本时应报错。"""

    dataset = [
        {
            "id": "AI001",
            "text": "测试内容",
            "expected": "invalid"
        },
        {
            "id": "AI002",
            "text": "",
            "expected": "pass"
        }
    ]

    dataset_path = create_dataset(tmp_path, dataset)

    monkeypatch.setattr(
        stability,
        "DATASET_PATH",
        dataset_path
    )

    with pytest.raises(ValueError, match="有效测试样本"):
        stability.run_stability_test(
            repeats=2,
            max_cases=3
        )


def test_run_stability_test_success(
    tmp_path,
    monkeypatch
):
    """验证重复预测、标签统计、一致率和报告保存。"""

    dataset = [
        {
            "id": "AI001",
            "text": "正常内容",
            "expected": "pass"
        },
        {
            "id": "AI002",
            "text": "违规内容",
            "expected": "block"
        },
        {
            "id": "AI003",
            "text": "无效标签样本",
            "expected": "invalid"
        }
    ]

    dataset_path = create_dataset(tmp_path, dataset)
    output_path = tmp_path / "reports" / "stability.json"

    monkeypatch.setattr(
        stability,
        "DATASET_PATH",
        dataset_path
    )

    monkeypatch.setattr(
        stability,
        "load_prompt",
        lambda version: "测试 Prompt"
    )

    fake_client = FakeOllamaClient([
        # AI001：三次预测完全一致
        {"label": "pass", "reason": "正常"},
        {"label": "pass", "reason": "正常"},
        {"label": "pass", "reason": "正常"},

        # AI002：两次 block，一次 review
        {"label": "block", "reason": "违规"},
        {"label": "block", "reason": "违规"},
        {"label": "review", "reason": "需要复核"},
    ])

    class FakeClientFactory:
        def __init__(self, **kwargs):
            self.client = fake_client

        def classify(self, text):
            return self.client.classify(text)

    monkeypatch.setattr(
        stability,
        "OllamaClient",
        FakeClientFactory
    )

    report = stability.run_stability_test(
        repeats=3,
        max_cases=3,
        output_path=output_path,
        temperature=0
    )

    assert report["total_cases"] == 2
    assert report["stable_cases"] == 1
    assert report["unstable_cases"] == 1

    assert report["case_stability_rate"] == 0.5
    assert report["average_agreement_rate"] == pytest.approx(5 / 6)

    first_case = report["prediction_details"][0]
    assert first_case["predictions"] == ["pass", "pass", "pass"]
    assert first_case["stable"] is True
    assert first_case["agreement_rate"] == 1

    second_case = report["prediction_details"][1]
    assert second_case["prediction_counts"] == {
        "block": 2,
        "review": 1
    }
    assert second_case["stable"] is False
    assert second_case["agreement_rate"] == pytest.approx(2 / 3)

    assert fake_client.call_count == 6
    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        saved_report = json.load(file)

    assert saved_report["total_cases"] == 2
    assert saved_report["prompt_version"] == "v2"


def test_run_stability_test_default_output_path(
    tmp_path,
    monkeypatch
):
    """不传 output_path 时，应使用默认报告目录。"""

    dataset = [
        {
            "id": "AI001",
            "text": "正常内容",
            "expected": "pass"
        }
    ]

    dataset_path = create_dataset(tmp_path, dataset)

    monkeypatch.setattr(
        stability,
        "DATASET_PATH",
        dataset_path
    )

    monkeypatch.setattr(
        stability,
        "REPORT_DIR",
        tmp_path / "default_reports"
    )

    monkeypatch.setattr(
        stability,
        "load_prompt",
        lambda version: "测试 Prompt"
    )

    class FakeClient:
        def __init__(self, **kwargs):
            pass

        def classify(self, text):
            return {
                "label": "pass",
                "reason": "正常"
            }

    monkeypatch.setattr(
        stability,
        "OllamaClient",
        FakeClient
    )

    report = stability.run_stability_test(
        repeats=2,
        max_cases=1
    )

    assert report["total_cases"] == 1

    report_files = list(
        (tmp_path / "default_reports").glob("stability_*.json")
    )

    assert len(report_files) == 1


def test_run_stability_test_model_error(
    tmp_path,
    monkeypatch
):
    """模型调用失败时，异常应正常向外传递。"""

    dataset = [
        {
            "id": "AI001",
            "text": "测试内容",
            "expected": "pass"
        }
    ]

    dataset_path = create_dataset(tmp_path, dataset)

    monkeypatch.setattr(
        stability,
        "DATASET_PATH",
        dataset_path
    )

    monkeypatch.setattr(
        stability,
        "load_prompt",
        lambda version: "测试 Prompt"
    )

    class ErrorClient:
        def __init__(self, **kwargs):
            pass

        def classify(self, text):
            raise RuntimeError("模拟模型请求失败")

    monkeypatch.setattr(
        stability,
        "OllamaClient",
        ErrorClient
    )

    with pytest.raises(RuntimeError, match="模拟模型请求失败"):
        stability.run_stability_test(
            repeats=2,
            max_cases=1,
            output_path=tmp_path / "error.json"
        )
