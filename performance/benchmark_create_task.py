import sys
from pathlib import Path

# 将项目根目录加入 Python 模块搜索路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import time
from uuid import uuid4

from app.moderation import classify_content




CONTENT = "这是一条普通内容"
TASK_COUNT = 100_000


def benchmark(name, func):
    # 预热，减少首次执行的影响
    for _ in range(1_000):
        func()

    start = time.perf_counter()

    for _ in range(TASK_COUNT):
        func()

    elapsed = time.perf_counter() - start

    print(
        f"{name}: "
        f"总耗时={elapsed:.6f}s, "
        f"平均耗时={elapsed / TASK_COUNT * 1_000_000:.3f}μs/次"
    )


def classify():
    return classify_content(CONTENT)


def generate_id():
    return str(uuid4())


def determine_status():
    result = {"decision": "pass"}

    if result["decision"] == "review":
        return "pending"

    return "completed"


def build_task():
    result = classify_content(CONTENT)
    task_id = str(uuid4())

    if result["decision"] == "review":
        status = "pending"
    else:
        status = "completed"

    return {
        "task_id": task_id,
        "status": status,
        "decision": result["decision"],
        "risk_level": result["risk_level"],
        "content": CONTENT,
    }


def save_task():
    task_id = str(uuid4())
    task = {"task_id": task_id}
    task_store = {}
    task_store[task_id] = task


if __name__ == "__main__":
    benchmark("内容分类", classify)
    benchmark("UUID生成", generate_id)
    benchmark("状态判断", determine_status)
    benchmark("任务组装（含分类和UUID）", build_task)
    benchmark("字典创建及写入", save_task)
