
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.moderation import classify_content


app = FastAPI(title="ContentGuard API")


# 临时任务存储
task_store = {}


# 创建审核请求的数据结构
class ModerationRequest(BaseModel):
    content: str


# 创建人工审核请求的数据结构
class ManualReviewRequest(BaseModel):
    decision: str


# 1. 创建审核任务
@app.post("/api/v1/moderation/tasks")
def create_moderation_task(request: ModerationRequest):

    try:
        result = classify_content(request.content)
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    task_id = str(uuid4())

    # review 任务等待人工审核，其他任务直接完成
    if result["decision"] == "review":
        status = "pending"
    else:
        status = "completed"

    task = {
        "task_id": task_id,
        "status": status,
        "decision": result["decision"],
        "risk_level": result["risk_level"],
        "content": request.content
    }

    # 保存任务
    task_store[task_id] = task

    return task


# 2. 根据任务 ID 查询审核任务
@app.get("/api/v1/moderation/tasks/{task_id}")
def get_moderation_task(task_id: str):

    if task_id not in task_store:
        raise HTTPException(
            status_code=404,
            detail="审核任务不存在"
        )

    return task_store[task_id]


# 3. 人工审核
@app.post("/api/v1/moderation/tasks/{task_id}/manual-review")
def manual_review(
    task_id: str,
    request: ManualReviewRequest
):

    # 检查任务是否存在
    if task_id not in task_store:
        raise HTTPException(
            status_code=404,
            detail="审核任务不存在"
        )

    task = task_store[task_id]

    # 只允许审核 pending 状态的任务
    if task["status"] != "pending":
        raise HTTPException(
            status_code=409,
            detail="该任务已经完成，不能重复审核"
        )

    # 检查人工审核结果是否合法
    if request.decision not in ["pass", "block"]:
        raise HTTPException(
            status_code=400,
            detail="人工审核结果只能是 pass 或 block"
        )

    # 更新任务
    task["decision"] = request.decision
    task["status"] = "completed"

    if request.decision == "pass":
        task["risk_level"] = "low"
    else:
        task["risk_level"] = "high"

    return task
