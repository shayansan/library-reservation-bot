from playwright.sync_api import sync_playwright

from reservation_bot.config import (
    load_settings,
    load_users,
)
from reservation_bot.runner import (
    run_single_reservation,
)


def main() -> None:
    settings = load_settings()

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
        "\nLibrary Reservation Bot v2"
    )

    print(
        "Enabled users:",
        len(enabled_users),
    )

    print(
        "Dry run:",
        settings.dry_run,
    )

    print(
        "Live submission allowed:",
        settings.allow_live_submission,
    )

    with sync_playwright() as playwright:
        for user_config in enabled_users:
            for period in user_config.periods:
                run_single_reservation(
                    playwright,
                    settings,
                    user_config,
                    period,
                )


if __name__ == "__main__":
    main()