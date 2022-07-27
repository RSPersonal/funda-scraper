import unittest
import re
from .funda_helpers import transform_month_in_digit_string, transform_date_to_database_date_format


class TestGetMonthInDigit(unittest.TestCase):
    def test_transform_months_do_digit(self):
        self.assertEqual(transform_month_in_digit_string("januari"), "01")
        self.assertEqual(transform_month_in_digit_string("februari"), "02")
        self.assertEqual(transform_month_in_digit_string("maart"), "03")
        self.assertEqual(transform_month_in_digit_string("april"), "04")
        self.assertEqual(transform_month_in_digit_string("mei"), "05")
        self.assertEqual(transform_month_in_digit_string("juni"), "06")
        self.assertEqual(transform_month_in_digit_string("juli"), "07")
        self.assertEqual(transform_month_in_digit_string("augustus"), "08")
        self.assertEqual(transform_month_in_digit_string("september"), "09")
        self.assertEqual(transform_month_in_digit_string("oktober"), "10")
        self.assertEqual(transform_month_in_digit_string("november"), "11")
        self.assertEqual(transform_month_in_digit_string("december"), "12")

    def test_construct_clean_date_format(self):
        self.assertEqual(transform_date_to_database_date_format("15 maart 2022"), "2022-03-15")
        self.assertEqual(transform_date_to_database_date_format("5 mei 2022"), "2022-05-05")

    def test_extract_street_from_object(self):
        case_with_dot = 'Verkocht: P.C. Boutensstraat 14 1321 VX Almere'
        case_with_dot_address = re.findall(r'Verkocht: (.*) \d{4}', case_with_dot)[0].replace(' ', '')
        case_with_dot_street = re.search('[a-zA-Z-.]+', case_with_dot_address).group(0)
        self.assertEqual(case_with_dot_street, 'P.C.Boutensstraat')

        case_with_dash = 'Verkocht: Jan-Boutensstraat 14 1321 VX Almere'
        case_with_dash_address = re.findall(r'Verkocht: (.*) \d{4}', case_with_dash)[0].replace(' ', '')
        case_with_dash_street = re.search('[a-zA-Z-.]+', case_with_dash_address).group(0)
        self.assertEqual(case_with_dash_street, 'Jan-Boutensstraat')


if __name__ == '__main__':
    unittest.main()
