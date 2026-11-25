import unittest
from economics import Scenario, calculate


class EconomicsTests(unittest.TestCase):
    def scenario(self, **changes):
        values = dict(monthly_tasks=1000, adoption=.5, minutes_before=8, minutes_after=5,
                      hourly_cost=60, cash_realization=.25, cost_per_adopted_task=.1,
                      monthly_fixed_cost=800)
        values.update(changes)
        return Scenario(**values)

    def test_example_separates_time_value_from_cash_impact(self):
        result = calculate(self.scenario())
        self.assertEqual(result["hours_saved"], 25)
        self.assertEqual(result["time_value"], 1500)
        self.assertEqual(result["estimated_cash_impact"], -475)

    def test_no_adoption_still_incurs_fixed_cost(self):
        self.assertEqual(calculate(self.scenario(adoption=0))["estimated_cash_impact"], -800)

    def test_slower_workflow_can_have_negative_time_savings(self):
        self.assertLess(calculate(self.scenario(minutes_after=10))["hours_saved"], 0)

    def test_invalid_adoption_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate(self.scenario(adoption=1.1))


if __name__ == "__main__":
    unittest.main()
