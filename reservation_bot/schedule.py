from datetime import date, timedelta


THURSDAY = 3
FRIDAY = 4


class ScheduleError(RuntimeError):
    """Raised when the bot is started on an invalid day."""


def get_target_booking_date(
    today: date | None = None,
) -> date:
    """
    Thursday -> Saturday
    Friday   -> Sunday
    """

    current_date = today or date.today()

    weekday = current_date.weekday()

    if weekday == THURSDAY:
        return current_date + timedelta(days=2)

    if weekday == FRIDAY:
        return current_date + timedelta(days=2)

    raise ScheduleError(
        "Live reservation is allowed only "
        "on Thursday or Friday."
    )