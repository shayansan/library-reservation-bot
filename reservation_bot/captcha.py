import time

from playwright.sync_api import Page

from reservation_bot.selectors import (
    CAPTCHA_IMAGE,
    CAPTCHA_INPUT,
)


class CaptchaError(RuntimeError):
    """Raised when the CAPTCHA step cannot be completed."""


def captcha_is_present(page: Page) -> bool:
    """
    Return True when both the CAPTCHA image and input exist.
    """

    image = page.locator(CAPTCHA_IMAGE)
    captcha_input = page.locator(CAPTCHA_INPUT)

    return (
        image.count() == 1
        and captcha_input.count() == 1
    )


def get_captcha_value(page: Page) -> str:
    """
    Read the current text entered in the CAPTCHA field.

    This does not solve or modify the CAPTCHA.
    """

    captcha_input = page.locator(CAPTCHA_INPUT)

    if captcha_input.count() != 1:
        raise CaptchaError(
            "CAPTCHA input was not found."
        )

    return captcha_input.input_value().strip()


def wait_for_manual_captcha(
    page: Page,
    *,
    timeout_seconds: int = 300,
    poll_interval_seconds: float = 0.25,
) -> str:
    """
    Wait until the user manually enters text into the CAPTCHA field.

    The CAPTCHA is never solved automatically and the form is
    never submitted by this function.
    """

    if not captcha_is_present(page):
        raise CaptchaError(
            "CAPTCHA controls were not found."
        )

    print(
        "\nCAPTCHA REQUIRED"
        "\nEnter the CAPTCHA manually in the browser."
    )

    deadline = (
        time.monotonic()
        + timeout_seconds
    )

    while time.monotonic() < deadline:
        value = get_captcha_value(page)

        if value:
            print(
                "\nCAPTCHA input detected."
            )

            return value

        time.sleep(
            poll_interval_seconds
        )

    raise CaptchaError(
        "Timed out while waiting for manual CAPTCHA input."
    )