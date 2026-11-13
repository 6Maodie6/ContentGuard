
import json
import pytest

from ai_testing.security.compare_security import (
    load_report,
    validate_reports,
    compare_reports,
    save_comparison,
)

import sys

from ai_testing.security import compare_security as security_module


def make_report(version, predictions=None):
    """构造模拟安全测试报告。"""

    if predictions is None:
        predictions = {
            "SEC001": ("block", "block"),
            "SEC002": ("block", "block"),
            "SEC003": ("pass", "pass"),
            "SEC004": ("pass", "pass"),
        }

    details = []

    for case_id, (expected, predicted) in predictions.items():
        is_attack = case_id in {"SEC002", "SEC004"}

        details.append({
            "id": case_id,
            "pair_id": "PAIR001" if case_id in {"SEC001", "SEC002"} else "PAIR002",
            "case_type": "attack" if is_attack else "baseline",
            "attack_type": "label_override" if is_attack else "none",
            "text": f"测试文本 {case_id}",
            "expected": expected,
            "predicted": predicted,
            "correct": expected == predicted,
            "reason": "模拟判断理由",
        })

    attack_cases = [
        item for item in details
        if item["case_type"] == "attack"
    ]

    attack_correct = sum(item["correct"] for item in attack_cases)

    pair_total = 2
    consistent_pairs = 0

    for pair_id in {"PAIR001", "PAIR002"}:
        pair_cases = [
            item for item in details
            if item["pair_id"] == pair_id
        ]

        if all(item["correct"] for item in pair_cases):
            consistent_pairs += 1

    metrics = {
        "attack_total": len(attack_cases),
        "attack_correct_count": attack_correct,
        "attack_failure_count": len(attack_cases) - attack_correct,
        "attack_accuracy": attack_correct / len(attack_cases),
        "resistant_count": attack_correct,
        "attack_resistance_rate": attack_correct / len(attack_cases),
        "pair_total": pair_total,
        "consistent_pair_count": consistent_pairs,
        "pair_consistency": consistent_pairs / pair_total,
    }

    return {
        "evaluation_type": "security",
        "model": "test-model",
        "prompt_version": version,
        "temperature": 0.0,
        "total_cases": len(details),
        "metrics": metrics,
        "prediction_details": details,
    }


def test_validate_reports_success():
    reports = [
        make_report("v2"),
        make_report("v3"),
    ]

    validate_reports(reports)


def test_validate_reports_requires_two_reports():
    with pytest.raises(ValueError, match="至少需要两份"):
        validate_reports([make_report("v2")])


def test_validate_reports_model_mismatch():
    first = make_report("v2")
    second = make_report("v3")
    second["model"] = "another-model"

    with pytest.raises(ValueError, match="模型不一致"):
        validate_reports([first, second])


def test_validate_reports_temperature_mismatch():
    first = make_report("v2")
    second = make_report("v3")
    second["temperature"] = 0.7

    with pytest.raises(ValueError, match="Temperature"):
        validate_reports([first, second])


def test_validate_reports_case_mismatch():
    first = make_report("v2")
    second = make_report("v3")
    second["prediction_details"].pop()

    with pytest.raises(ValueError, match="测试用例 ID 不一致"):
        validate_reports([first, second])


def test_validate_reports_expected_mismatch():
    first = make_report("v2")
    second = make_report("v3")
    second["prediction_details"][0]["expected"] = "pass"

    with pytest.raises(ValueError, match="expected"):
        validate_reports([first, second])


def test_compare_reports_detects_fixed_and_regressed_cases():
    v2 = make_report("v2", {
        "SEC001": ("block", "block"),
        "SEC002": ("block", "block"),
        "SEC003": ("pass", "block"),
        "SEC004": ("pass", "pass"),
    })

    v3 = make_report("v3", {
        "SEC001": ("block", "block"),
        "SEC002": ("block", "block"),
        "SEC003": ("pass", "pass"),
        "SEC004": ("pass", "block"),
    })

    result = compare_reports([v2, v3])
    transition = result["transitions"][0]

    assert transition["fixed_cases"] == ["SEC003"]
    assert transition["regressed_cases"] == ["SEC004"]
    assert transition["fixed_count"] == 1
    assert transition["regressed_count"] == 1
    assert transition["prediction_changed_cases"] == ["SEC003", "SEC004"]


def test_load_report_and_save_comparison(tmp_path):
    report_path = tmp_path / "report.json"
    output_path = tmp_path / "result" / "comparison.json"

    report = make_report("v2")

    report_path.write_text(
        json.dumps(report, ensure_ascii=False),
        encoding="utf-8"
    )

    loaded = load_report(report_path)

    assert loaded["prompt_version"] == "v2"

    save_comparison({"result": "success"}, output_path)

    assert output_path.exists()

    saved = json.loads(output_path.read_text(encoding="utf-8"))

    assert saved["result"] == "success"



@pytest.mark.parametrize(
    "field, value",
    [
        ("evaluation_type", "normal"),
        ("prediction_details", None),
        ("metrics", None),
    ]
)
def test_validate_reports_invalid_first_report(field, value):
    """第一份报告的类型或必要字段不合法。"""

    first = make_report("v2")
    second = make_report("v3")

    first[field] = value

    with pytest.raises(ValueError):
        validate_reports([first, second])


def test_validate_reports_duplicate_ids_in_first_report():
    """第一份报告存在重复测试用例 ID。"""

    first = make_report("v2")
    second = make_report("v3")

    first["prediction_details"].append(
        first["prediction_details"][0].copy()
    )

    with pytest.raises(ValueError):
        validate_reports([first, second])


@pytest.mark.parametrize(
    "field, value",
    [
        ("evaluation_type", "normal"),
        ("prediction_details", None),
        ("metrics", None),
    ]
)
def test_validate_reports_invalid_current_report(field, value):
    """后续报告的类型或必要字段不合法。"""

    first = make_report("v2")
    second = make_report("v3")

    second[field] = value

    with pytest.raises(ValueError):
        validate_reports([first, second])


def test_validate_reports_duplicate_ids_in_current_report():
    """后续报告存在重复测试用例 ID。"""

    first = make_report("v2")
    second = make_report("v3")

    second["prediction_details"].append(
        second["prediction_details"][0].copy()
    )

    with pytest.raises(ValueError):
        validate_reports([first, second])


@pytest.mark.parametrize(
    "field, value",
    [
        ("text", "修改后的测试文本"),
        ("expected", "review"),
        ("pair_id", "PAIR999"),
        ("case_type", "attack"),
        ("attack_type", "instruction_override"),
    ]
)
def test_validate_reports_case_field_mismatch(field, value):
    """同一个测试用例在不同报告中的基础信息必须一致。"""

    first = make_report("v2")
    second = make_report("v3")

    second["prediction_details"][0][field] = value

    with pytest.raises(ValueError):
        validate_reports([first, second])


def test_validate_reports_invalid_current_evaluation_type():
    """后续报告的 evaluation_type 必须是 security。"""

    first = make_report("v2")
    second = make_report("v3")
    second["evaluation_type"] = "normal"

    with pytest.raises(ValueError):
        validate_reports([first, second])


def test_compare_reports_unchanged_cases_and_metric_changes():
    """验证未变化案例和指标变化量。"""

    v2 = make_report("v2", {
        "SEC001": ("block", "block"),
        "SEC002": ("block", "block"),
        "SEC003": ("pass", "block"),
        "SEC004": ("pass", "block"),
    })

    v3 = make_report("v3", {
        "SEC001": ("block", "block"),
        "SEC002": ("block", "block"),
        "SEC003": ("pass", "block"),
        "SEC004": ("pass", "pass"),
    })

    v2["metrics"]["attack_accuracy"] = 0.5
    v2["metrics"]["attack_resistance_rate"] = 0.5
    v2["metrics"]["pair_consistency"] = 0.5

    v3["metrics"]["attack_accuracy"] = 1.0
    v3["metrics"]["attack_resistance_rate"] = 1.0
    v3["metrics"]["pair_consistency"] = 1.0

    result = compare_reports([v2, v3])

    transition = result["transitions"][0]

    assert transition["fixed_cases"] == ["SEC004"]
    assert transition["regressed_cases"] == []

    assert transition["unchanged_correct_cases"] == [
        "SEC001",
        "SEC002",
    ]

    assert transition["unchanged_incorrect_cases"] == [
        "SEC003",
    ]

    assert transition["prediction_changed_cases"] == ["SEC004"]

    assert transition["metric_changes"] == {
        "attack_accuracy": 0.5,
        "attack_resistance_rate": 0.5,
        "pair_consistency": 0.5,
    }

    assert result["comparison_type"] == "security_prompt_comparison"
    assert result["model"] == "test-model"
    assert len(result["version_results"]) == 2


def test_compare_reports_multiple_transitions():
    """验证三个 Prompt 版本能生成两段版本变化记录。"""

    reports = [
        make_report("v2"),
        make_report("v3"),
        make_report("v4"),
    ]

    result = compare_reports(reports)

    assert len(result["version_results"]) == 3
    assert len(result["transitions"]) == 2

    assert result["transitions"][0]["from_version"] == "v2"
    assert result["transitions"][0]["to_version"] == "v3"

    assert result["transitions"][1]["from_version"] == "v3"
    assert result["transitions"][1]["to_version"] == "v4"


def test_print_comparison(capsys):
    """验证版本比较结果能够正常输出到终端。"""

    result = compare_reports([
        make_report("v2"),
        make_report("v3"),
    ])

    security_module.print_comparison(result)

    output = capsys.readouterr().out

    assert "AI" in output
    assert "v2" in output
    assert "v3" in output
    assert "attack_accuracy" in output


def test_main_with_custom_output(tmp_path, monkeypatch):
    """验证 CLI 能读取报告并保存到用户指定的位置。"""

    report1 = make_report("v2")
    report2 = make_report("v3")

    report1_path = tmp_path / "v2.json"
    report2_path = tmp_path / "v3.json"
    output_path = tmp_path / "custom" / "comparison.json"

    report1_path.write_text(
        json.dumps(report1, ensure_ascii=False),
        encoding="utf-8"
    )

    report2_path.write_text(
        json.dumps(report2, ensure_ascii=False),
        encoding="utf-8"
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compare_security.py",
            "--reports",
            str(report1_path),
            str(report2_path),
            "--output",
            str(output_path),
        ]
    )

    security_module.main()

    assert output_path.exists()

    saved = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert saved["comparison_type"] == "security_prompt_comparison"


def test_main_with_default_output(tmp_path, monkeypatch):
    """没有指定 --output 时，使用默认报告目录。"""

    report1 = make_report("v2")
    report2 = make_report("v3")

    report1_path = tmp_path / "v2.json"
    report2_path = tmp_path / "v3.json"

    report1_path.write_text(
        json.dumps(report1, ensure_ascii=False),
        encoding="utf-8"
    )

    report2_path.write_text(
        json.dumps(report2, ensure_ascii=False),
        encoding="utf-8"
    )

    default_report_dir = tmp_path / "default_reports"

    monkeypatch.setattr(
        security_module,
        "REPORT_DIR",
        default_report_dir
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compare_security.py",
            "--reports",
            str(report1_path),
            str(report2_path),
        ]
    )

    security_module.main()

    output_path = default_report_dir / "security_comparison.json"

    assert output_path.exists()

    saved = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert saved["comparison_type"] == "security_prompt_comparison"
