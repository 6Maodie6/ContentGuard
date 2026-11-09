import json
from pathlib import Path

import pytest


# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 拼接 JSON 测试数据文件路径
DATA_FILE = PROJECT_ROOT / "data" / "moderation_cases.json"

# 读取 JSON 文件
with open(DATA_FILE, "r", encoding="utf-8") as file:
    test_cases = json.load(file)


@pytest.mark.parametrize("case", 
                         test_cases,
                         ids=[case["case_name"] for case in test_cases])
def test_moderation_cases(client, case):
    response = client.post(
        "/api/v1/moderation/tasks",
        json={"content": case["content"]}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["decision"] == case["expected_decision"]
    assert data["risk_level"] == case["expected_risk_level"]