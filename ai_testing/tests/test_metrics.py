
import pytest

from ai_testing.evaluation.metrics import evaluate_multiclass


def build_test_data():
    """构造一组已知结果的三分类测试数据。"""

    y_true = (
        ["pass"] * 50
        + ["review"] * 35
        + ["block"] * 15
    )

    y_pred = (
        ["pass"] * 40 + ["review"] * 5 + ["block"] * 5
        + ["pass"] * 4 + ["review"] * 26 + ["block"] * 5
        + ["pass"] * 3 + ["review"] * 2 + ["block"] * 10
    )

    return y_true, y_pred


def test_confusion_matrix():
    y_true, y_pred = build_test_data()

    result = evaluate_multiclass(
        y_true,
        y_pred,
        ["pass", "review", "block"]
    )

    matrix = result["confusion_matrix"]

    assert matrix["pass"]["pass"] == 40
    assert matrix["pass"]["review"] == 5
    assert matrix["review"]["block"] == 5
    assert matrix["block"]["block"] == 10


def test_accuracy():
    y_true, y_pred = build_test_data()

    result = evaluate_multiclass(
        y_true,
        y_pred,
        ["pass", "review", "block"]
    )

    assert result["accuracy"] == pytest.approx(0.76)


def test_block_metrics():
    y_true, y_pred = build_test_data()

    result = evaluate_multiclass(
        y_true,
        y_pred,
        ["pass", "review", "block"]
    )

    block = result["per_class"]["block"]

    assert block["TP"] == 10
    assert block["FP"] == 10
    assert block["FN"] == 5
    assert block["TN"] == 75

    assert block["precision"] == pytest.approx(0.5)
    assert block["recall"] == pytest.approx(10 / 15)


def test_macro_and_weighted_f1():
    y_true, y_pred = build_test_data()

    result = evaluate_multiclass(
        y_true,
        y_pred,
        ["pass", "review", "block"]
    )

    assert result["macro_f1"] == pytest.approx(
        (0.824742268 + 0.764705882 + 0.571428571) / 3
    )

    assert result["weighted_f1"] == pytest.approx(
        0.7657324786
    )


def test_different_length_should_raise_error():
    with pytest.raises(ValueError):
        evaluate_multiclass(
            ["pass", "block"],
            ["pass"],
            ["pass", "review", "block"]
        )


def test_unknown_label_should_raise_error():
    with pytest.raises(ValueError):
        evaluate_multiclass(
            ["pass", "unknown"],
            ["pass", "block"],
            ["pass", "review", "block"]
        )


def test_empty_data_should_raise_error():
    with pytest.raises(ValueError):
        evaluate_multiclass(
            [],
            [],
            ["pass", "review", "block"]
        )
