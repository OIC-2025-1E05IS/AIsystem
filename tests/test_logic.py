import unittest

from keiba_money.logic import calculate_profit, calculate_recovery_rate, validate_race_record


class ProfitTests(unittest.TestCase):
    def test_profit(self):
        self.assertEqual(calculate_profit(1000, 2500), 1500)

    def test_loss(self):
        self.assertEqual(calculate_profit(1000, 0), -1000)

    def test_zero_amounts(self):
        self.assertEqual(calculate_profit(0, 0), 0)

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValueError):
            calculate_profit(-1, 100)

    def test_non_integer_rejected(self):
        with self.assertRaises(ValueError):
            calculate_profit(100.5, 200)

    def test_bool_rejected(self):
        with self.assertRaises(ValueError):
            calculate_profit(True, 200)

    def test_payout_without_purchase_rejected(self):
        with self.assertRaises(ValueError):
            calculate_profit(0, 100)

    def test_recovery_rate(self):
        self.assertAlmostEqual(calculate_recovery_rate(2000, 1500), 75.0)

    def test_recovery_rate_zero_division_boundary(self):
        self.assertEqual(calculate_recovery_rate(0, 0), 0.0)

    def test_blank_race_name_rejected(self):
        with self.assertRaises(ValueError):
            validate_race_record("  ", "2026-11-02", 100, 0)

    def test_invalid_date_rejected(self):
        with self.assertRaises(ValueError):
            validate_race_record("天皇賞", "2026/11/02", 100, 0)

    def test_valid_record(self):
        validate_race_record("天皇賞", "2026-11-02", 100, 250)


if __name__ == "__main__":
    unittest.main()
