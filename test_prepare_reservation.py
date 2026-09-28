from playwright.sync_api import sync_playwright

from reservation_bot.browser import (
    is_period_available,
    open_reservation_page,
)
from reservation_bot.config import (
    load_settings,
    load_users,
)
from reservation_bot.models import ReservationPeriod
from reservation_bot.reservation import prepare_reservation


def choose_test_period(page):
    """
    Prefer morning for the test.
    If morning is unavailable, use afternoon.

    If neither is available, return None.
    """

    if is_period_available(
        page,
        ReservationPeriod.MORNING,
    ):
        return ReservationPeriod.MORNING

    if is_period_available(
        page,
        ReservationPeriod.AFTERNOON,
    ):
        return ReservationPeriod.AFTERNOON

    return None


def main() -> None:
    settings = load_settings()

    user_configs = load_users(
        settings.users_file
    )

    enabled_users = [
        item
        for item in user_configs
        if item.enabled
    ]

    if not enabled_users:
        raise RuntimeError(
            "No enabled users found in users.json."
        )

    test_user_config = enabled_users[0]

    user = test_user_config.user

    print("\nUsing first enabled local user.")
    print(
        "User email:",
        user.email,
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
        )

        page = browser.new_page(
            viewport={
                "width": 1400,
                "height": 1000,
            }
        )

        page.set_default_timeout(
            settings.action_timeout_ms
        )

        print(
            "\nOpening reservation page..."
        )

        open_reservation_page(
            page,
            settings.reservation_url,
            timeout_ms=settings.load_timeout_ms,
        )

        print(
            "Reservation page loaded."
        )

        period = choose_test_period(page)

        if period is None:
            print(
                "\nNo available reservation period "
                "was found."
            )

            input(
                "\nPress Enter to close browser..."
            )

            browser.close()
            return

        print(
            "\nSelected test period:",
            period.value,
        )

        print(
            "\nPreparing reservation form..."
        )

        prepare_reservation(
            page,
            user,
            period,
        )

        print(
            "\n================================"
        )

        print(
            "FORM PREPARED SUCCESSFULLY"
        )

        print(
            "================================"
        )

        print(
            "\nThe bot has:"
        )

        print(
            "- selected an available slot"
        )

        print(
            "- filled name"
        )

        print(
            "- filled email"
        )

        print(
            "- filled student ID"
        )

        print(
            "- accepted required checkboxes"
        )

        print(
            "- verified the CAPTCHA exists"
        )

        print(
            "\nIMPORTANT:"
        )

        print(
            "The CAPTCHA has NOT been solved."
        )

        print(
            "The reservation has NOT been submitted."
        )

        print(
            "\nInspect the browser now."
        )

        input(
            "\nPress Enter to close the browser..."
        )

        browser.close()


if __name__ == "__main__":
    main()