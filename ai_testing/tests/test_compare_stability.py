import json
import pytest

from ai_testing.stability import compare_stability as compare_module

from ai_testing.stability.compare_stability import (
    load_report,
    get_case_counts,
    analyze_report,
    validate_reports,
    compare_stability,
)


def create_report(
    temperature=0,
    model="qwen3",
    prompt_version="v2",
    case_ids=None,
):
    """构造一份模拟稳定性报告。"""
    if case_ids is None:
        case_ids = ["AI001", "AI002"]

    return {
        "model": model,
        "prompt_version": prompt_version,
        "temperature": temperature,
        "repeats": 5,
        "prediction_details": [
            {
                "id": case_id,
                "counts": {
                    "pass": 5
                },
            }
            for case_id in case_ids
        ],
    }


def save_report(tmp_path, filename, report):
    """把模拟报告保存为临时 JSON 文件。"""
    path = tmp_path / filename

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    return path


def test_load_report_success(tmp_path):
    report_data = create_report()
    path = save_report(tmp_path, "report.json", report_data)

    result = load_report(path)

    assert result["model"] == "qwen3"
    assert result["temperature"] == 0


def test_load_report_file_not_found(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_report(path)


def test_analyze_report_calculates_stability(tmp_path):
    report = create_report()

    report["prediction_details"] = [
        {
            "id": "AI001",
            "counts": {"pass": 5},
        },
        {
            "id": "AI002",
            "counts": {"pass": 4, "review": 1},
        },
    ]

    result = analyze_report(report, tmp_path / "report.json")

    assert result["total_cases"] == 2
    assert result["stable_cases"] == 1
    assert result["unstable_cases"] == 1
    assert result["case_stability_rate"] == 0.5
    assert result["average_agreement_rate"] == 0.9


def test_validate_reports_model_mismatch():
    report1 = analyze_report(
        create_report(model="qwen3"),
        "report1.json",
    )
    report2 = analyze_report(
        create_report(model="other-model", temperature=0.3),
        "report2.json",
    )

    with pytest.raises(ValueError, match="模型不一致"):
        validate_reports([report1, report2])


def test_validate_reports_prompt_mismatch():
    report1 = analyze_report(
        create_report(prompt_version="v1"),
        "report1.json",
    )
    report2 = analyze_report(
        create_report(prompt_version="v2", temperature=0.3),
        "report2.json",
    )

    with pytest.raises(ValueError, match="Prompt 版本不一致"):
        validate_reports([report1, report2])


def test_validate_reports_case_mismatch():
    report1 = analyze_report(
        create_report(case_ids=["AI001", "AI002"]),
        "report1.json",
    )
    report2 = analyze_report(
        create_report(
            temperature=0.3,
            case_ids=["AI001", "AI003"],
        ),
        "report2.json",
    )

    with pytest.raises(ValueError, match="测试样本不一致"):
        validate_reports([report1, report2])


def test_compare_stability_generates_report(tmp_path):
    report1 = create_report(temperature=0)
    report2 = create_report(temperature=0.3)

    path1 = save_report(tmp_path, "report1.json", report1)
    path2 = save_report(tmp_path, "report2.json", report2)

    output_path = tmp_path / "comparison.json"

    result = compare_stability(
        report_paths=[path1, path2],
        output_path=output_path,
    )

    assert output_path.exists()
    assert result["comparison_type"] == "stability"
    assert len(result["summary"]) == 2
    assert "AI001" in result["case_comparison"]

    with output_path.open("r", encoding="utf-8") as file:
        saved_result = json.load(file)

    assert saved_result["model"] == "qwen3"
    assert saved_result["prompt_version"] == "v2"


def test_compare_stability_requires_two_reports(tmp_path):
    path = save_report(
        tmp_path,
        "report.json",
        create_report(),
    )

    with pytest.raises(ValueError, match="至少需要两份报告"):
        compare_stability([path])




# =========================
# get_case_counts 测试
# =========================

def test_get_case_counts_from_predictions():
    case = {
        "id": "AI001",
        "predictions": [
            "pass",
            "pass",
            "review",
            "pass",
            "block",
        ],
    }

    result = get_case_counts(case)

    assert result == {
        "pass": 3,
        "review": 1,
        "block": 1,
    }


def test_get_case_counts_invalid_data():
    case = {"id": "AI001"}

    with pytest.raises(ValueError, match="缺少有效的 counts 或 predictions"):
        get_case_counts(case)


# =========================
# analyze_report 异常分支测试
# =========================

@pytest.mark.parametrize(
    "details",
    [
        None,
        [],
        {},
    ],
)
def test_analyze_report_invalid_prediction_details(
    tmp_path, details
):
    report = {
        "prediction_details": details,
    }

    with pytest.raises(ValueError, match="缺少有效的 prediction_details"):
        analyze_report(report, tmp_path / "report.json")


def test_analyze_report_missing_case_id(tmp_path):
    report = {
        "prediction_details": [
            {
                "counts": {"pass": 5},
            }
        ]
    }

    with pytest.raises(ValueError, match="缺少 id"):
        analyze_report(report, tmp_path / "report.json")


def test_analyze_report_zero_predictions(tmp_path):
    report = {
        "prediction_details": [
            {
                "id": "AI001",
                "counts": {},
            }
        ]
    }

    with pytest.raises(ValueError, match="没有预测记录"):
        analyze_report(report, tmp_path / "report.json")


def test_analyze_report_uses_predictions(tmp_path):
    report = {
        "model": "qwen3",
        "prompt_version": "v2",
        "temperature": 0,
        "repeats": 5,
        "prediction_details": [
            {
                "id": "AI001",
                "predictions": [
                    "pass", "pass", "pass", "review", "pass"
                ],
            },
            {
                "id": "AI002",
                "predictions": [
                    "block", "block", "block", "block", "block"
                ],
            },
        ],
    }

    result = analyze_report(report, tmp_path / "report.json")

    assert result["cases"]["AI001"]["counts"]["pass"] == 4
    assert result["cases"]["AI001"]["agreement_rate"] == 0.8
    assert result["cases"]["AI001"]["stable"] is False
    assert result["cases"]["AI002"]["stable"] is True


# =========================
# validate_reports 测试
# =========================

def test_validate_reports_repeats_mismatch():
    report1 = analyze_report(
        create_report(temperature=0),
        "report1.json",
    )

    report_data = create_report(temperature=0.3)
    report_data["repeats"] = 3

    report2 = analyze_report(
        report_data,
        "report2.json",
    )

    with pytest.raises(ValueError, match="重复次数不一致"):
        validate_reports([report1, report2])


def test_validate_reports_duplicate_temperature():
    report1 = analyze_report(
        create_report(temperature=0),
        "report1.json",
    )

    report2 = analyze_report(
        create_report(temperature=0),
        "report2.json",
    )

    with pytest.raises(ValueError, match="重复的 Temperature"):
        validate_reports([report1, report2])


# =========================
# load_report JSON 异常测试
# =========================

def test_load_report_invalid_json(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("{invalid json}", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_report(path)


# =========================
# compare_stability 默认输出路径
# =========================

def test_compare_stability_default_output_path(
    tmp_path, monkeypatch
):
    report1 = create_report(temperature=0)
    report2 = create_report(temperature=0.3)

    path1 = save_report(tmp_path, "report1.json", report1)
    path2 = save_report(tmp_path, "report2.json", report2)

    report_dir = tmp_path / "reports"

    monkeypatch.setattr(
        compare_module,
        "REPORT_DIR",
        report_dir,
    )

    result = compare_stability(
        report_paths=[path1, path2],
    )

    expected_path = report_dir / "stability_comparison_v2.json"

    assert expected_path.exists()
    assert result["comparison_type"] == "stability"