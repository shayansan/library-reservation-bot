from datetime import date, timedelta


WEDNESDAY = 2
THURSDAY = 3


class ScheduleError(RuntimeError):
    """Raised when the bot is started on an invalid day."""


def get_target_booking_date(
    today: date | None = None,
) -> date:
    """
    Wednesday -> Saturday
    Thursday  -> Sunday
    """

    current_date = today or date.today()

    weekday = current_date.weekday()

    if weekday == WEDNESDAY:
        return current_date + timedelta(days=3)

    if weekday == THURSDAY:
        return current_date + timedelta(days=3)

    raise ScheduleError(
        "Live reservation is allowed only "
        "on Wednesday or Thursday."
    )