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


def append_zero_to_single_digit_days_in_date(input_days_string: str):
    """
    @param input_days_string:
    @return:
    """
    if input_days_string and 0 < int(input_days_string) < 10:
        return f"0{input_days_string}"
    else:
        return input_days_string


def transform_date_to_database_date_format(dirty_date_input: str):
    """
    Returns correct date format for database entry from scraped date example = 13 maart 2022
    @param dirty_date_input: string
    @return: New date format example: 2022-05-13
    """
    splitted_dirty_date = dirty_date_input.split(' ')
    clean_year = splitted_dirty_date[2]
    clean_date = [clean_year]
    month_clean = transform_month_in_digit_string(splitted_dirty_date[1])
    clean_date.append(month_clean)
    days_clean = append_zero_to_single_digit_days_in_date(splitted_dirty_date[0])
    clean_date.append(days_clean)
    return f"{clean_date[0]}-{clean_date[1]}-{clean_date[2]}"


if __name__ == '__main__':
    print(transform_date_to_database_date_format("15 mei 2022"))
