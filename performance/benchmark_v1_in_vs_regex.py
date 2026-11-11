
import re
import time
import statistics


# ==================================================
# 1. 原始 V1：使用 in 进行字符串匹配
# ==================================================

def baseline_in(content: str) -> dict:
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


# ==================================================
# 2. 正则 V1：预编译正则表达式
# ==================================================

HIGH_RISK_PATTERN = re.compile(re.escape("严重违规"))
REVIEW_PATTERN = re.compile(re.escape("低风险"))


def regex_classify(content: str) -> dict:
    if not isinstance(content, str):
        raise TypeError("内容必须是字符串")

    if len(content) == 0:
        raise ValueError("内容不能为空")

    if len(content) > 500:
        raise ValueError("内容长度不能超过500个字符")

    if HIGH_RISK_PATTERN.search(content):
        return {"decision": "block", "risk_level": "high"}

    if REVIEW_PATTERN.search(content):
        return {"decision": "review", "risk_level": "medium"}

    return {"decision": "pass", "risk_level": "low"}


# ==================================================
# 3. 准备相同的测试数据
# ==================================================

test_cases = [
    "今天天气很好，适合出去散步。",
    "这是一条普通的商品介绍信息。",
    "这条内容包含低风险关键词。",
    "这条内容包含严重违规关键词。",
    "这条内容同时包含低风险和严重违规关键词。",
    "普通文本" * 50,
    "普通文本" * 45 + "低风险",
    "普通文本" * 45 + "严重违规",
]


# ==================================================
# 4. 正确性验证
# ==================================================

def check_correctness():
    for content in test_cases:
        result_in = baseline_in(content)
        result_regex = regex_classify(content)

        assert result_in == result_regex, (
            f"结果不一致！\n"
            f"输入：{content}\n"
            f"in方案：{result_in}\n"
            f"正则方案：{result_regex}"
        )

    print("正确性验证通过：所有测试数据的结果一致。")


# ==================================================
# 5. 单轮性能测量
# ==================================================

def measure(func, loops):
    start = time.perf_counter()

    for _ in range(loops):
        for content in test_cases:
            func(content)

    elapsed = time.perf_counter() - start

    total_calls = loops * len(test_cases)
    average_us = elapsed / total_calls * 1_000_000

    return elapsed, average_us


# ==================================================
# 6. 多轮公平对比
# ==================================================

def run_benchmark():
    loops = 20_000
    rounds = 7

    # 预热：让两个方案都先运行一遍
    measure(baseline_in, 1_000)
    measure(regex_classify, 1_000)

    in_times = []
    regex_times = []

    for round_number in range(rounds):

        # 轮换执行顺序，降低顺序偏差
        if round_number % 2 == 0:
            in_result = measure(baseline_in, loops)
            regex_result = measure(regex_classify, loops)
        else:
            regex_result = measure(regex_classify, loops)
            in_result = measure(baseline_in, loops)

        in_times.append(in_result[1])
        regex_times.append(regex_result[1])

        print(
            f"第 {round_number + 1} 轮："
            f"in={in_result[1]:.4f} μs/次，"
            f"regex={regex_result[1]:.4f} μs/次"
        )

    in_median = statistics.median(in_times)
    regex_median = statistics.median(regex_times)

    print("\n========== 最终结果 ==========")
    print(f"每轮调用次数：{loops * len(test_cases):,}")
    print(f"测量轮数：{rounds}")
    print(f"in 中位数：{in_median:.4f} μs/次")
    print(f"regex 中位数：{regex_median:.4f} μs/次")

    if regex_median < in_median:
        ratio = in_median / regex_median
        print(f"正则方案约快 {ratio:.2f} 倍")
    elif in_median < regex_median:
        ratio = regex_median / in_median
        print(f"in 方案约快 {ratio:.2f} 倍")
    else:
        print("两个方案的中位数相同")


if __name__ == "__main__":
    check_correctness()
    run_benchmark()
