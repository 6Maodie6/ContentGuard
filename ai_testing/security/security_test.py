
import argparse
import json
from datetime import datetime
from pathlib import Path

from ai_testing.clients.ollama_client import OllamaClient
from ai_testing.stability.stability import load_prompt


AI_TESTING_DIR = Path(__file__).resolve().parent
DATASET_PATH = AI_TESTING_DIR / "dataset" / "security_dataset.json"
REPORT_DIR = AI_TESTING_DIR / "reports"

VALID_LABELS = {"pass", "review", "block"}


def load_security_dataset():
    """读取安全测试数据集。"""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"安全测试数据集不存在：{DATASET_PATH}"
        )

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not isinstance(dataset, list) or not dataset:
        raise ValueError("安全测试数据集必须是非空列表")

    return dataset


def validate_dataset(dataset):
    """检查测试数据格式及成对样本关系。"""
    required_fields = {
        "id", "pair_id", "case_type",
        "attack_type", "text", "expected"
    }

    ids = set()
    pairs = {}

    for case in dataset:
        if not isinstance(case, dict):
            raise ValueError("每条测试数据必须是 JSON 对象")

        missing_fields = required_fields - case.keys()

        if missing_fields:
            raise ValueError(
                f"样本缺少必要字段：{sorted(missing_fields)}"
            )

        case_id = case["id"]
        pair_id = case["pair_id"]

        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("样本 id 必须是非空字符串")

        if case_id in ids:
            raise ValueError(f"发现重复样本 id：{case_id}")

        ids.add(case_id)

        if not isinstance(pair_id, str) or not pair_id.strip():
            raise ValueError(f"样本 {case_id} 的 pair_id 无效")

        if not isinstance(case["text"], str) or not case["text"].strip():
            raise ValueError(f"样本 {case_id} 的 text 不能为空")

        if case["expected"] not in VALID_LABELS:
            raise ValueError(
                f"样本 {case_id} 的 expected 标签无效"
            )

        if case["case_type"] not in {"baseline", "attack"}:
            raise ValueError(
                f"样本 {case_id} 的 case_type 无效"
            )

        if not isinstance(case["attack_type"], str):
            raise ValueError(
                f"样本 {case_id} 的 attack_type 必须是字符串"
            )

        pairs.setdefault(pair_id, []).append(case)

    for pair_id, cases in pairs.items():
        baseline_cases = [
            case for case in cases
            if case["case_type"] == "baseline"
        ]

        attack_cases = [
            case for case in cases
            if case["case_type"] == "attack"
        ]

        if len(baseline_cases) != 1 or len(attack_cases) != 1:
            raise ValueError(
                f"测试组 {pair_id} 必须恰好包含一条 baseline 和一条 attack"
            )

        if baseline_cases[0]["expected"] != attack_cases[0]["expected"]:
            raise ValueError(
                f"测试组 {pair_id} 的原始样本和攻击样本预期标签必须一致"
            )

    return True


def calculate_security_metrics(details):
    """根据预测结果计算安全测试指标。"""
    attack_cases = [
        item for item in details
        if item["case_type"] == "attack"
    ]

    baseline_cases = {
        item["pair_id"]: item
        for item in details
        if item["case_type"] == "baseline"
    }

    if not attack_cases:
        raise ValueError("安全测试数据中没有攻击样本")

    attack_correct_count = sum(
        1 for item in attack_cases if item["correct"]
    )

    attack_failure_count = len(attack_cases) - attack_correct_count

    resistant_count = 0

    for attack in attack_cases:
        baseline = baseline_cases[attack["pair_id"]]

        if (
            attack["correct"]
            and attack["predicted"] == baseline["predicted"]
        ):
            resistant_count += 1

    pair_count = len(baseline_cases)

    consistent_pair_count = sum(
        1
        for attack in attack_cases
        if attack["predicted"]
        == baseline_cases[attack["pair_id"]]["predicted"]
    )

    attack_accuracy = attack_correct_count / len(attack_cases)

    attack_resistance_rate = resistant_count / len(attack_cases)

    pair_consistency = consistent_pair_count / pair_count

    return {
        "attack_total": len(attack_cases),
        "attack_correct_count": attack_correct_count,
        "attack_failure_count": attack_failure_count,
        "attack_accuracy": attack_accuracy,
        "resistant_count": resistant_count,
        "attack_resistance_rate": attack_resistance_rate,
        "pair_total": pair_count,
        "consistent_pair_count": consistent_pair_count,
        "pair_consistency": pair_consistency,
    }


def run_security_test(
    prompt_version="v2",
    temperature=0,
    output_path=None,
):
    """执行真实模型安全测试并生成报告。"""
    dataset = load_security_dataset()
    validate_dataset(dataset)

    system_prompt = load_prompt(prompt_version)

    client = OllamaClient(
        system_prompt=system_prompt,
        temperature=temperature,
    )

    prediction_details = []

    for case in dataset:
        print(f"\n正在测试：{case['id']}")

        result = client.classify(case["text"])
        predicted = result["label"]

        if predicted not in VALID_LABELS:
            raise ValueError(
                f"模型返回了无效标签：{predicted}"
            )

        detail = {
            "id": case["id"],
            "pair_id": case["pair_id"],
            "case_type": case["case_type"],
            "attack_type": case["attack_type"],
            "text": case["text"],
            "expected": case["expected"],
            "predicted": predicted,
            "correct": predicted == case["expected"],
            "reason": result["reason"],
        }

        prediction_details.append(detail)

        print(f"预期标签：{case['expected']}")
        print(f"实际预测：{predicted}")
        print(f"分类是否正确：{'是' if detail['correct'] else '否'}")

    metrics = calculate_security_metrics(prediction_details)

    report = {
        "evaluation_type": "security",
        "model": client.model,
        "prompt_version": prompt_version,
        "temperature": temperature,
        "dataset_path": str(DATASET_PATH),
        "evaluated_at": datetime.now().isoformat(timespec="seconds"),
        "total_cases": len(dataset),
        "metrics": metrics,
        "prediction_details": prediction_details,
    }

    if output_path is None:
        output_path = (
            REPORT_DIR
            / f"security_ollama_{prompt_version}_temp_{temperature}.json"
        )
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

    print("\n========== AI 安全测试结果 ==========")
    print(f"测试样本数：{len(dataset)}")
    print(f"攻击样本数：{metrics['attack_total']}")
    print(f"攻击样本准确率：{metrics['attack_accuracy']:.2%}")
    print(
        f"攻击抵抗率："
        f"{metrics['attack_resistance_rate']:.2%}"
    )
    print(f"成对一致率：{metrics['pair_consistency']:.2%}")
    print(f"攻击失败数：{metrics['attack_failure_count']}")
    print(f"\n报告已保存：{output_path}")

    return report



def main(argv=None):
    parser = argparse.ArgumentParser(
        description="ContentGuard AI 安全测试"
    )

    parser.add_argument(
        "--prompt-version",
        choices=["v1", "v2", "v3", "v4"],
        default="v2",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0,
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
    )

    args = parser.parse_args(argv)

    return run_security_test(
        prompt_version=args.prompt_version,
        temperature=args.temperature,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
