import pytest

from app.moderation_v2 import classify_content_v2


@pytest.mark.parametrize(
    "content, expected_exception",
    [
        pytest.param(123, TypeError, id="integer"),
        pytest.param(None, TypeError, id="none"),
        pytest.param("", ValueError, id="empty"),
        pytest.param("A" * 501, ValueError, id="too-long"),
    ],
)
def test_v2_invalid_input(content, expected_exception):
    """测试 V2 对非法输入的处理"""

    with pytest.raises(expected_exception):
        classify_content_v2(content)


@pytest.mark.parametrize(
    "content, expected_decision",
    [
        pytest.param("这是一条普通内容", "pass", id="normal"),
        pytest.param("这是一条低风险内容", "review", id="low-risk"),
        pytest.param("这是一条严重违规内容", "block", id="high-risk"),
        pytest.param("这是一条诈骗内容", "block", id="fraud"),
    ],
)
def test_v2_classification(content, expected_decision):
    """测试 V2 的内容分类规则"""

    result = classify_content_v2(content)

    assert result["decision"] == expected_decision