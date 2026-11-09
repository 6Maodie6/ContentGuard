import pytest

from app.moderation import classify_content


@pytest.mark.parametrize(
    "content, expected_exception",
    [
        pytest.param(123, TypeError, id="integer"),
        pytest.param(None, TypeError, id="none"),
        pytest.param("", ValueError, id="empty"),
        pytest.param("A" * 501, ValueError, id="too-long"),
    ],
)
def test_classify_content_invalid_input(content, expected_exception):
    """直接测试分类函数对非法输入的处理"""

    with pytest.raises(expected_exception):
        classify_content(content)