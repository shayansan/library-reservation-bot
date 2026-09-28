from playwright.sync_api import sync_playwright

from reservation_bot.config import (
    load_settings,
    load_users,
)
from reservation_bot.runner import (
    run_single_reservation,
)
from reservation_bot.schedule import (
    ScheduleError,
    get_target_booking_date,
)


def main() -> None:
    settings = load_settings()

    print(
        "\nLibrary Reservation Bot v2"
    )

    print(
        "Dry run:",
        settings.dry_run,
    )

    print(
        "Live submission allowed:",
        settings.allow_live_submission,
    )

    try:
        target_date = get_target_booking_date()

    except ScheduleError as exc:
        print(
            "\nSCHEDULE BLOCK"
        )

        print(
            exc
        )

        print(
            "No reservation workflow will run today."
        )

        return

    print(
        "Target booking date:",
        target_date.isoformat(),
    )

    user_configs = load_users(
        settings.users_file
    )

    enabled_users = [
        user_config
        for user_config in user_configs
        if user_config.enabled
    ]

    if not enabled_users:
        print(
            "No enabled users configured."
        )

        return

    print(
        "Enabled users:",
        len(enabled_users),
    )

    with sync_playwright() as playwright:
        for user_config in enabled_users:
            for period in user_config.periods:
                run_single_reservation(
                    playwright,
                    settings,
                    user_config,
                    period,
                    target_date,
                )


if __name__ == "__main__":
    main()