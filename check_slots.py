from playwright.sync_api import sync_playwright

from reservation_bot.browser import (
    get_available_slots,
    is_period_available,
    open_reservation_page,
)
from reservation_bot.config import load_settings
from reservation_bot.models import ReservationPeriod


def main() -> None:
    settings = load_settings()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=settings.headless,
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

        print("\nOpening UniME reservation page...\n")

        open_reservation_page(
            page,
            settings.reservation_url,
            timeout_ms=settings.load_timeout_ms,
        )

        print("Page loaded successfully.")

        print("\nAvailable slots:")

        slots = get_available_slots(page)

        if not slots:
            print("No available slots found.")

        else:
            for slot in slots:
                print(
                    f"- {slot.date}: "
                    f"{slot.label}"
                )

        morning_available = is_period_available(
            page,
            ReservationPeriod.MORNING,
        )

        afternoon_available = is_period_available(
            page,
            ReservationPeriod.AFTERNOON,
        )

        print("\nPeriod availability:")

        print(
            "Morning:",
            "AVAILABLE"
            if morning_available
            else "NOT AVAILABLE",
        )

        print(
            "Afternoon:",
            "AVAILABLE"
            if afternoon_available
            else "NOT AVAILABLE",
        )

        print(
            "\nREAD-ONLY TEST."
            "\nNo reservation was submitted."
        )

        input(
            "\nPress Enter to close the browser..."
        )

        browser.close()


if __name__ == "__main__":
    main()