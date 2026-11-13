import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


AI_TESTING_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = AI_TESTING_DIR / "reports" / "stability_reports"

DEFAULT_REPORTS = [
    REPORT_DIR / "stability_ollama_v2.json",
    REPORT_DIR / "stability_ollama_v2_temp_0.3.json",
    REPORT_DIR / "stability_ollama_v2_temp_0.7.json",
]


def load_report(path):
    """读取一份稳定性测试报告。"""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"报告不存在：{path}")

    with path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    return report


def get_case_counts(case):
    """提取单条样本的各标签预测次数。"""
    counts = case.get("counts")

    if isinstance(counts, dict):
        return dict(counts)

    predictions = case.get("predictions")

    if isinstance(predictions, list):
        return dict(Counter(predictions))

    raise ValueError(
        f"样本 {case.get('id')} 缺少有效的 counts 或 predictions"
    )


def analyze_report(report, path):
    """提取一份报告的总体指标和单条样本结果。"""
    details = report.get("prediction_details")

    if not isinstance(details, list) or not details:
        raise ValueError(
            f"报告缺少有效的 prediction_details：{path}"
        )

    cases = {}

    for case in details:
        case_id = case.get("id")

        if not case_id:
            raise ValueError(f"报告中存在缺少 id 的样本：{path}")

        counts = get_case_counts(case)
        total_predictions = sum(counts.values())

        if total_predictions == 0:
            raise ValueError(f"样本 {case_id} 没有预测记录")

        max_count = max(counts.values())
        agreement_rate = max_count / total_predictions

        cases[case_id] = {
            "counts": counts,
            "agreement_rate": agreement_rate,
            "stable": len(counts) == 1,
        }

    total_cases = len(cases)
    stable_cases = sum(
        1 for case in cases.values() if case["stable"]
    )

    case_stability_rate = stable_cases / total_cases

    average_agreement_rate = sum(
        case["agreement_rate"] for case in cases.values()
    ) / total_cases

    return {
        "file": str(path),
        "model": report.get("model"),
        "prompt_version": report.get("prompt_version"),
        "temperature": report.get("temperature"),
        "repeats": report.get("repeats"),
        "total_cases": total_cases,
        "stable_cases": stable_cases,
        "unstable_cases": total_cases - stable_cases,
        "case_stability_rate": case_stability_rate,
        "average_agreement_rate": average_agreement_rate,
        "cases": cases,
    }


def validate_reports(results):
    """检查几份报告是否具备可比性。"""
    first = results[0]

    for result in results[1:]:
        if result["model"] != first["model"]:
            raise ValueError("模型不一致，不能直接比较")

        if result["prompt_version"] != first["prompt_version"]:
            raise ValueError("Prompt 版本不一致，不能直接比较")

        if result["repeats"] != first["repeats"]:
            raise ValueError("每条样本重复次数不一致，不能直接比较")

        if set(result["cases"]) != set(first["cases"]):
            raise ValueError("测试样本不一致，不能直接比较")

    temperatures = [result["temperature"] for result in results]

    if len(set(temperatures)) != len(temperatures):
        raise ValueError("存在重复的 Temperature，无法进行有效对比")


def compare_stability(report_paths, output_path=None):
    """比较多份稳定性报告并生成 JSON 对比结果。"""
    results = []

    for path in report_paths:
        report = load_report(path)
        result = analyze_report(report, path)
        results.append(result)

    if len(results) < 2:
        raise ValueError("至少需要两份报告才能进行对比")

    validate_reports(results)

    results.sort(key=lambda item: float(item["temperature"]))

    summary = []

    for result in results:
        summary.append({
            "temperature": result["temperature"],
            "total_cases": result["total_cases"],
            "stable_cases": result["stable_cases"],
            "unstable_cases": result["unstable_cases"],
            "case_stability_rate": result["case_stability_rate"],
            "average_agreement_rate": result["average_agreement_rate"],
        })

    case_comparison = {}

    case_ids = results[0]["cases"].keys()

    for case_id in case_ids:
        case_comparison[case_id] = {}

        for result in results:
            case = result["cases"][case_id]
            temperature = str(result["temperature"])

            case_comparison[case_id][temperature] = {
                "counts": case["counts"],
                "agreement_rate": case["agreement_rate"],
                "stable": case["stable"],
            }

    comparison = {
        "comparison_type": "stability",
        "model": results[0]["model"],
        "prompt_version": results[0]["prompt_version"],
        "repeats": results[0]["repeats"],
        "compared_at": datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
        "case_comparison": case_comparison,
    }

    if output_path is None:
        output_path = (
            REPORT_DIR
            / f"stability_comparison_{results[0]['prompt_version']}.json"
        )
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            comparison,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n========== 稳定性对比结果 ==========")

    for item in summary:
        print(f"\nTemperature：{item['temperature']}")
        print(f"完全稳定率：{item['case_stability_rate']:.2%}")
        print(f"平均一致率：{item['average_agreement_rate']:.2%}")
        print(f"不稳定样本数：{item['unstable_cases']}")

    print(f"\n对比报告已保存：{output_path}")

    return comparison



def main(argv=None):
    parser = argparse.ArgumentParser(
        description="ContentGuard AI 模型稳定性报告对比工具"
    )

    parser.add_argument(
        "--reports",
        nargs="+",
        default=[str(path) for path in DEFAULT_REPORTS],
        help="需要对比的稳定性报告路径",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="对比报告保存路径",
    )

    args = parser.parse_args(argv)

    return compare_stability(
        report_paths=args.reports,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
