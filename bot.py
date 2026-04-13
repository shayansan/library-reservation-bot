from playwright.sync_api import sync_playwright
from datetime import datetime, time as dtime
import time
import threading

from config import (
    URL,
    MY_USERS,
    FRIEND_USERS,
    HEADLESS,
    MAX_RETRIES,
    LOAD_TIMEOUT,
    RESERVATION_HOUR,
    RESERVATION_MINUTE,
    HIGH_TRAFFIC_DAYS,
)

from notifier import send_telegram


# ---------- STATS ----------
stats = {"total": 0, "success": 0, "failed": 0}
lock = threading.Lock()


# ---------- LOG ----------
def log(msg):
    print(msg)


def init_log():
    log("========================================")
    log(f"RUN STARTED AT: {datetime.now()}")
    log("========================================")


# ---------- TIME ----------
def wait_until_target_time():
    log(f"Waiting until {RESERVATION_HOUR:02d}:{RESERVATION_MINUTE:02d}...")
    while True:
        now = datetime.now().time()
        if now >= dtime(RESERVATION_HOUR, RESERVATION_MINUTE):
            log("Target time reached - Starting reservations...")
            send_telegram("⏰ STARTING RESERVATION")
            return
        time.sleep(0.1)


# ---------- WEEKDAY ----------
def is_high_traffic_day():
    return datetime.now().weekday() in HIGH_TRAFFIC_DAYS


# ---------- PAGE LOAD ----------
def open_page_with_retry(page, label):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log(f"[{label}] Loading attempt {attempt}")
            page.goto(URL, timeout=LOAD_TIMEOUT, wait_until="domcontentloaded")
            return True
        except Exception as e:
            log(f"[{label}] load error {e}")
            time.sleep(2)
    return False


# ---------- SLOT ----------
def wait_for_slots(page):
    for _ in range(200):
        try:
            slots = page.locator("text=/08:|14:/")
            if slots.count() >= 2:
                return slots
        except:
            pass
        time.sleep(0.2)
    return None


# ---------- SUBMIT + VERIFY ----------
def submit_and_verify(page):
    page.evaluate("""
    () => {
        const btn = document.querySelector('.pbSubmit');
        if (btn) btn.click();
    }
    """)

    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except:
        pass

    page.wait_for_timeout(4000)

    html = page.content().lower()
    url = page.url

    if "la prenotazione è andata a buon fine" in html:
        return True

    if "prenotazione-postazione" in url and "formid" not in url:
        return True

    if page.locator('input[name="email_1"]').count() == 0:
        return True

    return False


# ---------- WORKER ----------
def process_reservation(user, slot_index, label):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = browser.new_context()
        page = context.new_page()

        if not open_page_with_retry(page, label):
            send_telegram(f"❌ LOAD ERROR | {user['email']}")
            browser.close()
            return

        slots = wait_for_slots(page)

        if not slots:
            send_telegram(f"❌ NO SLOTS | {user['email']}")
            browser.close()
            return

        slots.nth(slot_index).click()
        page.wait_for_timeout(1500)

        page.fill('input[name="fieldname2_1"]', user["name"])
        page.fill('input[name="email_1"]', user["email"])
        page.fill('input[name="fieldname5_1"]', user["student_id"])

        page.check('input[name="fieldname3_1"]')
        page.check('input[name="fieldname6_1"]')

        success = submit_and_verify(page)

        with lock:
            stats["total"] += 1
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1

        if success:
            send_telegram(f"✅ SUCCESS | {user['email']}")
            log(f"[{label}] SUCCESS")
        else:
            send_telegram(f"❌ FAILED | {user['email']}")
            log(f"[{label}] FAILED")

        browser.close()


# ---------- PARALLEL ----------
def run_parallel(users, slot_index, phase):

    threads = []

    log(f"\n{phase} PARALLEL MODE\n")

    for i, user in enumerate(users, 1):
        label = f"{phase}-{i}"

        t = threading.Thread(
            target=process_reservation,
            args=(user, slot_index, label)
        )

        threads.append(t)
        t.start()

    for t in threads:
        t.join()


# ---------- NORMAL ----------
def run_normal(users, slot_index, phase):

    log(f"\n{phase} NORMAL MODE\n")

    for i, user in enumerate(users, 1):
        process_reservation(user, slot_index, f"{phase}-{i}")


# ---------- MAIN ----------
def main():

    init_log()

    high_traffic = is_high_traffic_day()

    if high_traffic:
        log("HIGH TRAFFIC MODE (Wed/Thu)")
        users = MY_USERS + FRIEND_USERS
    else:
        log("NORMAL MODE")
        users = MY_USERS

    wait_until_target_time()

    if high_traffic:
        run_parallel(users, 1, "Evening")
        run_parallel(users, 0, "Morning")
    else:
        run_normal(users, 1, "Evening")
        run_normal(users, 0, "Morning")

    total = stats["total"]
    success = stats["success"]
    failed = stats["failed"]

    success_rate = (success / total * 100) if total > 0 else 0

    summary_msg = (
        f"📊 DAILY SUMMARY\n"
        f"----------------------\n"
        f"Total: {total}\n"
        f"Success: {success}\n"
        f"Failed: {failed}\n"
        f"Success Rate: {success_rate:.1f}%"
    )

    send_telegram(summary_msg)

    send_telegram("🏁 ROBOT FINISHED")

    log("========================================")
    log(f"RUN FINISHED AT: {datetime.now()}")
    log("========================================")
