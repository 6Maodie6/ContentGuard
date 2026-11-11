
import re
import time
from statistics import mean

from performance.aho_corasick import AhoCorasick


# ==================================================
# 1. 关键词：总数仍然是 1003 个
# ==================================================

# 4 个基础高风险词 + 498 个模拟词 = 502 个
high_risk_keywords = [
    "严重违规",
    "诈骗",
    "诈骗信息",
    "诈骗信息平台",
] + [f"模拟高风险词{i}" for i in range(498)]

# 1 个基础低风险词 + 500 个模拟词 = 501 个
review_keywords = ["低风险"] + [
    f"模拟低风险词{i}" for i in range(500)
]

all_keywords = high_risk_keywords + review_keywords

high_risk_set = set(high_risk_keywords)
review_set = set(review_keywords)

print("高风险关键词数量：", len(high_risk_keywords))
print("低风险关键词数量：", len(review_keywords))
print("关键词总数：", len(all_keywords))


# ==================================================
# 2. 公共校验和分类结果
# ==================================================

def validate_content(content):
    if not isinstance(content, str):
        raise TypeError("content 必须是字符串")

    if not content:
        raise ValueError("content 不能为空")

    if len(content) > 500:
        raise ValueError("content 长度不能超过 500")


def build_result(has_high_risk, has_review):
    if has_high_risk:
        return {"status": "block", "risk_level": "high"}

    if has_review:
        return {"status": "review", "risk_level": "medium"}

    return {"status": "pass", "risk_level": "low"}


# ==================================================
# 3. 方案一：逐个扫描
# ==================================================

def classify_naive(content):
    validate_content(content)

    has_high_risk = any(
        keyword in content
        for keyword in high_risk_keywords
    )

    has_review = any(
        keyword in content
        for keyword in review_keywords
    )

    return build_result(has_high_risk, has_review)


# ==================================================
# 4. 方案二：正则扫描
# ==================================================

# 两类规则分别编译。
# search() 只判断是否存在匹配，不负责枚举所有匹配词。
high_pattern = re.compile(
    "|".join(re.escape(k) for k in high_risk_keywords)
)

review_pattern = re.compile(
    "|".join(re.escape(k) for k in review_keywords)
)


def classify_regex(content):
    validate_content(content)

    has_high_risk = high_pattern.search(content) is not None
    has_review = review_pattern.search(content) is not None

    return build_result(has_high_risk, has_review)


# ==================================================
# 5. 方案三：AC 自动机
# ==================================================

ac = AhoCorasick(all_keywords)


def classify_ac(content):
    validate_content(content)

    matches = ac.search(content)
    matched_keywords = {
        item["keyword"] for item in matches
    }

    has_high_risk = bool(matched_keywords & high_risk_set)
    has_review = bool(matched_keywords & review_set)

    return build_result(has_high_risk, has_review)


algorithms = {
    "逐个扫描": classify_naive,
    "正则扫描": classify_regex,
    "AC自动机": classify_ac,
}


# ==================================================
# 6. 构造不超过 500 字符的测试文本
# ==================================================

def make_500_chars(suffix):
    """构造一条长度恰好为 500 的文本，并以 suffix 结尾。"""
    prefix_length = 500 - len(suffix)
    return ("普" * prefix_length) + suffix


long_no_hit = "普" * 500
long_single_hit = make_500_chars("诈骗")

test_cases = {
    "短文本无命中": "这是一条普通内容",
    "长文本无命中": long_no_hit,
    "短文本单命中": "这条内容包含严重违规信息",
    "长文本末尾单命中": long_single_hit,
    "多个高风险词": "诈骗，严重违规，诈骗信息",
    "多个低风险词": "低风险，模拟低风险词20，模拟低风险词100",
    "高低风险混合": "低风险内容，同时包含严重违规信息",
    "重叠关键词": "这条内容涉及诈骗信息平台",
    "重复关键词": "诈骗，诈骗，诈骗信息平台",
}

test_contents = list(test_cases.values())


# ==================================================
# 7. 正确性验证：逐个场景比较三种算法
# ==================================================

print("\n===== 场景正确性验证 =====")

for case_name, content in test_cases.items():
    results = {
        name: func(content)
        for name, func in algorithms.items()
    }

    assert results["逐个扫描"] == results["正则扫描"], case_name
    assert results["逐个扫描"] == results["AC自动机"], case_name

    print(case_name, "长度 =", len(content))
    print("  分类结果：", results["逐个扫描"])


# 验证异常输入
print("\n===== 异常输入验证 =====")

invalid_inputs = [123, None, "", "普" * 501]

for invalid in invalid_inputs:
    error_types = []

    for name, func in algorithms.items():
        try:
            func(invalid)
        except (TypeError, ValueError) as error:
            error_types.append(type(error))
        else:
            raise AssertionError(
                f"{name} 未拒绝非法输入：{invalid!r}"
            )

    assert error_types[0] == error_types[1] == error_types[2]

print("异常输入验证通过！")
print("所有场景的分类结果一致！")


# ==================================================
# 8. 单独测量构建耗时
# ==================================================

print("\n===== 构建耗时 =====")

start = time.perf_counter()
re.compile(
    "|".join(re.escape(k) for k in high_risk_keywords)
)
re.compile(
    "|".join(re.escape(k) for k in review_keywords)
)
regex_build_time = time.perf_counter() - start

start = time.perf_counter()
AhoCorasick(all_keywords)
ac_build_time = time.perf_counter() - start

print(f"正则表达式编译：{regex_build_time:.6f} 秒")
print(f"AC 自动机构建：{ac_build_time:.6f} 秒")
print("逐个扫描：无需额外构建索引")


# ==================================================
# 9. 性能测试函数
# ==================================================

def benchmark(func, contents, rounds=1000):
    start = time.perf_counter()

    for _ in range(rounds):
        for content in contents:
            func(content)

    return time.perf_counter() - start


# 先预热，每种算法处理相同的数据
print("\n===== 预热 =====")

for func in algorithms.values():
    benchmark(func, test_contents, rounds=200)

print("预热完成！")


# ==================================================
# 10. 交替顺序进行 10 轮测试
# ==================================================

results = {
    name: [] for name in algorithms
}

names = list(algorithms.keys())

print("\n===== 正式性能测试 =====")

for round_index in range(10):
    shift = round_index % len(names)
    order = names[shift:] + names[:shift]

    for name in order:
        elapsed = benchmark(
            algorithms[name],
            test_contents,
            rounds=1000
        )
        results[name].append(elapsed)

    print(f"第 {round_index + 1} 轮完成：{order}")


# ==================================================
# 11. 汇总结果
# ==================================================

averages = {
    name: mean(times)
    for name, times in results.items()
}

print("\n===== 十轮测试结果 =====")

for name, times in results.items():
    print(f"\n{name}：")
    print([round(value, 6) for value in times])
    print(f"平均耗时：{averages[name]:.6f} 秒")

naive_avg = averages["逐个扫描"]

print("\n===== 相对逐个扫描的加速比 =====")

for name in ["正则扫描", "AC自动机"]:
    print(
        f"{name}：{naive_avg / averages[name]:.2f} 倍"
    )

print("\n===== 实验完成 =====")
