
def test_manual_review_workflow(client):
    """测试完整人工审核流程"""

    # 第一步：创建待人工审核任务
    create_response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": "这是一段低风险内容"}
    )

    assert create_response.status_code == 200

    task = create_response.json()
    task_id = task["task_id"]

    assert task["status"] == "pending"
    assert task["decision"] == "review"

    # 第二步：查询任务
    get_response = client.get(
        f"/api/v1/moderation/tasks/{task_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["task_id"] == task_id

    # 第三步：人工审核，判定为 block
    review_response = client.post(
        f"/api/v1/moderation/tasks/{task_id}/manual-review",
        json={"decision": "block"}
    )

    assert review_response.status_code == 200

    reviewed_task = review_response.json()

    assert reviewed_task["status"] == "completed"
    assert reviewed_task["decision"] == "block"
    assert reviewed_task["risk_level"] == "high"

    # 第四步：再次审核，应该失败
    repeat_response = client.post(
        f"/api/v1/moderation/tasks/{task_id}/manual-review",
        json={"decision": "pass"}
    )

    assert repeat_response.status_code == 409


def test_invalid_manual_decision(client):
    """人工审核不允许使用非法结果"""

    create_response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": "这是一段低风险内容"}
    )

    task_id = create_response.json()["task_id"]

    review_response = client.post(
        f"/api/v1/moderation/tasks/{task_id}/manual-review",
        json={"decision": "unknown"}
    )

    assert review_response.status_code == 400
