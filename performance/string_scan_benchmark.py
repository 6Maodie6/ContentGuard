
import re
import time


# =========================
# 1. 构造模拟审核关键词
# =========================

high_risk_keywords = ["严重违规", "诈骗"] + [
    f"模拟高风险词{i}" for i in range(500)
]

review_keywords = ["低风险"] + [
    f"模拟低风险词{i}" for i in range(500)
]

# =========================
# 2. 优化前：逐个关键词扫描
# =========================

def classify_naive(content):
    if not isinstance(content, str):
        raise TypeError("content 必须是字符串")

    if not content:
        raise ValueError("content 不能为空")

    if len(content) > 500:
        raise ValueError("content 不能超过 500 字符")

    # 高风险优先
    for keyword in high_risk_keywords:
        if keyword in content:
            return {"status": "block", "risk_level": "high"}

    # 再检查低风险
    for keyword in review_keywords:
        if keyword in content:
            return {"status": "review", "risk_level": "medium"}

    return {"status": "pass", "risk_level": "low"}


# =========================
# 3. 优化后：正则表达式统一扫描
# =========================

all_keywords = high_risk_keywords + review_keywords

# 编译一次，后续重复使用
keyword_pattern = re.compile(
    "|".join(re.escape(keyword) for keyword in all_keywords)
)

high_risk_set = set(high_risk_keywords)


def classify_regex(content):
    if not isinstance(content, str):
        raise TypeError("content 必须是字符串")

    if not content:
        raise ValueError("content 不能为空")

    if len(content) > 500:
        raise ValueError("content 不能超过 500 字符")

    matched_keywords = {
        match.group()
        for match in keyword_pattern.finditer(content)
    }

    # 不能依赖关键词在文本中出现的先后顺序
    if matched_keywords & high_risk_set:
        return {"status": "block", "risk_level": "high"}

    if matched_keywords:
        return {"status": "review", "risk_level": "medium"}

    return {"status": "pass", "risk_level": "low"}


# =========================
# 4. 准备模拟测试数据
# =========================

test_contents = [
    "这是一条普通内容",
    "这条内容包含低风险信息",
    "这条内容包含严重违规信息",
    "这条内容涉及诈骗",
    "低风险内容中同时包含严重违规信息",
    "严重违规信息出现在前面，低风险信息出现在后面",
    "这是一段比较长的普通内容。" * 30,
    "这条内容包含模拟高风险词20",
    "这条内容包含模拟低风险词10",
]


# =========================
# 5. 先验证两个算法结果一致
# =========================

print("===== 正确性验证 =====")

for content in test_contents:
    result_naive = classify_naive(content)
    result_regex = classify_regex(content)

    assert result_naive == result_regex, (
        f"结果不一致：{content}"
    )

    print(content[:30], result_naive)

print("正确性验证通过！")


# =========================
# 6. 性能测试
# =========================


def benchmark(func, contents, rounds=10000):
    start = time.perf_counter()

    for _ in range(rounds):
        for content in contents:
            func(content)

    return time.perf_counter() - start


print("\n===== 重复性能测试 =====")

# 先预热，减少首次运行带来的影响
benchmark(classify_naive, test_contents, rounds=1000)
benchmark(classify_regex, test_contents, rounds=1000)

naive_results = []
regex_results = []

for i in range(10):
    naive_results.append(
        benchmark(classify_naive, test_contents)
    )
    regex_results.append(
        benchmark(classify_regex, test_contents)
    )

naive_avg = sum(naive_results) / len(naive_results)
regex_avg = sum(regex_results) / len(regex_results)

print("逐个扫描每轮耗时：", naive_results)
print("正则扫描每轮耗时：", regex_results)

print(f"\n逐个扫描平均耗时：{naive_avg:.6f} 秒")
print(f"正则扫描平均耗时：{regex_avg:.6f} 秒")
print(f"平均加速比：{naive_avg / regex_avg:.2f} 倍")
