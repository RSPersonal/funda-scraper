MONTHS = {
    "januari": "01",
    "februari": "02",
    "maart": "03",
    "april": "04",
    "mei": "05",
    "Juni": "06",
    "juli": "07",
    "augustus": "08",
    "september": "09",
    "oktober": "10",
    "november": "11",
    "december": "12",
}


def get_month_in_digit_string(input_user_string: str):
    """
    @param input_user_string: string
    @return: months in digit string or None
    """
    if input_user_string and MONTHS[input_user_string]:
        return MONTHS[input_user_string]
    else:
        return False
