import requests


class NotificationError(RuntimeError):
    """Raised when a notification cannot be delivered."""


def telegram_is_configured(
    token: str | None,
    chat_id: str | None,
) -> bool:
    return bool(token and chat_id)


def send_telegram_message(
    token: str,
    chat_id: str,
    message: str,
    *,
    timeout_seconds: int = 15,
) -> None:
    """
    Send a plain-text Telegram message.
    """

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
        },
        timeout=timeout_seconds,
    )

    if not response.ok:
        raise NotificationError(
            "Telegram notification failed: "
            f"HTTP {response.status_code} "
            f"{response.text[:300]}"
        )