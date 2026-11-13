
import json

from ai_testing.evaluation import evaluator

import pytest
import runpy
import sys

from ai_testing.clients import ollama_client


def test_run_evaluation_generates_report(tmp_path, monkeypatch):
    """验证评估流程能读取数据、计算指标并生成报告。"""

    dataset = [
        {
            "id": "AI001",
            "text": "正常内容",
            "expected": "pass"
        },
        {
            "id": "AI002",
            "text": "需要人工审核",
            "expected": "review"
        },
        {
            "id": "AI003",
            "text": "违规内容",
            "expected": "block"
        },
        {
            "id": "AI004",
            "text": "",
            "expected": "invalid"
        }
    ]

    dataset_path = tmp_path / "golden_dataset.json"
    report_path = tmp_path / "evaluation_report.json"

    dataset_path.write_text(
        json.dumps(dataset, ensure_ascii=False),
        encoding="utf-8"
    )

    # 将评估程序使用的数据集路径替换为临时路径
    monkeypatch.setattr(
        evaluator,
        "DATASET_PATH",
        dataset_path
    )

    # 使用 mock 模式运行，并指定报告保存位置
    report = evaluator.run_evaluation(
        mode="mock",
        output_path=report_path
    )

    # 验证有效样本和异常样本数量
    assert report["total_dataset_cases"] == 4
    assert report["evaluated_cases"] == 3
    assert report["invalid_cases"] == 1
    assert report["invalid_case_ids"] == ["AI004"]

    # 验证报告文件确实生成
    assert report_path.exists()

    # 验证保存的 JSON 内容
    saved_report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    assert saved_report["evaluation_type"] == "mock"
    assert saved_report["metrics"]["total"] == 3


def test_load_dataset_rejects_non_list(tmp_path, monkeypatch):
    """JSON 文件内容不是数组时，应该抛出 ValueError。"""

    dataset_path = tmp_path / "invalid.json"
    dataset_path.write_text('{"id": "AI001"}', encoding="utf-8")

    monkeypatch.setattr(evaluator, "DATASET_PATH", dataset_path)

    with pytest.raises(ValueError, match="必须是 JSON 数组"):
        evaluator.load_dataset()


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_load_prompt_success(version):
    """验证支持的 Prompt 版本都能成功加载。"""

    prompt = evaluator.load_prompt(version)

    assert isinstance(prompt, str)
    assert prompt.strip()


def test_load_prompt_invalid_version():
    """非法 Prompt 版本应该抛出异常。"""

    with pytest.raises(ValueError, match="只能是 v1 或 v2"):
        evaluator.load_prompt("v3")


def test_run_evaluation_invalid_mode():
    """不支持的评估模式应该被拒绝。"""

    with pytest.raises(ValueError, match="只能是 mock 或 ollama"):
        evaluator.run_evaluation(mode="invalid")


def test_run_evaluation_invalid_prompt_version():
    """不支持的 Prompt 版本应该被拒绝。"""

    with pytest.raises(ValueError, match="只能是 v1 或 v2"):
        evaluator.run_evaluation(prompt_version="v3")


def test_run_evaluation_missing_required_field(tmp_path, monkeypatch):
    """测试用例缺少 text 或 expected 时应该报错。"""

    dataset = [
        {
            "id": "AI001",
            "text": "正常内容"
        }
    ]

    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(
        json.dumps(dataset, ensure_ascii=False),
        encoding="utf-8"
    )

    monkeypatch.setattr(evaluator, "DATASET_PATH", dataset_path)

    with pytest.raises(ValueError, match="缺少必要字段"):
        evaluator.run_evaluation()


def test_run_evaluation_unknown_expected_label(tmp_path, monkeypatch):
    """数据集中的标准标签不合法时应该报错。"""

    dataset = [
        {
            "id": "AI001",
            "text": "测试内容",
            "expected": "unknown"
        }
    ]

    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(
        json.dumps(dataset, ensure_ascii=False),
        encoding="utf-8"
    )

    monkeypatch.setattr(evaluator, "DATASET_PATH", dataset_path)

    with pytest.raises(ValueError, match="未知标准标签"):
        evaluator.run_evaluation()


def test_run_evaluation_unknown_predicted_label(tmp_path, monkeypatch):
    """模拟模型返回不支持的预测标签。"""

    dataset = [
        {
            "id": "AI001",
            "text": "测试内容",
            "expected": "pass"
        }
    ]

    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(
        json.dumps(dataset, ensure_ascii=False),
        encoding="utf-8"
    )

    monkeypatch.setattr(evaluator, "DATASET_PATH", dataset_path)

    monkeypatch.setattr(
        evaluator,
        "mock_predict",
        lambda case, index: {
            "label": "unknown",
            "reason": "模拟非法预测结果"
        }
    )

    with pytest.raises(ValueError, match="未知预测标签"):
        evaluator.run_evaluation()


def test_run_evaluation_no_valid_cases(tmp_path, monkeypatch):
    """全部样本都是 invalid 时，不能执行三分类评估。"""

    dataset = [
        {
            "id": "AI001",
            "text": "",
            "expected": "invalid"
        },
        {
            "id": "AI002",
            "text": "",
            "expected": "invalid"
        }
    ]

    dataset_path = tmp_path / "dataset.json"
    dataset_path.write_text(
        json.dumps(dataset, ensure_ascii=False),
        encoding="utf-8"
    )

    monkeypatch.setattr(evaluator, "DATASET_PATH", dataset_path)

    with pytest.raises(ValueError, match="没有可用于三分类评估的有效样本"):
        evaluator.run_evaluation()


def test_run_evaluation_ollama_mode(tmp_path, monkeypatch):
    """验证 Ollama 模式能够加载 Prompt、调用模型并生成报告。"""

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
        }
    ]

    dataset_path = tmp_path / "dataset.json"
    report_path = tmp_path / "ollama_report.json"

    dataset_path.write_text(
        json.dumps(dataset, ensure_ascii=False),
        encoding="utf-8"
    )

    monkeypatch.setattr(evaluator, "DATASET_PATH", dataset_path)
    monkeypatch.setattr(
        evaluator,
        "load_prompt",
        lambda version: "测试用 Prompt"
    )

    class FakeOllamaClient:
        model = "fake-model"

        def __init__(self, system_prompt):
            self.system_prompt = system_prompt

        def classify(self, text):
            if text == "正常内容":
                return {
                    "label": "pass",
                    "reason": "内容正常"
                }

            return {
                "label": "block",
                "reason": "内容违规"
            }

    monkeypatch.setattr(
        ollama_client,
        "OllamaClient",
        FakeOllamaClient
    )

    report = evaluator.run_evaluation(
        mode="ollama",
        prompt_version="v2",
        output_path=report_path
    )

    assert report["evaluation_type"] == "ollama"
    assert report["prompt_version"] == "v2"
    assert report["model"] == "fake-model"
    assert report["temperature"] == 0
    assert report["evaluated_cases"] == 2
    assert report_path.exists()


def test_run_evaluation_default_output_path(tmp_path, monkeypatch):
    """未指定输出路径时，应该保存到默认报告目录。"""

    dataset = [
        {
            "id": "AI001",
            "text": "正常内容",
            "expected": "pass"
        }
    ]

    dataset_path = tmp_path / "dataset.json"
    report_dir = tmp_path / "reports"

    dataset_path.write_text(
        json.dumps(dataset, ensure_ascii=False),
        encoding="utf-8"
    )

    monkeypatch.setattr(evaluator, "DATASET_PATH", dataset_path)
    monkeypatch.setattr(evaluator, "REPORT_DIR", report_dir)

    evaluator.run_evaluation(
        mode="mock",
        prompt_version="v1"
    )

    expected_path = report_dir / "evaluation_mock_v1.json"

    assert expected_path.exists()


def test_evaluator_command_line(tmp_path, monkeypatch):
    """验证命令行参数能够被解析并执行评估。"""

    dataset = [
        {
            "id": "AI001",
            "text": "正常内容",
            "expected": "pass"
        }
    ]

    dataset_path = tmp_path / "dataset.json"
    output_path = tmp_path / "cli_report.json"

    dataset_path.write_text(
        json.dumps(dataset, ensure_ascii=False),
        encoding="utf-8"
    )

    monkeypatch.setattr(evaluator, "DATASET_PATH", dataset_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "evaluator.py",
            "--mode", "mock",
            "--prompt-version", "v1",
            "--output", str(output_path)
        ]
    )

    report = evaluator.main()

    assert output_path.exists()
    assert report["evaluation_type"] == "mock"
    assert report["evaluated_cases"] == 1