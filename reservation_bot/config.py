import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from reservation_bot.models import (
    ReservationPeriod,
    User,
)


load_dotenv()


DEFAULT_RESERVATION_URL = (
    "https://antonello.unime.it/"
    "prenotazione-postazione-biblioteca/?formid=28"
)


@dataclass(frozen=True, slots=True)
class UserReservationConfig:
    user: User
    enabled: bool
    periods: tuple[ReservationPeriod, ...]


@dataclass(frozen=True, slots=True)
class Settings:
    reservation_url: str
    users_file: Path

    headless: bool

    load_timeout_ms: int
    action_timeout_ms: int
    captcha_timeout_seconds: int

    reservation_hour: int
    reservation_minute: int

    dry_run: bool
    allow_live_submission: bool

    telegram_token: str | None
    telegram_chat_id: str | None


class ConfigurationError(RuntimeError):
    """Raised when local configuration is invalid."""


def _get_bool(
    name: str,
    default: bool,
) -> bool:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    value = raw_value.strip().lower()

    if value in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return True

    if value in {
        "0",
        "false",
        "no",
        "off",
    }:
        return False

    raise ConfigurationError(
        f"{name} must be true or false, "
        f"got: {raw_value!r}"
    )


def _get_int(
    name: str,
    default: int,
) -> int:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    try:
        return int(raw_value)

    except ValueError as exc:
        raise ConfigurationError(
            f"{name} must be an integer, "
            f"got: {raw_value!r}"
        ) from exc


def load_settings() -> Settings:
    settings = Settings(
        reservation_url=os.getenv(
            "RESERVATION_URL",
            DEFAULT_RESERVATION_URL,
        ),
        users_file=Path(
            os.getenv(
                "USERS_FILE",
                "config/users.json",
            )
        ),
        headless=_get_bool(
            "HEADLESS",
            False,
        ),
        load_timeout_ms=_get_int(
            "LOAD_TIMEOUT_MS",
            45_000,
        ),
        action_timeout_ms=_get_int(
            "ACTION_TIMEOUT_MS",
            15_000,
        ),
        captcha_timeout_seconds=_get_int(
            "CAPTCHA_TIMEOUT_SECONDS",
            300,
        ),
        reservation_hour=_get_int(
            "RESERVATION_HOUR",
            8,
        ),
        reservation_minute=_get_int(
            "RESERVATION_MINUTE",
            0,
        ),
        dry_run=_get_bool(
            "DRY_RUN",
            True,
        ),
        allow_live_submission=_get_bool(
            "ALLOW_LIVE_SUBMISSION",
            False,
        ),
        telegram_token=(
            os.getenv("TELEGRAM_TOKEN")
            or None
        ),
        telegram_chat_id=(
            os.getenv("TELEGRAM_CHAT_ID")
            or None
        ),
    )

    if not 0 <= settings.reservation_hour <= 23:
        raise ConfigurationError(
            "RESERVATION_HOUR must be between 0 and 23."
        )

    if not 0 <= settings.reservation_minute <= 59:
        raise ConfigurationError(
            "RESERVATION_MINUTE must be between 0 and 59."
        )

    if settings.load_timeout_ms <= 0:
        raise ConfigurationError(
            "LOAD_TIMEOUT_MS must be greater than zero."
        )

    if settings.action_timeout_ms <= 0:
        raise ConfigurationError(
            "ACTION_TIMEOUT_MS must be greater than zero."
        )

    if settings.captcha_timeout_seconds <= 0:
        raise ConfigurationError(
            "CAPTCHA_TIMEOUT_SECONDS must be greater than zero."
        )

    return settings


def load_users(
    path: Path,
) -> list[UserReservationConfig]:

    if not path.exists():
        raise ConfigurationError(
            f"Users file does not exist: {path}"
        )

    try:
        raw_data = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

    except json.JSONDecodeError as exc:
        raise ConfigurationError(
            f"Invalid JSON in users file: {path}"
        ) from exc

    if not isinstance(raw_data, list):
        raise ConfigurationError(
            "Users file must contain a JSON list."
        )

    users: list[UserReservationConfig] = []

    for index, item in enumerate(raw_data):
        if not isinstance(item, dict):
            raise ConfigurationError(
                f"User #{index + 1} must be an object."
            )

        try:
            name = str(
                item["name"]
            ).strip()

            email = str(
                item["email"]
            ).strip()

            student_id = str(
                item["student_id"]
            ).strip()

        except KeyError as exc:
            raise ConfigurationError(
                f"User #{index + 1} is missing "
                f"required field: {exc.args[0]}"
            ) from exc

        if not name:
            raise ConfigurationError(
                f"User #{index + 1} has an empty name."
            )

        if not email:
            raise ConfigurationError(
                f"User #{index + 1} has an empty email."
            )

        if not student_id:
            raise ConfigurationError(
                f"User #{index + 1} has an empty student_id."
            )

        enabled = bool(
            item.get(
                "enabled",
                True,
            )
        )

        raw_periods = item.get(
            "periods",
            ["morning"],
        )

        if not isinstance(
            raw_periods,
            list,
        ):
            raise ConfigurationError(
                f"User #{index + 1} periods "
                "must be a list."
            )

        periods: list[
            ReservationPeriod
        ] = []

        for raw_period in raw_periods:
            try:
                period = ReservationPeriod(
                    str(raw_period)
                )

            except ValueError as exc:
                raise ConfigurationError(
                    f"User #{index + 1} has "
                    f"invalid period: {raw_period!r}"
                ) from exc

            periods.append(
                period
            )

        if not periods:
            raise ConfigurationError(
                f"User #{index + 1} must have "
                "at least one reservation period."
            )

        user = User(
            name=name,
            email=email,
            student_id=student_id,
        )

        users.append(
            UserReservationConfig(
                user=user,
                enabled=enabled,
                periods=tuple(periods),
            )
        )

    return users