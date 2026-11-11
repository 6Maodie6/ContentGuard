
def classify_content(content: str) -> dict:
    if not isinstance(content, str):
        raise TypeError("内容必须是字符串")

    if len(content) == 0:
        raise ValueError("内容不能为空")

    if len(content) > 500:
        raise ValueError("内容长度不能超过500个字符")

    if "严重违规" in content:
        return {"decision": "block", "risk_level": "high"}

    if "低风险" in content:
        return {"decision": "review", "risk_level": "medium"}

    return {"decision": "pass", "risk_level": "low"}
