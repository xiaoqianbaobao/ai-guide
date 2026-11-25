import unittest
from basics import cosine, dot, matvec


class LinearAlgebraTests(unittest.TestCase):
    def test_magnitude_changes_dot_but_not_cosine(self):
        self.assertEqual(dot([1, 0], [1, 1]), 1)
        self.assertEqual(dot([1, 0], [10, 10]), 10)
        self.assertAlmostEqual(cosine([1, 0], [1, 1]), cosine([1, 0], [10, 10]))

    def test_matrix_vector_shape_and_values(self):
        self.assertEqual(matvec([[1, 2], [3, 4]], [2, 1]), [4, 10])

    def test_bad_dimensions_and_zero_norm_are_explicit(self):
        with self.assertRaises(ValueError):
            dot([1], [1, 2])
        with self.assertRaises(ValueError):
            cosine([0, 0], [1, 1])


if __name__ == "__main__":
    unittest.main()
