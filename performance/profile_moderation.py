import cProfile
import pstats

from app.moderation import classify_content


def run_test():
    for _ in range(100000):
        classify_content("这是一条普通内容")


if __name__ == "__main__":
    profiler = cProfile.Profile()

    profiler.enable()
    run_test()
    profiler.disable()

    stats = pstats.Stats(profiler)

    stats.strip_dirs()
    stats.sort_stats("cumtime")
    stats.print_stats(20)