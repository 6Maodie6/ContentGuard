
import argparse
import json
from pathlib import Path

AI_TESTING_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = AI_TESTING_DIR / "reports"

EVALUATION_DIR = REPORT_DIR / "evaluation_reports"
COMPARISON_DIR = REPORT_DIR / "prompt_comparison_reports"

V1_REPORT = EVALUATION_DIR / "evaluation_ollama_v1.json"
V2_REPORT = EVALUATION_DIR / "evaluation_ollama_v2.json"

COMPARISON_REPORT = COMPARISON_DIR / "prompt_comparison_v1_vs_v2.json"
def load_report(path):
    """读取评估报告，支持 str 和 Path 类型。"""

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"找不到评估报告：{path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)



def validate_reports(v1, v2):
    """检查两份报告是否具备可比性。"""

    if v1.get("evaluation_type") != "ollama":
        raise ValueError("V1 报告不是 Ollama 真实模型评估报告")

    if v2.get("evaluation_type") != "ollama":
        raise ValueError("V2 报告不是 Ollama 真实模型评估报告")

    if v1.get("model") != v2.get("model"):
        raise ValueError("两份报告使用的模型不同，不能直接进行 Prompt 对比")

    if v1.get("temperature") != v2.get("temperature"):
        raise ValueError("两份报告的 Temperature 不同，不能直接进行 Prompt 对比")

    details_v1 = v1.get("prediction_details", [])
    details_v2 = v2.get("prediction_details", [])

    cases_v1 = {case["id"]: case for case in details_v1}
    cases_v2 = {case["id"]: case for case in details_v2}

    if cases_v1.keys() != cases_v2.keys():
        raise ValueError("两份报告的有效测试用例不一致")

    for case_id in cases_v1:
        old = cases_v1[case_id]
        new = cases_v2[case_id]

        if old["expected"] != new["expected"]:
            raise ValueError(f"测试用例 {case_id} 的标准答案不一致")

        if old["text"] != new["text"]:
            raise ValueError(f"测试用例 {case_id} 的测试文本不一致")

    return cases_v1, cases_v2



def compare_reports(v1_path=V1_REPORT, v2_path=V2_REPORT):
    """对比两个 Prompt 版本的评估结果。"""

    v1 = load_report(Path(v1_path))
    v2 = load_report(Path(v2_path))

    cases_v1, cases_v2 = validate_reports(v1, v2)

    fixed_cases = []
    regressed_cases = []
    unchanged_cases = []

    for case_id in cases_v1:
        old = cases_v1[case_id]
        new = cases_v2[case_id]

        if not old["correct"] and new["correct"]:
            fixed_cases.append({
                "id": case_id,
                "expected": old["expected"],
                "v1_predicted": old["predicted"],
                "v2_predicted": new["predicted"],
                "v1_reason": old.get("reason"),
                "v2_reason": new.get("reason")
            })

        elif old["correct"] and not new["correct"]:
            regressed_cases.append({
                "id": case_id,
                "expected": old["expected"],
                "v1_predicted": old["predicted"],
                "v2_predicted": new["predicted"],
                "v1_reason": old.get("reason"),
                "v2_reason": new.get("reason")
            })

        else:
            unchanged_cases.append(case_id)

    metrics_v1 = v1["metrics"]
    metrics_v2 = v2["metrics"]

    metric_names = [
        "accuracy",
        "macro_f1",
        "weighted_f1"
    ]

    metric_comparison = {}

    for name in metric_names:
        old_value = metrics_v1[name]
        new_value = metrics_v2[name]

        metric_comparison[name] = {
            "v1": old_value,
            "v2": new_value,
            "change": new_value - old_value
        }

    comparison = {
        "v1_model": v1["model"],
        "v2_model": v2["model"],
        "v1_prompt_version": v1.get("prompt_version"),
        "v2_prompt_version": v2.get("prompt_version"),
        "v1_evaluated_at": v1.get("evaluated_at"),
        "v2_evaluated_at": v2.get("evaluated_at"),
        "total_cases": len(cases_v1),
        "fixed_count": len(fixed_cases),
        "regressed_count": len(regressed_cases),
        "unchanged_count": len(unchanged_cases),
        "fixed_cases": fixed_cases,
        "regressed_cases": regressed_cases,
        "unchanged_case_ids": unchanged_cases,
        "metric_comparison": metric_comparison
    }

    COMPARISON_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(COMPARISON_REPORT, "w", encoding="utf-8") as file:
        json.dump(
            comparison,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n========== Prompt 版本对比结果 ==========")
    print(f"测试用例总数：{len(cases_v1)}")
    print(f"修复用例数：{len(fixed_cases)}")
    print(f"回归用例数：{len(regressed_cases)}")
    print(f"正确性持平用例数：{len(unchanged_cases)}")

    print("\n========== 指标变化 ==========")

    for name, values in metric_comparison.items():
        print(
            f"{name}: "
            f"V1={values['v1']:.2%}, "
            f"V2={values['v2']:.2%}, "
            f"变化={values['change']:+.2%}"
        )

    print("\n========== 修复的用例 ==========")

    for case in fixed_cases:
        print(
            f"{case['id']}: "
            f"{case['v1_predicted']} -> {case['v2_predicted']}"
        )

    print("\n========== 出现回归的用例 ==========")

    for case in regressed_cases:
        print(
            f"{case['id']}: "
            f"{case['v1_predicted']} -> {case['v2_predicted']}"
        )

    print(f"\n对比报告已保存：{COMPARISON_REPORT}")

    return comparison


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ContentGuard Prompt 版本对比工具"
    )

    parser.add_argument(
        "--v1",
        default=str(V1_REPORT),
        help="V1 评估报告路径"
    )

    parser.add_argument(
        "--v2",
        default=str(V2_REPORT),
        help="V2 评估报告路径"
    )

    args = parser.parse_args()

    compare_reports(args.v1, args.v2)
