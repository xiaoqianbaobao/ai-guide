import unittest
from linear_fit import fit, loss_and_gradient


class GradientTests(unittest.TestCase):
    def test_analytic_gradient_matches_finite_difference(self):
        xs, ys, w, b, epsilon = [0, 1, 2], [1, 3, 5], .3, -.2, 1e-6
        _, dw, db = loss_and_gradient(xs, ys, w, b)
        numeric_w = (loss_and_gradient(xs, ys, w + epsilon, b)[0] - loss_and_gradient(xs, ys, w - epsilon, b)[0]) / (2 * epsilon)
        numeric_b = (loss_and_gradient(xs, ys, w, b + epsilon)[0] - loss_and_gradient(xs, ys, w, b - epsilon)[0]) / (2 * epsilon)
        self.assertAlmostEqual(dw, numeric_w, places=6)
        self.assertAlmostEqual(db, numeric_b, places=6)

    def test_training_reduces_loss_on_teaching_data(self):
        result = fit([0, 1, 2, 3], [1, 3, 5, 7])
        self.assertLess(result["final_loss"], result["initial_loss"])
        self.assertAlmostEqual(result["w"], 2, places=3)
        self.assertAlmostEqual(result["b"], 1, places=3)

    def test_invalid_data_is_rejected(self):
        with self.assertRaises(ValueError):
            loss_and_gradient([1], [], 0, 0)
        with self.assertRaises(ValueError):
            fit([1], [2], learning_rate=0)


if __name__ == "__main__":
    unittest.main()
