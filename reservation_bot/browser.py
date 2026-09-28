from datetime import date

from playwright.sync_api import Page

from reservation_bot.models import (
    ReservationPeriod,
    Slot,
)
from reservation_bot.selectors import (
    AVAILABLE_SLOT,
    FORM,
    SLOTS_CONTAINER,
)


class ReservationPageError(RuntimeError):
    """Raised when the reservation page cannot be used safely."""


def open_reservation_page(
    page: Page,
    reservation_url: str,
    *,
    timeout_ms: int = 45_000,
) -> None:
    page.goto(
        reservation_url,
        wait_until="domcontentloaded",
        timeout=timeout_ms,
    )

    page.locator(FORM).wait_for(
        state="visible",
        timeout=timeout_ms,
    )

    page.locator(SLOTS_CONTAINER).wait_for(
        state="visible",
        timeout=timeout_ms,
    )


def get_available_slots(
    page: Page,
) -> list[Slot]:

    locator = page.locator(
        AVAILABLE_SLOT
    )

    slots: list[Slot] = []

    for index in range(locator.count()):
        element = locator.nth(index)

        slot_date = element.get_attribute("d")

        h1 = element.get_attribute("h1")
        m1 = element.get_attribute("m1")
        h2 = element.get_attribute("h2")
        m2 = element.get_attribute("m2")

        attributes = {
            "date": slot_date,
            "h1": h1,
            "m1": m1,
            "h2": h2,
            "m2": m2,
        }

        missing = [
            name
            for name, value in attributes.items()
            if value is None
        ]

        if missing:
            raise ReservationPageError(
                "Available slot is missing required "
                f"attributes: {', '.join(missing)}"
            )

        slots.append(
            Slot(
                date=slot_date,
                start_hour=int(h1),
                start_minute=int(m1),
                end_hour=int(h2),
                end_minute=int(m2),
            )
        )

    return slots


def get_calendar_date_selector(
    target_date: date,
) -> str:
    """
    Build a selector for exactly one calendar date.

    jQuery UI uses zero-based months:
    January = 0, ..., December = 11.
    """

    year = target_date.year
    month = target_date.month - 1
    day = target_date.day

    return (
        ".ui-datepicker-calendar "
        f'td[data-year="{year}"]'
        f'[data-month="{month}"] '
        f'a[data-date="{day}"]'
    )


def select_calendar_date(
    page: Page,
    target_date: date,
) -> None:
    """
    Select exactly the requested calendar date.

    If the requested date is not currently offered by the site,
    fail safely instead of selecting another date.
    """

    selector = get_calendar_date_selector(
        target_date
    )

    calendar_date = page.locator(
        selector
    )

    count = calendar_date.count()

    if count == 0:
        raise ReservationPageError(
            "Target booking date is not available "
            "in the calendar: "
            f"{target_date.isoformat()}"
        )

    if count > 1:
        raise ReservationPageError(
            "Expected exactly one calendar entry "
            f"for {target_date.isoformat()}, "
            f"found {count}."
        )

    calendar_date.click()

    expected_date = target_date.isoformat()

    page.locator(
        ".slotsCalendarfieldname1_1 "
        f'a[d="{expected_date}"]'
    ).first.wait_for(
        state="attached",
        timeout=10_000,
    )


def get_period_selector(
    period: ReservationPeriod,
    target_date: date,
) -> str:

    date_value = target_date.isoformat()

    if period is ReservationPeriod.MORNING:
        return (
            ".slotsCalendarfieldname1_1 "
            '.availableslot > a'
            f'[d="{date_value}"]'
            '[h1="8"]'
            '[m1="30"]'
            '[h2="14"]'
            '[m2="0"]'
        )

    if period is ReservationPeriod.AFTERNOON:
        return (
            ".slotsCalendarfieldname1_1 "
            '.availableslot > a'
            f'[d="{date_value}"]'
            '[h1="14"]'
            '[m1="0"]'
            '[h2="23"]'
            '[m2="55"]'
        )

    raise ValueError(
        f"Unsupported reservation period: {period}"
    )


def is_period_available(
    page: Page,
    period: ReservationPeriod,
    target_date: date,
) -> bool:

    selector = get_period_selector(
        period,
        target_date,
    )

    return page.locator(
        selector
    ).count() > 0