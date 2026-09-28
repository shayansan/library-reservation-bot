from playwright.sync_api import sync_playwright

from reservation_bot.browser import (
    is_period_available,
    open_reservation_page,
)
from reservation_bot.captcha import (
    wait_for_manual_captcha,
)
from reservation_bot.config import (
    load_settings,
    load_users,
)
from reservation_bot.models import (
    ReservationPeriod,
)
from reservation_bot.reservation import (
    prepare_reservation,
)


def choose_test_period(page):
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
            "No enabled users found."
        )

    user = enabled_users[0].user

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

        period = choose_test_period(page)

        if period is None:
            print(
                "No available slot found."
            )

            input(
                "Press Enter to close..."
            )

            browser.close()
            return

        print(
            "Using period:",
            period.value,
        )

        prepare_reservation(
            page,
            user,
            period,
        )

        print(
            "\nForm prepared."
        )

        print(
            "The reservation has NOT "
            "been submitted."
        )

        wait_for_manual_captcha(
            page,
            timeout_seconds=(
                settings.captcha_timeout_seconds
            ),
        )

        print(
            "\n================================"
        )

        print(
            "CAPTCHA DETECTION TEST PASSED"
        )

        print(
            "================================"
        )

        print(
            "\nThe CAPTCHA input was detected."
        )

        print(
            "NO reservation was submitted."
        )

        print(
            "\nDo NOT click Prenota posto."
        )

        input(
            "\nPress Enter to close browser..."
        )

        browser.close()


if __name__ == "__main__":
    main()