
import pytest


# ==========================================
# 1. 内容长度边界值测试
# ==========================================

@pytest.mark.parametrize(
    "content, expected_status, expected_decision",
    [
        pytest.param("", 400, None, id="length-0"),
        pytest.param("A", 200, "pass", id="length-1"),
        pytest.param("AB", 200, "pass", id="length-2"),
        pytest.param("A" * 499, 200, "pass", id="length-499"),
        pytest.param("A" * 500, 200, "pass", id="length-500"),
        pytest.param("A" * 501, 400, None, id="length-501"),
    ],
)
def test_content_length_boundary(
    client, content, expected_status, expected_decision
):
    """测试内容长度边界值"""

    response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": content}
    )

    assert response.status_code == expected_status

    if expected_decision is not None:
        assert response.json()["decision"] == expected_decision


# ==========================================
# 2. 非法输入类型等价类测试
# ==========================================

@pytest.mark.parametrize(
    "content",
    [
        pytest.param(123, id="integer"),
        pytest.param(12.5, id="float"),
        pytest.param(True, id="boolean"),
        pytest.param(["测试内容"], id="list"),
        pytest.param({"text": "测试内容"}, id="object"),
    ],
)
def test_invalid_content_type(client, content):
    """测试各种非字符串类型"""

    response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": content}
    )

    assert response.status_code == 422


# ==========================================
# 3. 缺失字段和空值测试
# ==========================================

@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="missing-content"),
        pytest.param({"content": None}, id="null-content"),
    ],
)
def test_missing_or_null_content(client, payload):
    """测试缺失content字段和null值"""

    response = client.post(
        "/api/v1/moderation/tasks",
        json=payload
    )

    assert response.status_code == 422


# ==========================================
# 4. 任务查询异常测试
# ==========================================

def test_missing_task(client):
    """查询不存在的任务应该返回404"""

    response = client.get(
        "/api/v1/moderation/tasks/not-exist"
    )

    assert response.status_code == 404
