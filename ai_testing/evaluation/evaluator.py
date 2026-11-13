
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from ai_testing.evaluation.metrics import evaluate_multiclass


# 项目目录
AI_TESTING_DIR = Path(__file__).resolve().parent.parent

# 数据集路径
DATASET_PATH = AI_TESTING_DIR / "dataset" / "golden_dataset.json"

# 报告目录
REPORT_DIR = AI_TESTING_DIR / "reports"

# 当前模型支持的分类标签
LABELS = ["pass", "review", "block"]


def load_dataset():
    """读取 Golden Dataset。"""

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not isinstance(dataset, list):
        raise ValueError("Golden Dataset 必须是 JSON 数组")

    return dataset


def load_prompt(prompt_version):
    """根据版本加载对应的 Prompt。"""

    if prompt_version == "v1":
        from ai_testing.prompts.prompt_v1 import SYSTEM_PROMPT
        return SYSTEM_PROMPT

    if prompt_version == "v2":
        from ai_testing.prompts.prompt_v2 import SYSTEM_PROMPT_V2
        return SYSTEM_PROMPT_V2

    raise ValueError("prompt_version 只能是 v1 或 v2")


def mock_predict(case, index):
    """模拟模型预测，仅用于验证评估流程。"""

    mock_labels = ["pass", "review", "block"]

    return {
        "label": mock_labels[index % len(mock_labels)],
        "reason": "这是模拟预测结果"
    }


def run_evaluation(
    mode="mock",
    prompt_version="v1",
    output_path=None
):
    """
    执行模型评估并生成 JSON 报告。

    mode:
        mock   - 使用模拟预测
        ollama - 使用本地模型预测

    prompt_version:
        v1 - 使用旧版 Prompt
        v2 - 使用新版 Prompt
    """

    if mode not in {"mock", "ollama"}:
        raise ValueError("mode 只能是 mock 或 ollama")

    if prompt_version not in {"v1", "v2"}:
        raise ValueError("prompt_version 只能是 v1 或 v2")

    # 只有真实模型模式才需要加载 Prompt 和创建客户端
    client = None

    if mode == "ollama":
        system_prompt = load_prompt(prompt_version)

        from ai_testing.clients.ollama_client import OllamaClient

        client = OllamaClient(system_prompt=system_prompt)

    dataset = load_dataset()

    y_true = []
    y_pred = []

    invalid_cases = []
    prediction_details = []

    for index, case in enumerate(dataset):
        case_id = case.get("id", f"UNKNOWN_{index}")

        if "text" not in case or "expected" not in case:
            raise ValueError(f"测试用例 {case_id} 缺少必要字段")

        text = case["text"]
        expected = case["expected"]

        # invalid 样本不参与三分类指标计算
        if expected == "invalid":
            invalid_cases.append(case_id)
            continue

        if expected not in LABELS:
            raise ValueError(
                f"测试用例 {case_id} 存在未知标准标签：{expected}"
            )

        # 根据模式选择预测方式
        if mode == "mock":
            result = mock_predict(case, index)
        else:
            result = client.classify(text)

        predicted = result["label"]
        reason = result["reason"]

        if predicted not in LABELS:
            raise ValueError(
                f"测试用例 {case_id} 返回未知预测标签：{predicted}"
            )

        y_true.append(expected)
        y_pred.append(predicted)

        prediction_details.append({
            "id": case_id,
            "text": text,
            "expected": expected,
            "predicted": predicted,
            "correct": expected == predicted,
            "reason": reason
        })

        print(
            f"[{len(y_true)}] {case_id} | "
            f"真实标签：{expected} | "
            f"预测标签：{predicted} | "
            f"{'正确' if expected == predicted else '错误'}"
        )

    if not y_true:
        raise ValueError("没有可用于三分类评估的有效样本")

    # 计算分类指标
    metrics = evaluate_multiclass(
        y_true,
        y_pred,
        LABELS
    )

    # 确定报告保存路径
    if output_path is None:
        output_path = REPORT_DIR / (
            f"evaluation_{mode}_{prompt_version}.json"
        )
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 生成评估报告
    report = {
        "evaluation_type": mode,
        "prompt_version": prompt_version if mode == "ollama" else None,
        "model": client.model if client else None,
        "temperature": 0 if client else None,
        "dataset_path": str(DATASET_PATH),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "total_dataset_cases": len(dataset),
        "evaluated_cases": len(y_true),
        "invalid_cases": len(invalid_cases),
        "invalid_case_ids": invalid_cases,
        "prediction_details": prediction_details,
        "metrics": metrics
    }

    # 保存 JSON 报告
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n========== 评估结果 ==========")
    print(f"评估模式：{mode}")
    print(f"Prompt 版本：{prompt_version}")

    if client:
        print(f"使用模型：{client.model}")

    print(f"数据集总数：{len(dataset)}")
    print(f"有效评估数：{len(y_true)}")
    print(f"无效样本数：{len(invalid_cases)}")
    print(f"Accuracy：{metrics['accuracy']:.2%}")
    print(f"Macro-F1：{metrics['macro_f1']:.2%}")
    print(f"Weighted-F1：{metrics['weighted_f1']:.2%}")
    print(f"报告已保存到：{output_path}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="ContentGuard AI Prompt 版本回归评估工具"
    )

    parser.add_argument(
        "--mode",
        choices=["mock", "ollama"],
        default="mock",
        help="选择评估模式：mock 或 ollama"
    )

    parser.add_argument(
        "--prompt-version",
        choices=["v1", "v2"],
        default="v1",
        help="选择 Prompt 版本：v1 或 v2"
    )

    parser.add_argument(
        "--output",
        default=None,
        help="自定义评估报告保存路径"
    )

    args = parser.parse_args()

    return run_evaluation(
        mode=args.mode,
        prompt_version=args.prompt_version,
        output_path=args.output
    )


if __name__ == "__main__":
    main()