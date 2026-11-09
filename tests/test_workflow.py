
import pytest


def create_review_task(client):
    """创建一个等待人工审核的低风险任务"""

    response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": "这是一条低风险测试内容"}
    )

    assert response.status_code == 200

    task_id = response.json()["task_id"]
    return task_id


def test_create_review_task(client):
    """创建低风险任务后，状态应该是pending"""

    response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": "这是一条低风险测试内容"}
    )

    assert response.status_code == 200

    task = response.json()

    assert task["status"] == "pending"
    assert task["decision"] == "review"


@pytest.mark.parametrize(
    "decision",
    [
        pytest.param("pass", id="manual-pass"),
        pytest.param("block", id="manual-block"),
    ],
)
def test_manual_review_success(client, decision):
    """pending任务经过合法人工审核后应该变成completed"""

    task_id = create_review_task(client)

    response = client.post(
        f"/api/v1/moderation/tasks/{task_id}/manual-review",
        json={"decision": decision}
    )

    assert response.status_code == 200

    task = response.json()

    assert task["status"] == "completed"
    assert task["decision"] == decision


def test_cannot_review_completed_task(client):
    """已经完成的任务不能再次人工审核"""

    task_id = create_review_task(client)

    # 第一次人工审核，完成任务
    first_response = client.post(
        f"/api/v1/moderation/tasks/{task_id}/manual-review",
        json={"decision": "pass"}
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "completed"

    # 第二次人工审核，应该被拒绝
    second_response = client.post(
        f"/api/v1/moderation/tasks/{task_id}/manual-review",
        json={"decision": "block"}
    )

    assert second_response.status_code == 409

    # 再次查询，确认原来的审核结果没有被改变
    query_response = client.get(
        f"/api/v1/moderation/tasks/{task_id}"
    )

    assert query_response.status_code == 200
    assert query_response.json()["status"] == "completed"
    assert query_response.json()["decision"] == "pass"


def test_invalid_review_decision(client):
    """非法人工审核结果应该被拒绝"""

    task_id = create_review_task(client)

    response = client.post(
        f"/api/v1/moderation/tasks/{task_id}/manual-review",
        json={"decision": "unknown"}
    )

    assert response.status_code == 400


def test_invalid_review_does_not_change_task_status(client):
    """非法审核操作不能改变任务原来的pending状态"""

    task_id = create_review_task(client)

    # 提交非法审核结果
    response = client.post(
        f"/api/v1/moderation/tasks/{task_id}/manual-review",
        json={"decision": "unknown"}
    )

    assert response.status_code == 400

    # 查询任务，确认状态没有改变
    query_response = client.get(
        f"/api/v1/moderation/tasks/{task_id}"
    )

    assert query_response.status_code == 200

    task = query_response.json()

    assert task["status"] == "pending"
    assert task["decision"] == "review"



def test_manual_review_missing_task(client):
    """对不存在的任务进行人工审核，应该返回404"""

    response = client.post(
        "/api/v1/moderation/tasks/not-exist/manual-review",
        json={"decision": "pass"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "审核任务不存在"