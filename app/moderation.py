
def classify_content(content: str) -> dict:
    """
    判断内容是否合法，并进行风险分类。
    """

    # 1. 检查输入类型
    if not isinstance(content, str):
        raise TypeError("内容必须是字符串")

    # 2. 检查内容是否为空
    if len(content) == 0:
        raise ValueError("内容不能为空")

    # 3. 检查内容长度
    if len(content) > 500:
        raise ValueError("内容长度不能超过500个字符")

    # 4. 判断严重违规内容
    if "严重违规" in content:
        return {
            "decision": "block",
            "risk_level": "high"
        }

    # 5. 判断低风险内容
    if "低风险" in content:
        return {
            "decision": "review",
            "risk_level": "medium"
        }

    # 6. 普通内容
    return {
        "decision": "pass",
        "risk_level": "low"
    }
