"""Elementary probability and Wilson intervals for an illustrative evaluation."""
import math


def binomial_pmf(n: int, k: int, p: float) -> float:
    if not isinstance(n, int) or not isinstance(k, int) or n < 0 or not 0 <= k <= n or not 0 <= p <= 1:
        raise ValueError("require integer 0 <= k <= n and probability in [0, 1]")
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> tuple:
    if (not isinstance(trials, int) or not isinstance(successes, int) or trials <= 0
            or not 0 <= successes <= trials or not math.isfinite(z) or z <= 0):
        raise ValueError("require 0 <= successes <= trials, trials > 0, finite z > 0")
    p = successes / trials
    z2 = z * z
    denominator = 1 + z2 / trials
    centre = (p + z2 / (2 * trials)) / denominator
    margin = z * math.sqrt(p * (1 - p) / trials + z2 / (4 * trials * trials)) / denominator
    return max(0.0, centre - margin), min(1.0, centre + margin)


if __name__ == "__main__":
    print(f"真实失败率假设为 5%，20 次独立尝试零失败的概率: {binomial_pmf(20, 0, .05):.3f}")
    low, high = wilson_interval(5, 100)
    print(f"100 次中失败 5 次，失败率的 Wilson 95% 区间: [{low:.3f}, {high:.3f}]")
