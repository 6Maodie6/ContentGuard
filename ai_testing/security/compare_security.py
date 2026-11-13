
import argparse
import json
from pathlib import Path
from datetime import datetime


REPORT_DIR = Path(__file__).resolve().parent.parent / "reports" / "security_reports"

METRIC_KEYS = [
    "attack_accuracy",
    "attack_resistance_rate",
    "pair_consistency",
]


def load_report(path):
    """读取单份安全测试报告。"""
    path = Path(path)

    with open(path, "r", encoding="utf-8") as file:
        report = json.load(file)

    return report


def validate_reports(reports):
    """检查多份报告是否具备可比性。"""

    if len(reports) < 2:
        raise ValueError("至少需要两份报告才能进行版本比较")

    first = reports[0]

    if first.get("evaluation_type") != "security":
        raise ValueError("报告类型必须是 security")

    if not isinstance(first.get("prediction_details"), list):
        raise ValueError("报告缺少有效的 prediction_details")

    if not isinstance(first.get("metrics"), dict):
        raise ValueError("报告缺少有效的 metrics")

    first_cases = {
        item["id"]: item
        for item in first["prediction_details"]
    }

    if len(first_cases) != len(first["prediction_details"]):
        raise ValueError("报告中存在重复的测试用例 ID")

    for report in reports[1:]:

        if report.get("evaluation_type") != "security":
            raise ValueError("报告类型必须是 security")

        if report.get("model") != first.get("model"):
            raise ValueError("不同报告的模型不一致")

        if report.get("temperature") != first.get("temperature"):
            raise ValueError("不同报告的 Temperature 不一致")

        if not isinstance(report.get("prediction_details"), list):
            raise ValueError("报告缺少有效的 prediction_details")

        if not isinstance(report.get("metrics"), dict):
            raise ValueError("报告缺少有效的 metrics")

        current_cases = {
            item["id"]: item
            for item in report["prediction_details"]
        }

        if len(current_cases) != len(report["prediction_details"]):
            raise ValueError("报告中存在重复的测试用例 ID")

        if set(current_cases) != set(first_cases):
            raise ValueError("不同版本的测试用例 ID 不一致")

        for case_id, first_case in first_cases.items():
            current_case = current_cases[case_id]

            for field in [
                "text",
                "expected",
                "pair_id",
                "case_type",
                "attack_type",
            ]:
                if current_case.get(field) != first_case.get(field):
                    raise ValueError(
                        f"测试用例 {case_id} 的 {field} 不一致"
                    )


def compare_reports(reports):
    """比较多个 Prompt 版本的安全测试结果。"""

    validate_reports(reports)

    version_results = []

    for report in reports:
        metrics = report["metrics"]

        version_results.append({
            "prompt_version": report["prompt_version"],
            "total_cases": report["total_cases"],
            "attack_total": metrics["attack_total"],
            "attack_accuracy": metrics["attack_accuracy"],
            "attack_resistance_rate": metrics["attack_resistance_rate"],
            "pair_consistency": metrics["pair_consistency"],
            "attack_failure_count": metrics["attack_failure_count"],
        })

    transitions = []

    for index in range(1, len(reports)):
        previous = reports[index - 1]
        current = reports[index]

        previous_cases = {
            item["id"]: item
            for item in previous["prediction_details"]
        }

        current_cases = {
            item["id"]: item
            for item in current["prediction_details"]
        }

        fixed_cases = []
        regressed_cases = []
        unchanged_correct_cases = []
        unchanged_incorrect_cases = []
        prediction_changed_cases = []

        for case_id, previous_case in previous_cases.items():
            current_case = current_cases[case_id]

            if (
                previous_case["predicted"]
                != current_case["predicted"]
            ):
                prediction_changed_cases.append(case_id)

            if not previous_case["correct"] and current_case["correct"]:
                fixed_cases.append(case_id)

            elif previous_case["correct"] and not current_case["correct"]:
                regressed_cases.append(case_id)

            elif previous_case["correct"] and current_case["correct"]:
                unchanged_correct_cases.append(case_id)

            else:
                unchanged_incorrect_cases.append(case_id)

        previous_metrics = previous["metrics"]
        current_metrics = current["metrics"]

        metric_changes = {}

        for key in METRIC_KEYS:
            metric_changes[key] = round(
                current_metrics[key] - previous_metrics[key],
                6
            )

        transitions.append({
            "from_version": previous["prompt_version"],
            "to_version": current["prompt_version"],
            "fixed_count": len(fixed_cases),
            "fixed_cases": fixed_cases,
            "regressed_count": len(regressed_cases),
            "regressed_cases": regressed_cases,
            "unchanged_correct_cases": unchanged_correct_cases,
            "unchanged_incorrect_cases": unchanged_incorrect_cases,
            "prediction_changed_cases": prediction_changed_cases,
            "metric_changes": metric_changes,
        })

    return {
        "comparison_type": "security_prompt_comparison",
        "model": reports[0]["model"],
        "temperature": reports[0]["temperature"],
        "total_cases": reports[0]["total_cases"],
        "compared_at": datetime.now().isoformat(timespec="seconds"),
        "version_results": version_results,
        "transitions": transitions,
    }


def save_comparison(result, output_path):
    """保存版本比较报告。"""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

    return output_path


def print_comparison(result):
    """在终端展示版本比较结果。"""

    print("\n========== AI 安全测试版本对比 ==========")

    print(f"模型：{result['model']}")
    print(f"Temperature：{result['temperature']}")
    print(f"测试样本数：{result['total_cases']}")

    print("\n---------- 各版本指标 ----------")

    for item in result["version_results"]:
        print(f"\nPrompt {item['prompt_version']}")
        print(f"攻击样本准确率：{item['attack_accuracy']:.2%}")
        print(f"攻击抵抗率：{item['attack_resistance_rate']:.2%}")
        print(f"成对一致率：{item['pair_consistency']:.2%}")
        print(f"攻击失败数：{item['attack_failure_count']}")

    print("\n---------- 版本变化 ----------")

    for item in result["transitions"]:
        print(
            f"\n{item['from_version']} -> {item['to_version']}"
        )
        print(f"修复用例：{item['fixed_count']}")
        print(f"回归用例：{item['regressed_count']}")
        print(f"预测标签发生变化：{item['prediction_changed_cases']}")

        print("指标变化：")

        for key, value in item["metric_changes"].items():
            print(f"  {key}: {value:+.2%}")


def main():
    parser = argparse.ArgumentParser(
        description="ContentGuard Prompt 安全测试版本对比"
    )

    parser.add_argument(
        "--reports",
        nargs="+",
        required=True,
        help="按比较顺序传入安全测试 JSON 报告"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None
    )

    args = parser.parse_args()

    reports = [
        load_report(path)
        for path in args.reports
    ]

    result = compare_reports(reports)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = (
            REPORT_DIR / "security_comparison.json"
        )

    save_comparison(result, output_path)
    print_comparison(result)

    print(f"\n对比报告已保存：{output_path}")


if __name__ == "__main__":
    main()
