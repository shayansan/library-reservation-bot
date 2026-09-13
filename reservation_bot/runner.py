from playwright.sync_api import (
    Browser,
    Page,
    Playwright,
)

from reservation_bot.browser import (
    is_period_available,
    open_reservation_page,
)
from reservation_bot.captcha import (
    wait_for_manual_captcha,
)
from reservation_bot.config import (
    Settings,
    UserReservationConfig,
)
from reservation_bot.models import (
    ReservationPeriod,
)
from reservation_bot.notifier import (
    send_telegram_message,
    telegram_is_configured,
)
from reservation_bot.reservation import (
    prepare_reservation,
)
from reservation_bot.submission import (
    SubmissionResult,
    SubmissionStatus,
    submit_once_and_capture,
)


def create_page(
    browser: Browser,
    settings: Settings,
) -> Page:
    page = browser.new_page(
        viewport={
            "width": 1400,
            "height": 1000,
        }
    )

    page.set_default_timeout(
        settings.action_timeout_ms
    )

    return page


def send_notification_safely(
    settings: Settings,
    message: str,
) -> None:
    if not telegram_is_configured(
        settings.telegram_token,
        settings.telegram_chat_id,
    ):
        return

    try:
        send_telegram_message(
            settings.telegram_token,
            settings.telegram_chat_id,
            message,
        )

    except Exception as exc:
        print(
            "\nTelegram notification failed:",
            exc,
        )


def notify_captcha_ready(
    settings: Settings,
    user_config: UserReservationConfig,
    period: ReservationPeriod,
) -> None:
    user = user_config.user

    message = (
        "Library reservation CAPTCHA ready\n"
        f"User: {user.name}\n"
        f"Period: {period.value}\n"
        "Enter the CAPTCHA manually in the open browser."
    )

    send_notification_safely(
        settings,
        message,
    )


def notify_result(
    settings: Settings,
    user_config: UserReservationConfig,
    period: ReservationPeriod,
    result: SubmissionResult,
) -> None:
    user = user_config.user

    message = (
        "Library reservation result\n"
        f"User: {user.name}\n"
        f"Period: {period.value}\n"
        f"Status: {result.status.value}"
    )

    send_notification_safely(
        settings,
        message,
    )


def run_single_reservation(
    playwright: Playwright,
    settings: Settings,
    user_config: UserReservationConfig,
    period: ReservationPeriod,
) -> SubmissionResult | None:

    user = user_config.user

    print(
        "\n--------------------------------"
    )

    print(
        "User:",
        user.name,
    )

    print(
        "Period:",
        period.value,
    )

    browser = playwright.chromium.launch(
        headless=False,
    )

    page = create_page(
        browser,
        settings,
    )

    try:
        print(
            "\nOpening reservation page..."
        )

        open_reservation_page(
            page,
            settings.reservation_url,
            timeout_ms=settings.load_timeout_ms,
        )

        if not is_period_available(
            page,
            period,
        ):
            print(
                "Requested period is not available."
            )

            return None

        prepare_reservation(
            page,
            user,
            period,
        )

        print(
            "\nForm prepared successfully."
        )

        if settings.dry_run:
            print(
                "\nDRY RUN MODE"
            )

            print(
                "The form was prepared, but:"
            )

            print(
                "- CAPTCHA will not be entered"
            )

            print(
                "- reservation will not be submitted"
            )

            return None

        if not settings.allow_live_submission:
            print(
                "\nLIVE SUBMISSION BLOCKED"
            )

            print(
                "ALLOW_LIVE_SUBMISSION is false."
            )

            print(
                "No reservation will be submitted."
            )

            return None

        notify_captcha_ready(
            settings,
            user_config,
            period,
        )

        print(
            "\nWaiting for manual CAPTCHA..."
        )

        wait_for_manual_captcha(
            page,
            timeout_seconds=(
                settings.captcha_timeout_seconds
            ),
        )

        print(
            "\nCAPTCHA input detected."
        )

        print(
            "Submitting automatically..."
        )

        result = submit_once_and_capture(
            page
        )

        print(
            "\nReservation result:",
            result.status.value,
        )

        if (
            result.status
            is SubmissionStatus.SUCCESS
        ):
            print(
                "Reservation confirmed successfully."
            )

        elif (
            result.status
            is SubmissionStatus.DUPLICATE
        ):
            print(
                "A reservation already exists "
                "for this period."
            )

        elif (
            result.status
            is SubmissionStatus.SLOT_UNAVAILABLE
        ):
            print(
                "The selected slot is "
                "no longer available."
            )

        else:
            print(
                "The server response could not "
                "be classified safely."
            )

            print(
                "Screenshot:",
                result.screenshot_path,
            )

            print(
                "HTML:",
                result.html_path,
            )

        notify_result(
            settings,
            user_config,
            period,
            result,
        )

        return result

    finally:
        browser.close()