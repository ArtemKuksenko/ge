from datetime import datetime


def get_day_from_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")
