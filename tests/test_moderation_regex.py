import pytest

from app.moderation import classify_content


@pytest.mark.parametrize(
    "content, expected",
    [
        (
            "这是一段普通内容",
            {"decision": "pass", "risk_level": "low"}
        ),
        (
            "这是一段低风险内容",
            {"decision": "review", "risk_level": "medium"}
        ),
        (
            "这是一段严重违规内容",
            {"decision": "block", "risk_level": "high"}
        ),
        (
            "同时包含低风险和严重违规",
            {"decision": "block", "risk_level": "high"}
        ),
        (
            "严重违规内容出现在开头",
            {"decision": "block", "risk_level": "high"}
        ),
        (
            "普通内容" * 100 + "低风险",
            {"decision": "review", "risk_level": "medium"}
        ),
        (
            "普通内容" * 100,
            {"decision": "pass", "risk_level": "low"}
        ),
    ]
)
def test_classify_content_regex(content, expected):
    assert classify_content(content) == expected


@pytest.mark.parametrize("content", [123, None, [], {}])
def test_classify_content_invalid_type(content):
    with pytest.raises(TypeError):
        classify_content(content)


@pytest.mark.parametrize("content", ["", " " * 501])
def test_classify_content_invalid_value(content):
    with pytest.raises(ValueError):
        classify_content(content)


def test_classify_content_max_length():
    content = "普" * 500

    assert classify_content(content) == {
        "decision": "pass",
        "risk_level": "low"
    }


def test_classify_content_over_max_length():
    content = "普" * 501

    with pytest.raises(ValueError):
        classify_content(content)