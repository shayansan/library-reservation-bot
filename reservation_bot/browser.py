from playwright.sync_api import Page

from reservation_bot.models import (
    ReservationPeriod,
    Slot,
)
from reservation_bot.selectors import (
    AFTERNOON_SLOT,
    AVAILABLE_SLOT,
    FORM,
    MORNING_SLOT,
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
    """
    Open the UniME reservation page and wait until the booking
    form and slot widget have been rendered.

    This function does not click a slot and does not submit
    any reservation.
    """

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


def get_available_slots(page: Page) -> list[Slot]:
    """
    Read the slots that the website currently marks as available.

    Only anchors inside `.availableslot` are accepted.
    Used/unavailable slots are intentionally ignored.
    """

    locator = page.locator(AVAILABLE_SLOT)

    slots: list[Slot] = []

    for index in range(locator.count()):
        element = locator.nth(index)

        date = element.get_attribute("d")

        h1 = element.get_attribute("h1")
        m1 = element.get_attribute("m1")
        h2 = element.get_attribute("h2")
        m2 = element.get_attribute("m2")

        attributes = {
            "date": date,
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

        slot = Slot(
            date=date,
            start_hour=int(h1),
            start_minute=int(m1),
            end_hour=int(h2),
            end_minute=int(m2),
        )

        slots.append(slot)

    return slots


def is_period_available(
    page: Page,
    period: ReservationPeriod,
) -> bool:
    """
    Return True only if the requested reservation period is
    currently represented by an available slot.
    """

    if period is ReservationPeriod.MORNING:
        selector = MORNING_SLOT

    elif period is ReservationPeriod.AFTERNOON:
        selector = AFTERNOON_SLOT

    else:
        raise ValueError(
            f"Unsupported reservation period: {period}"
        )

    return page.locator(selector).count() > 0