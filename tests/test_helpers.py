import unittest
from datetime import time, date
from app.utils.helpers import apply_winter_shift

class TestApplyWinterShift(unittest.TestCase):

    def test_winter_months(self):
        # Test in winter months (October)
        base_time = time(8, 0)
        test_date = date(2025, 10, 15)
        shift_minutes = 30
        expected_time = time(8, 30)
        self.assertEqual(apply_winter_shift(base_time, test_date, shift_minutes), expected_time)

        # Test in winter months (March)
        test_date = date(2025, 3, 15)
        expected_time = time(8, 30)
        self.assertEqual(apply_winter_shift(base_time, test_date, shift_minutes), expected_time)

    def test_non_winter_months(self):
        # Test in non-winter months (May)
        base_time = time(8, 0)
        test_date = date(2025, 5, 15)
        shift_minutes = 30
        expected_time = time(8, 0)
        self.assertEqual(apply_winter_shift(base_time, test_date, shift_minutes), expected_time)

        # Test in non-winter months (September)
        test_date = date(2025, 9, 15)
        self.assertEqual(apply_winter_shift(base_time, test_date, shift_minutes), expected_time)

if __name__ == "__main__":
    unittest.main()