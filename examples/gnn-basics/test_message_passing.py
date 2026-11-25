import unittest
from message_passing import aggregate


class AggregationTests(unittest.TestCase):
    def test_small_graph_and_self_loop(self):
        features = {"A": [1, 0], "B": [0, 1], "C": [1, 1]}
        result = aggregate(features, {"A": ["B"], "B": ["A", "C"], "C": ["B"]})
        self.assertEqual(result["A"], [.5, .5])
        self.assertAlmostEqual(result["B"][0], 2 / 3)
        self.assertEqual(result["C"], [.5, 1])

    def test_isolated_node_keeps_its_features(self):
        self.assertEqual(aggregate({"A": [3, 4]}, {})["A"], [3, 4])

    def test_invalid_neighbors_and_dimensions(self):
        with self.assertRaises(ValueError):
            aggregate({"A": [1]}, {"A": ["missing"]})
        with self.assertRaises(ValueError):
            aggregate({"A": [1], "B": [1, 2]}, {})
        with self.assertRaises(ValueError):
            aggregate({"A": [1], "B": [2]}, {"A": ["B", "B"]})


if __name__ == "__main__":
    unittest.main()
