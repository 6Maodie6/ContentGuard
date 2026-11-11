
from locust import HttpUser, task, between


class ContentGuardUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def moderation_workflow(self):
        # 第一步：创建一个需要人工审核的任务
        with self.client.post(
            "/api/v1/moderation/tasks",
            json={"content": "这是一条低风险内容"},
            catch_response=True,
            name="1. 创建审核任务"
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"创建任务失败：HTTP {response.status_code}"
                )
                return

            try:
                result = response.json()
                task_id = result["task_id"]

                if result.get("status") != "pending":
                    response.failure(
                        f"任务状态不符合预期：{result.get('status')}"
                    )
                    return

                response.success()

            except (ValueError, KeyError) as e:
                response.failure(f"创建任务响应解析失败：{e}")
                return

        # 第二步：查询任务
        with self.client.get(
            f"/api/v1/moderation/tasks/{task_id}",
            catch_response=True,
            name="2. 查询审核任务"
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"查询任务失败：HTTP {response.status_code}"
                )
                return

            try:
                result = response.json()

                if result.get("status") != "pending":
                    response.failure("查询到的任务状态不是 pending")
                    return

                response.success()

            except ValueError as e:
                response.failure(f"查询响应解析失败：{e}")
                return

        # 第三步：提交人工审核
        with self.client.post(
            f"/api/v1/moderation/tasks/{task_id}/manual-review",
            json={"decision": "pass"},
            catch_response=True,
            name="3. 人工审核任务"
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"人工审核失败：HTTP {response.status_code}"
                )
                return

            response.success()

        # 第四步：再次查询，确认审核完成
        with self.client.get(
            f"/api/v1/moderation/tasks/{task_id}",
            catch_response=True,
            name="4. 查询审核结果"
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"审核后查询失败：HTTP {response.status_code}"
                )
                return

            try:
                result = response.json()

                if result.get("status") != "completed":
                    response.failure("人工审核后任务没有完成")
                    return

                if result.get("decision") != "pass":
                    response.failure("最终审核结果不是 pass")
                    return

                response.success()

            except ValueError as e:
                response.failure(f"最终响应解析失败：{e}")
