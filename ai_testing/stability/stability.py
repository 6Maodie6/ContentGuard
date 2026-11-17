
import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from ai_testing.clients.ollama_client import OllamaClient, MODEL_NAME
from ai_testing.prompts.prompt_v1 import SYSTEM_PROMPT
from ai_testing.prompts.prompt_v2 import SYSTEM_PROMPT_V2
from ai_testing.prompts.prompt_v3 import SYSTEM_PROMPT_V3
from ai_testing.prompts.prompt_v4 import SYSTEM_PROMPT_V4

AI_TESTING_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = AI_TESTING_DIR / "dataset" / "golden_dataset.json"
REPORT_DIR = AI_TESTING_DIR / "reports" / "stability_reports"

LABELS = {"pass", "review", "block"}


def load_prompt(prompt_version):
    """根据版本加载对应的 Prompt。"""

    if prompt_version == "v1":
        return SYSTEM_PROMPT

    if prompt_version == "v2":
        return SYSTEM_PROMPT_V2

    if prompt_version == "v3":
        return SYSTEM_PROMPT_V3

    if prompt_version == "v4":
        return SYSTEM_PROMPT_V4

    raise ValueError(f"不支持的 Prompt 版本：{prompt_version}")


def run_stability_test(
    repeats=3,
    prompt_version="v2",
    max_cases=3,
    output_path=None,
    temperature=0
):
    """重复运行模型审核，评估预测结果的一致性。"""

    if repeats < 2:
        raise ValueError("重复测试次数至少为 2")

    if max_cases < 1:
        raise ValueError("测试样本数量至少为 1")

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    # 只选择有效的三分类样本
    valid_cases = [
        case for case in dataset
        if case.get("expected") in LABELS
        and isinstance(case.get("text"), str)
        and case["text"].strip()
    ]

    selected_cases = valid_cases[:max_cases]

    if not selected_cases:
        raise ValueError("Golden Dataset 中没有有效测试样本")

    system_prompt = load_prompt(prompt_version)
    client = OllamaClient(
    system_prompt=system_prompt,
    temperature=temperature
)

    prediction_details = []

    for case in selected_cases:
        predictions = []
        reasons = []

        print(f"\n正在测试：{case['id']}")

        for i in range(repeats):
            result = client.classify(case["text"])

            predictions.append(result["label"])
            reasons.append(result["reason"])

            print(f"第 {i + 1} 次预测：{result['label']}")

        counts = Counter(predictions)
        most_common_count = counts.most_common(1)[0][1]

        agreement_rate = most_common_count / repeats
        stable = len(counts) == 1

        prediction_details.append({
            "id": case["id"],
            "text": case["text"],
            "expected": case["expected"],
            "predictions": predictions,
            "prediction_counts": dict(counts),
            "reasons": reasons,
            "agreement_rate": agreement_rate,
            "stable": stable
        })

    total_cases = len(prediction_details)

    stable_cases = sum(
        item["stable"] for item in prediction_details
    )

    average_agreement_rate = sum(
        item["agreement_rate"] for item in prediction_details
    ) / total_cases

    report = {
        "evaluation_type": "stability",
        "model": MODEL_NAME,
        "prompt_version": prompt_version,
        "temperature": temperature,
        "repeats": repeats,
        "total_cases": total_cases,
        "stable_cases": stable_cases,
        "unstable_cases": total_cases - stable_cases,
        "case_stability_rate": stable_cases / total_cases,
        "average_agreement_rate": average_agreement_rate,
        "evaluated_at": datetime.now().isoformat(timespec="seconds"),
        "prediction_details": prediction_details
    }

    if output_path is None:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = (
            REPORT_DIR /
            f"stability_ollama_{prompt_version}_temp_{temperature}.json"
        )
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    print("\n========== 模型稳定性测试结果 ==========")
    print(f"测试样本数：{total_cases}")
    print(f"每条样本重复次数：{repeats}")
    print(f"完全稳定样本：{stable_cases}")
    print(f"不稳定样本：{total_cases - stable_cases}")
    print(f"完全稳定率：{report['case_stability_rate']:.2%}")
    print(f"平均一致率：{average_agreement_rate:.2%}")
    print(f"\n报告已保存：{output_path}")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ContentGuard AI 模型稳定性测试"
    )

    parser.add_argument(
        "--repeats",
        type=int,
        default=3
    )

    parser.add_argument(
        "--prompt-version",
        choices=["v1","v2","v3","v4"],
        default="v2"
    )

    parser.add_argument(
        "--max-cases",
        type=int,
        default=3
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0
    )

    args = parser.parse_args()

    run_stability_test(
        repeats=args.repeats,
        prompt_version=args.prompt_version,
        max_cases=args.max_cases,
        output_path=args.output,
        temperature=args.temperature
    )
