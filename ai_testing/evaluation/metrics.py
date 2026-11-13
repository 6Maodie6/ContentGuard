
def evaluate_multiclass(y_true, y_pred, labels):
    """
    计算多分类模型的混淆矩阵和评估指标。

    y_true: 真实标签列表
    y_pred: 模型预测标签列表
    labels: 所有类别，例如 ["pass", "review", "block"]
    """

    if len(y_true) != len(y_pred):
        raise ValueError("真实标签数量与预测标签数量不一致")

    if not labels or len(set(labels)) != len(labels):
        raise ValueError("labels 不能为空，且不能包含重复类别")

    if not y_true:
        raise ValueError("测试数据不能为空")

    # 检查标签是否合法
    for label in y_true + y_pred:
        if label not in labels:
            raise ValueError(f"发现未定义的标签：{label}")

    # 初始化混淆矩阵：行是真实标签，列是预测标签
    matrix = {
        true_label: {pred_label: 0 for pred_label in labels}
        for true_label in labels
    }

    # 统计每一种真实标签和预测标签的组合
    for true_label, pred_label in zip(y_true, y_pred):
        matrix[true_label][pred_label] += 1

    total = len(y_true)
    correct = sum(
        matrix[label][label]
        for label in labels
    )

    # 计算整体准确率
    accuracy = correct / total

    per_class = {}

    for label in labels:
        # 对当前类别采用 One-vs-Rest 计算方式
        tp = matrix[label][label]

        fp = sum(
            matrix[other][label]
            for other in labels
            if other != label
        )

        fn = sum(
            matrix[label][other]
            for other in labels
            if other != label
        )

        support = sum(matrix[label].values())

        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0

        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0
        )

        per_class[label] = {
            "TP": tp,
            "FP": fp,
            "FN": fn,
            "TN": total - tp - fp - fn,
            "support": support,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    # Macro-F1：各类别 F1 的简单平均
    macro_f1 = sum(
        per_class[label]["f1"]
        for label in labels
    ) / len(labels)

    # Weighted-F1：按照各类别真实样本数量加权
    weighted_f1 = sum(
        per_class[label]["f1"] * per_class[label]["support"]
        for label in labels
    ) / total

    return {
        "total": total,
        "accuracy": accuracy,
        "confusion_matrix": matrix,
        "per_class": per_class,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
    }
