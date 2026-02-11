"""Datetime for SHOWROOM specification."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone


class ShowroomDatetime:
    """Datetime for SHOWROOM specification."""

    FORMAT_CODE = "%Y_%m_%d-%H_%M_%S"

    @staticmethod
    def encode(argument_datetime: datetime) -> str:
        return argument_datetime.strftime(ShowroomDatetime.FORMAT_CODE)

    @staticmethod
    def now_jst() -> datetime:
        return datetime.now(tz=timezone(timedelta(hours=+9), "JST"))
