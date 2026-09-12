from playwright.sync_api import Page

from reservation_bot.models import (
    ReservationPeriod,
    User,
)
from reservation_bot.selectors import (
    AFTERNOON_SLOT,
    CAPTCHA_INPUT,
    CAPTCHA_IMAGE,
    EMAIL_INPUT,
    MORNING_SLOT,
    NAME_INPUT,
    PRIVACY_CHECKBOX,
    STUDENT_ID_INPUT,
    TERMS_CHECKBOX,
)


class ReservationPreparationError(RuntimeError):
    """Raised when the reservation form cannot be prepared safely."""


def get_slot_selector(
    period: ReservationPeriod,
) -> str:
    if period is ReservationPeriod.MORNING:
        return MORNING_SLOT

    if period is ReservationPeriod.AFTERNOON:
        return AFTERNOON_SLOT

    raise ValueError(
        f"Unsupported reservation period: {period}"
    )


def select_available_slot(
    page: Page,
    period: ReservationPeriod,
) -> None:
    """
    Select the requested period only if the website currently
    marks it as available.
    """

    selector = get_slot_selector(period)

    slot = page.locator(selector)

    if slot.count() == 0:
        raise ReservationPreparationError(
            f"{period.value} slot is not currently available."
        )

    if slot.count() > 1:
        raise ReservationPreparationError(
            f"Expected one {period.value} slot, "
            f"found {slot.count()}."
        )

    slot.click()

    page.wait_for_timeout(500)


def fill_user_information(
    page: Page,
    user: User,
) -> None:
    """
    Fill the user-specific reservation form fields.
    """

    page.locator(NAME_INPUT).fill(user.name)

    page.locator(EMAIL_INPUT).fill(user.email)

    page.locator(STUDENT_ID_INPUT).fill(
        user.student_id
    )


def accept_required_agreements(
    page: Page,
) -> None:
    """
    Check the required terms and privacy checkboxes.
    """

    terms = page.locator(TERMS_CHECKBOX)

    privacy = page.locator(PRIVACY_CHECKBOX)

    if not terms.is_checked():
        terms.check()

    if not privacy.is_checked():
        privacy.check()


def verify_captcha_present(
    page: Page,
) -> None:
    """
    Verify that the CAPTCHA UI exists.

    The CAPTCHA is not solved automatically.
    """

    captcha_image = page.locator(CAPTCHA_IMAGE)

    captcha_input = page.locator(CAPTCHA_INPUT)

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
) -> None:
    """
    Prepare a reservation up to the CAPTCHA step.

    This function intentionally does NOT submit the form.
    """

    select_available_slot(
        page,
        period,
    )

    fill_user_information(
        page,
        user,
    )

    accept_required_agreements(
        page,
    )

    verify_captcha_present(page)