
import json

import pytest

from ai_testing.evaluation.compare_reports import (
    load_report,
    validate_reports,
    compare_reports
)


def make_report(predictions, accuracy=0.8):
    """构造用于测试的模拟评估报告。"""

    return {
        "evaluation_type": "ollama",
        "model": "Qwen3-8B",
        "temperature": 0,
        "prompt_version": "v1",
        "prediction_details": predictions,
        "metrics": {
            "accuracy": accuracy,
            "macro_f1": 0.75,
            "weighted_f1": 0.8
        }
    }


def make_case(case_id, expected, predicted):
    """构造一条预测记录。"""

    return {
        "id": case_id,
        "text": f"测试文本 {case_id}",
        "expected": expected,
        "predicted": predicted,
        "correct": expected == predicted,
        "reason": "测试原因"
    }


def test_load_report_missing_file():
    """测试读取不存在的报告。"""

    with pytest.raises(FileNotFoundError):
        load_report("not_exists.json")


def test_validate_reports_model_mismatch():
    """测试模型不一致时拒绝比较。"""

    v1 = make_report([
        make_case("AI001", "pass", "pass")
    ])

    v2 = make_report([
        make_case("AI001", "pass", "pass")
    ])

    v2["model"] = "OtherModel"

    with pytest.raises(ValueError, match="模型不同"):
        validate_reports(v1, v2)


def test_validate_reports_dataset_mismatch():
    """测试测试文本不一致时拒绝比较。"""

    v1 = make_report([
        make_case("AI001", "pass", "pass")
    ])

    v2 = make_report([
        make_case("AI001", "pass", "pass")
    ])

    v2["prediction_details"][0]["text"] = "不同的测试文本"

    with pytest.raises(ValueError, match="测试文本不一致"):
        validate_reports(v1, v2)


def test_validate_reports_temperature_mismatch():
    """测试 Temperature 不一致时拒绝比较。"""

    v1 = make_report([
        make_case("AI001", "pass", "pass")
    ])

    v2 = make_report([
        make_case("AI001", "pass", "pass")
    ])

    v2["temperature"] = 0.7

    with pytest.raises(ValueError, match="Temperature 不同"):
        validate_reports(v1, v2)


def test_compare_reports_counts_and_metrics(tmp_path, monkeypatch):
    """测试修复、回归、持平数量和指标变化。"""

    v1_predictions = [
        make_case("AI001", "block", "review"),  # V1 错，V2 对
        make_case("AI002", "pass", "pass"),     # V1 对，V2 错
        make_case("AI003", "review", "pass"),   # 两版都错
        make_case("AI004", "pass", "pass")      # 两版都对
    ]

    v2_predictions = [
        make_case("AI001", "block", "block"),
        make_case("AI002", "pass", "block"),
        make_case("AI003", "review", "block"),
        make_case("AI004", "pass", "pass")
    ]

    v1 = make_report(v1_predictions, accuracy=0.5)
    v2 = make_report(v2_predictions, accuracy=0.5)

    v1_path = tmp_path / "v1.json"
    v2_path = tmp_path / "v2.json"
    output_path = tmp_path / "comparison.json"

    v1_path.write_text(
        json.dumps(v1),
        encoding="utf-8"
    )

    v2_path.write_text(
        json.dumps(v2),
        encoding="utf-8"
    )

    monkeypatch.setattr(
        "ai_testing.evaluation.compare_reports.COMPARISON_REPORT",
        output_path
    )

    result = compare_reports(v1_path, v2_path)

    assert result["total_cases"] == 4
    assert result["fixed_count"] == 1
    assert result["regressed_count"] == 1
    assert result["unchanged_count"] == 2

    assert result["fixed_cases"][0]["id"] == "AI001"
    assert result["regressed_cases"][0]["id"] == "AI002"

    assert result["metric_comparison"]["accuracy"]["change"] == 0

    assert output_path.exists()

    saved_result = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert saved_result["fixed_count"] == 1
    assert saved_result["regressed_count"] == 1
