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
from reservation_bot.submission import (
    submit_once_and_capture,
)


def choose_period(page):
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


def print_relevant_response_lines(
    body_text: str,
) -> None:
    keywords = (
        "prenot",
        "captcha",
        "codice",
        "errore",
        "error",
        "email",
        "success",
        "grazie",
        "posto",
    )

    print(
        "\nRelevant response text:"
    )

    found = False

    for raw_line in body_text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        lowered = line.casefold()

        if any(
            keyword in lowered
            for keyword in keywords
        ):
            print(
                "-",
                line[:500],
            )

            found = True

    if not found:
        print(
            "- No obvious response message found."
        )


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

        period = choose_period(page)

        if period is None:
            print(
                "No available period found."
            )

            input(
                "Press Enter to close..."
            )

            browser.close()
            return

        print(
            "Selected period:",
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

        wait_for_manual_captcha(
            page,
            timeout_seconds=(
                settings.captcha_timeout_seconds
            ),
        )

        print(
            "\nWARNING:"
        )

        print(
            "The next step will create a REAL "
            "reservation if the CAPTCHA and "
            "form are accepted."
        )

        confirmation = input(
            "\nType SUBMIT to send the reservation: "
        )

        if confirmation != "SUBMIT":
            print(
                "\nSubmission cancelled."
            )

            input(
                "Press Enter to close browser..."
            )

            browser.close()
            return

        result = submit_once_and_capture(
            page
        )

        print(
            "\n================================"
        )

        print(
            "SUBMISSION RESPONSE CAPTURED"
        )

        print(
            "================================"
        )

        print(
            "Status:",
            result.status.value,
        )

        print(
            "URL:",
            result.page_url,
        )

        print(
            "Reservation form still present:",
            result.form_present,
        )

        print(
            "CAPTCHA input still present:",
            result.captcha_present,
        )

        print(
            "Screenshot:",
            result.screenshot_path,
        )

        print(
            "HTML:",
            result.html_path,
        )

        print_relevant_response_lines(
            result.body_text
        )

        print(
            "\nDo not submit again."
        )

        input(
            "\nPress Enter to close browser..."
        )

        browser.close()


if __name__ == "__main__":
    main()