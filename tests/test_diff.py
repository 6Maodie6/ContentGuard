import json
from pathlib import Path

import pytest

from app.moderation import classify_content
from app.moderation_v2 import classify_content_v2


# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 读取 Diff 测试数据
DATA_FILE = PROJECT_ROOT / "data" / "diff_cases.json"

with open(DATA_FILE, "r", encoding="utf-8") as file:
    diff_cases = json.load(file)


@pytest.mark.parametrize(
    "case",
    diff_cases,
    ids=[case["case_name"] for case in diff_cases]
)
def test_moderation_diff(case):
    content = case["content"]

    # 分别使用新旧版本处理相同输入
    old_result = classify_content(content)
    new_result = classify_content_v2(content)

    # 比较两个版本的审核结果
    actual_diff = old_result != new_result

    # 检查实际差异是否符合预期
    assert actual_diff == case["expected_diff"], (
        f"用例：{case['case_name']}\n"
        f"旧版本结果：{old_result}\n"
        f"新版本结果：{new_result}\n"
        f"预期是否存在差异：{case['expected_diff']}\n"
        f"实际是否存在差异：{actual_diff}"
    )