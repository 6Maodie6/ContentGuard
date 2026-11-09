
def test_empty_content(client):
    """空内容应该被拒绝"""

    response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": ""}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "内容不能为空"


def test_content_exceeds_limit(client):
    """超过500个字符应该被拒绝"""

    response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": "A" * 501}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "内容长度不能超过500个字符"


def test_content_is_not_string(client):
    """非字符串输入应该被拒绝"""

    response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": 123}
    )

    assert response.status_code == 422


def test_content_at_max_length(client):
    """刚好500个字符应该允许通过"""

    response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": "A" * 500}
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "pass"


def test_missing_task(client):
    """查询不存在的任务应该返回404"""

    response = client.get(
        "/api/v1/moderation/tasks/not-exist"
    )

    assert response.status_code == 404
