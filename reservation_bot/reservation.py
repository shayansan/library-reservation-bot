from datetime import date

from playwright.sync_api import Page

from reservation_bot.browser import (
    get_period_selector,
)
from reservation_bot.models import (
    ReservationPeriod,
    User,
)
from reservation_bot.selectors import (
    CAPTCHA_IMAGE,
    CAPTCHA_INPUT,
    EMAIL_INPUT,
    NAME_INPUT,
    PRIVACY_CHECKBOX,
    STUDENT_ID_INPUT,
    TERMS_CHECKBOX,
)


class ReservationPreparationError(RuntimeError):
    """Raised when the reservation form cannot be prepared safely."""


def select_available_slot(
    page: Page,
    period: ReservationPeriod,
    target_date: date,
) -> None:

    selector = get_period_selector(
        period,
        target_date,
    )

    slot = page.locator(
        selector
    )

    count = slot.count()

    if count == 0:
        raise ReservationPreparationError(
            f"{period.value} slot is not available "
            f"for {target_date.isoformat()}."
        )

    if count > 1:
        raise ReservationPreparationError(
            f"Expected exactly one {period.value} "
            f"slot for {target_date.isoformat()}, "
            f"found {count}."
        )

    actual_date = slot.get_attribute(
        "d"
    )

    expected_date = target_date.isoformat()

    if actual_date != expected_date:
        raise ReservationPreparationError(
            "Slot date safety check failed. "
            f"Expected {expected_date}, "
            f"got {actual_date!r}."
        )

    slot.click()

    page.wait_for_timeout(
        500
    )


def fill_user_information(
    page: Page,
    user: User,
) -> None:

    page.locator(
        NAME_INPUT
    ).fill(
        user.name
    )

    page.locator(
        EMAIL_INPUT
    ).fill(
        user.email
    )

    page.locator(
        STUDENT_ID_INPUT
    ).fill(
        user.student_id
    )


def accept_required_agreements(
    page: Page,
) -> None:

    terms = page.locator(
        TERMS_CHECKBOX
    )

    privacy = page.locator(
        PRIVACY_CHECKBOX
    )

    if not terms.is_checked():
        terms.check()

    if not privacy.is_checked():
        privacy.check()


def verify_captcha_present(
    page: Page,
) -> None:

    captcha_image = page.locator(
        CAPTCHA_IMAGE
    )

    captcha_input = page.locator(
        CAPTCHA_INPUT
    )

    if captcha_image.count() != 1:
        raise ReservationPreparationError(
            "CAPTCHA image was not found."
        )

    if captcha_input.count() != 1:
        raise ReservationPreparationError(
            "CAPTCHA input was not found."
        )


def prepare_reservation(
    page: Page,
    user: User,
    period: ReservationPeriod,
    target_date: date,
) -> None:

    select_available_slot(
        page,
        period,
        target_date,
    )

    fill_user_information(
        page,
        user,
    )

    accept_required_agreements(
        page,
    )

    verify_captcha_present(
        page
    )