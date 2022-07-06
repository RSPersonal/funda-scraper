import re

MONTHS = {
    "januari": "01",
    "februari": "02",
    "maart": "03",
    "april": "04",
    "mei": "05",
    "juni": "06",
    "juli": "07",
    "augustus": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "december": "12",
}


def transform_month_in_digit_string(input_user_string: str):
    """
    @param input_user_string: string
    @return: months in digit string or None
    """
    if input_user_string and MONTHS[input_user_string]:
        return MONTHS[input_user_string]
    else:
        return False


def append_zero_to_single_digit_days_in_date(input_month_string: str):
    """
    @param input_month_string:
    @return:
    """
    if input_month_string and 0 < int(input_month_string) < 10:
        return f"0{input_month_string}"
    else:
        return input_month_string


def transform_date_to_database_date_format(dirty_date_input: str):
    """
    Returns correct date format for database entry from scraped date example = 13 maart 2022
    @param dirty_date_input: string
    @return: New date format example: 2022-05-13
    """
    find_dirty_year_sold = re.search(r'[a-z]+', dirty_date_input).group(0)
    find_dirty_month = re.search(r'\d+', dirty_date_input).group(0)
    dirty_date_input = dirty_date_input.replace(find_dirty_year_sold, transform_month_in_digit_string(find_dirty_year_sold))
    year_month_clean = dirty_date_input.replace(find_dirty_month, append_zero_to_single_digit_days_in_date(find_dirty_month))
    splitted_clean_date = year_month_clean.split(' ')
    return f"{splitted_clean_date[2]}-{splitted_clean_date[1]}-{splitted_clean_date[0]}"
