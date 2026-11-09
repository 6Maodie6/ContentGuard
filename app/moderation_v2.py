def classify_content_v2(content: str) -> dict:
    """
    ContentGuard 新版审核规则 V2。
    在 V1 的基础上，新增诈骗内容识别。
    """
    if not isinstance(content, str):
        raise TypeError("内容必须是字符串")

    if len(content) == 0:
        raise ValueError("内容不能为空")

    if len(content) > 500:
        raise ValueError("内容长度不能超过500个字符")

    if "严重违规" in content:
        return {
            "decision": "block",
            "risk_level": "high"
        }

    # V2 新增规则
    if "诈骗" in content:
        return {
            "decision": "block",
            "risk_level": "high"
        }

    if "低风险" in content:
        return {
            "decision": "review",
            "risk_level": "medium"
        }

    return {
        "decision": "pass",
        "risk_level": "low"
    }