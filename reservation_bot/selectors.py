"""
CSS selectors for the UniME library reservation page.

All site-specific selectors are kept in this module so that
changes to the website can be updated in one place.
"""


# ---------------------------------------------------------
# Main form
# ---------------------------------------------------------

FORM = "#cp_appbooking_pform_1"


# ---------------------------------------------------------
# User information
# ---------------------------------------------------------

NAME_INPUT = "#fieldname2_1"

EMAIL_INPUT = "#email_1"

STUDENT_ID_INPUT = "#fieldname5_1"


# ---------------------------------------------------------
# Required agreements
# ---------------------------------------------------------

TERMS_CHECKBOX = "#fieldname3_1"

PRIVACY_CHECKBOX = "#fieldname6_1"


# ---------------------------------------------------------
# CAPTCHA
# ---------------------------------------------------------

CAPTCHA_INPUT = "#hdcaptcha_cp_appbooking_post_1"

CAPTCHA_IMAGE = "#captchaimg_1"


# ---------------------------------------------------------
# Reservation submit
# ---------------------------------------------------------

SUBMIT_BUTTON = ".pbSubmit"

SUBMIT_CONTAINER = "#cp_subbtn_1"


# ---------------------------------------------------------
# Booking calendar
# ---------------------------------------------------------

CALENDAR = ".fieldCalendarfieldname1_1"

CALENDAR_DAY = ".ui-datepicker-calendar a[data-date]"


# ---------------------------------------------------------
# Slots
# ---------------------------------------------------------

SLOTS_CONTAINER = ".slotsCalendarfieldname1_1"

AVAILABLE_SLOT = (
    ".slotsCalendarfieldname1_1 "
    ".availableslot > a"
)


# ---------------------------------------------------------
# Specific reservation periods
# ---------------------------------------------------------

MORNING_SLOT = (
    ".slotsCalendarfieldname1_1 "
    '.availableslot > a'
    '[h1="8"]'
    '[m1="30"]'
    '[h2="14"]'
    '[m2="0"]'
)

AFTERNOON_SLOT = (
    ".slotsCalendarfieldname1_1 "
    '.availableslot > a'
    '[h1="14"]'
    '[m1="0"]'
    '[h2="23"]'
    '[m2="55"]'
)