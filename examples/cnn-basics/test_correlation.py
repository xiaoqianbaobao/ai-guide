import unittest
from correlation import correlate, relu


class CorrelationTests(unittest.TestCase):
    def test_hand_calculated_example(self):
        image = [[1, 2, 0], [0, 1, 2], [2, 2, 1]]
        feature = correlate(image, [[1, 0], [-1, 0]])
        self.assertEqual(feature, [[1, 1], [-2, -1]])
        self.assertEqual(relu(feature), [[1, 1], [0, 0]])

    def test_padding_and_stride_shape(self):
        result = correlate([[1, 2], [3, 4]], [[1, 0], [0, 1]], stride=2, padding=1)
        self.assertEqual(result, [[1, 0], [0, 4]])

    def test_invalid_shapes_and_stride(self):
        with self.assertRaises(ValueError):
            correlate([[1], [1, 2]], [[1]])
        with self.assertRaises(ValueError):
            correlate([[1]], [[1]], stride=0)
        with self.assertRaises(ValueError):
            correlate([[1]], [[1, 2]])


if __name__ == "__main__":
    unittest.main()
