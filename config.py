import os

# ---------- URL ----------
URL = "https://antonello.unime.it/prenotazione-postazione-biblioteca/?formid=28"


# ---------- TELEGRAM (from .env) ----------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# ---------- USERS ----------
MY_USERS = [
    {
        "name": "your_name",
        "student_id": "your_student_id",
        "email": "your_email"
    }
]

FRIEND_USERS = [
    {
        "name": "friend_name",
        "student_id": "friend_student_id",
        "email": "friend_email"
    }
]


# ---------- SETTINGS ----------
HEADLESS = True
MAX_RETRIES = 5
LOAD_TIMEOUT = 45000


# ---------- TIME SETTINGS ----------
RESERVATION_HOUR = 8
RESERVATION_MINUTE = 0


# ---------- HIGH TRAFFIC DAYS (Wed / Thu) ----------
HIGH_TRAFFIC_DAYS = [2, 3]
