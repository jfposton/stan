import unittest
import datetime
from generate_post import select_week

class GeneratePost(unittest.TestCase):
    def test_select_week(self):
        date = datetime.datetime(2025, 8, 20)
        self.assertEqual(select_week(date)["week"], "01")
        date = datetime.datetime(2025, 9, 5)
        self.assertEqual(select_week(date)["week"], "02")
        date = datetime.datetime(2025, 9, 10)
        self.assertEqual(select_week(date)["week"], "03")

        date = datetime.datetime(2025, 9, 16)
        self.assertEqual(select_week(date)["week"], "04")

        date = datetime.datetime(2025, 9, 23)
        self.assertEqual(select_week(date)["week"], "05")
        date = datetime.datetime(2025, 9, 30)
        self.assertEqual(select_week(date)["week"], "06")

if __name__ == '__main__':
    unittest.main()