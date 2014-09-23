import unittest
from datetime import date

from django.utils.six.moves import xrange

from console.utils import all_days_of, excluded_days, daterange


class TestUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        start = date(2014, 1, 1)
        end = date(2014, 1, 31)
        cls.all_days_of_january = list(daterange(start, end))
        end = date(2014, 1, 30)
        cls.some_days_of_january = list(daterange(start, end))
        cls.missing_days_of_january = [date(2014, 1, 31)]
        cls.today = date.today()

    def test_daterange_generate_right_values(self):
        self.assertEqual(len(self.all_days_of_january), 31)
        self.assertEqual(len(self.some_days_of_january), 30)
        for i in xrange(1, 32):
            day = date(2014, 1, i)
            self.assertIn(day, self.all_days_of_january)

    def test_excluded_days_returns_missing_day(self):
        results = excluded_days(self.all_days_of_january, self.some_days_of_january)
        self.assertEqual(results, self.missing_days_of_january)

    def test_excluded_days_returns_empty_list(self):
        results = excluded_days(self.all_days_of_january, self.all_days_of_january)
        self.assertEqual(results, [])

    def test_excluded_days_returns_multiple_missing_days(self):
        sixth_january = self.some_days_of_january.pop(5)
        self.missing_days_of_january.append(sixth_january)
        results = excluded_days(self.all_days_of_january, self.some_days_of_january)
        self.assertEqual(sorted(results), sorted(self.missing_days_of_january))
        self.missing_days_of_january.remove(sixth_january)
        self.some_days_of_january.append(sixth_january)

    def test_all_days_of_returns_all_days_of_an_year(self):
        results = all_days_of(2010, month=None, day=None)
        self.assertEqual(len(results), 365)
        self.assertEqual(results[0], date(2010, 1, 1))
        self.assertEqual(results[-1], date(2010, 12, 31))

    def test_all_days_of_returns_all_days_of_a_month(self):
        results = all_days_of(2014, month=1, day=None)
        self.assertEqual(len(results), 31)
        self.assertEqual(results, self.all_days_of_january)

    def test_all_days_of_year_returns_one_day(self):
        results = all_days_of(2014, month=1, day=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.all_days_of_january[0])

    def test_all_days_handles_current_month(self):
        results = all_days_of(date.today().year, self.today.month)
        first_of_month = date(self.today.year, self.today.month, 1)
        all_days_of_the_month_untill_today = list(daterange(first_of_month, self.today))
        self.assertEqual(results, all_days_of_the_month_untill_today)

    def test_all_days_handles_current_year(self):
        results = all_days_of(date.today().year)
        first_of_year = date(self.today.year, 1, 1)
        all_days_of_the_year_untill_today = list(daterange(first_of_year, self.today))
        self.assertEqual(results, all_days_of_the_year_untill_today)
