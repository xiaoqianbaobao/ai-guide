import unittest
from metrics import binomial_pmf, wilson_interval


class MetricsTests(unittest.TestCase):
    def test_binomial_probabilities_sum_to_one(self):
        self.assertAlmostEqual(sum(binomial_pmf(20, k, .05) for k in range(21)), 1)

    def test_zero_observed_failures_does_not_yield_zero_upper_bound(self):
        low, high = wilson_interval(0, 20)
        self.assertAlmostEqual(low, 0)
        self.assertGreater(high, .15)

    def test_interval_contains_observed_rate(self):
        low, high = wilson_interval(5, 100)
        self.assertLess(low, .05)
        self.assertGreater(high, .05)

    def test_invalid_counts_are_rejected(self):
        with self.assertRaises(ValueError):
            wilson_interval(6, 5)
        with self.assertRaises(ValueError):
            binomial_pmf(5, 6, .5)


if __name__ == "__main__":
    unittest.main()
