from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from playwright.sync_api import Page

from reservation_bot.selectors import (
    CAPTCHA_INPUT,
    FORM,
    SUBMIT_BUTTON,
)


class SubmissionStatus(str, Enum):
    SUCCESS = "success"
    DUPLICATE = "duplicate"
    SLOT_UNAVAILABLE = "slot_unavailable"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    status: SubmissionStatus
    page_url: str
    form_present: bool
    captcha_present: bool
    body_text: str
    screenshot_path: Path
    html_path: Path


SUCCESS_MESSAGE = (
    "La prenotazione è andata a buon fine!"
)

DUPLICATE_MESSAGE = (
    "Prenotazione già esistente "
    "per questo giorno e questo orario"
)

SLOT_UNAVAILABLE_MESSAGES = (
    "No more slots available.",
    (
        "Selected time is no longer available. "
        "Please select a different time."
    ),
)


def _create_artifact_paths() -> tuple[Path, Path]:
    artifact_dir = Path("artifacts")

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    screenshot_path = (
        artifact_dir
        / f"submission-{timestamp}.png"
    )

    html_path = (
        artifact_dir
        / f"submission-{timestamp}.html"
    )

    return (
        screenshot_path,
        html_path,
    )


def _classify_result(
    body_text: str,
) -> SubmissionStatus:
    normalized = body_text.casefold()

    if SUCCESS_MESSAGE.casefold() in normalized:
        return SubmissionStatus.SUCCESS

    if DUPLICATE_MESSAGE.casefold() in normalized:
        return SubmissionStatus.DUPLICATE

    for message in SLOT_UNAVAILABLE_MESSAGES:
        if message.casefold() in normalized:
            return SubmissionStatus.SLOT_UNAVAILABLE

    return SubmissionStatus.UNKNOWN


def submit_once_and_capture(
    page: Page,
) -> SubmissionResult:
    """
    Submit the prepared reservation exactly once and capture
    the resulting page for analysis.

    Success is accepted only when the website returns its
    confirmed success message.
    """

    captcha_value = (
        page.locator(CAPTCHA_INPUT)
        .input_value()
        .strip()
    )

    if not captcha_value:
        raise RuntimeError(
            "CAPTCHA field is empty. "
            "Submission cancelled."
        )

    submit_button = page.locator(
        SUBMIT_BUTTON
    )

    if submit_button.count() != 1:
        raise RuntimeError(
            "Expected exactly one submit button, "
            f"found {submit_button.count()}."
        )

    print(
        "\nSubmitting reservation exactly once..."
    )

    submit_button.click()

    try:
        page.wait_for_load_state(
            "domcontentloaded",
            timeout=10_000,
        )

    except Exception:
        pass

    page.wait_for_timeout(
        2_000
    )

    body_text = (
        page.locator("body")
        .inner_text()
    )

    screenshot_path, html_path = (
        _create_artifact_paths()
    )

    page.screenshot(
        path=str(screenshot_path),
        full_page=True,
    )

    html_path.write_text(
        page.content(),
        encoding="utf-8",
    )

    form_present = (
        page.locator(FORM).count() > 0
    )

    captcha_present = (
        page.locator(CAPTCHA_INPUT).count() > 0
    )

    status = _classify_result(
        body_text
    )

    return SubmissionResult(
        status=status,
        page_url=page.url,
        form_present=form_present,
        captcha_present=captcha_present,
        body_text=body_text,
        screenshot_path=screenshot_path,
        html_path=html_path,
    )