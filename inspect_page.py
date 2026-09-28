from playwright.sync_api import sync_playwright


URL = (
    "https://antonello.unime.it/"
    "prenotazione-postazione-biblioteca/?formid=28"
)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page(
            viewport={
                "width": 1400,
                "height": 1000,
            }
        )

        print("\nOpening reservation page...\n")

        page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=45_000,
        )

        # Give the JavaScript booking widget time to render.
        page.wait_for_timeout(2000)

        print("TITLE:")
        print(page.title())

        print("\nURL:")
        print(page.url)

        # --------------------------------------------------
        # KNOWN ELEMENTS
        # --------------------------------------------------

        print("\n========== KNOWN ELEMENTS ==========")

        known_selectors = [
            "#fieldname2_1",
            "#email_1",
            "#fieldname5_1",
            "#fieldname3_1",
            "#fieldname6_1",
            "#hdcaptcha_cp_appbooking_post_1",
            "#captchaimg_1",
            ".pbSubmit",
            "#cp_subbtn_1",
        ]

        for selector in known_selectors:
            locator = page.locator(selector)

            print(f"\nSELECTOR: {selector}")
            print("COUNT:", locator.count())

            if locator.count() > 0:
                try:
                    print(
                        locator.first.evaluate(
                            "(el) => el.outerHTML"
                        )
                    )
                except Exception as e:
                    print("ERROR:", e)

        # --------------------------------------------------
        # SLOT AREA INSPECTION
        # --------------------------------------------------

        print("\n========== SLOT AREA INSPECTION ==========")

        slot_candidates = page.evaluate(
            """
            () => {
                const calendar = document.querySelector(
                    ".ui-datepicker"
                );

                const email = document.querySelector(
                    "#email_1"
                );

                if (!calendar) {
                    return {
                        error: "Calendar element not found"
                    };
                }

                if (!email) {
                    return {
                        error: "Email element not found"
                    };
                }

                const calendarRect =
                    calendar.getBoundingClientRect();

                const emailRect =
                    email.getBoundingClientRect();

                const topLimit =
                    calendarRect.bottom - 10;

                const bottomLimit =
                    emailRect.top + 10;

                const results = [];

                const elements =
                    Array.from(
                        document.querySelectorAll("*")
                    );

                for (const el of elements) {
                    const rect =
                        el.getBoundingClientRect();

                    const style =
                        window.getComputedStyle(el);

                    if (
                        rect.width <= 0 ||
                        rect.height <= 0
                    ) {
                        continue;
                    }

                    if (
                        style.display === "none" ||
                        style.visibility === "hidden"
                    ) {
                        continue;
                    }

                    /*
                    We only care about elements located
                    between the calendar and the email field.
                    */
                    if (
                        rect.bottom < topLimit ||
                        rect.top > bottomLimit
                    ) {
                        continue;
                    }

                    const before =
                        window.getComputedStyle(
                            el,
                            "::before"
                        ).content;

                    const after =
                        window.getComputedStyle(
                            el,
                            "::after"
                        ).content;

                    const attrs = {};

                    for (const attr of el.attributes) {
                        attrs[attr.name] =
                            attr.value;
                    }

                    results.push({
                        tag: el.tagName,
                        id: el.id || null,
                        className:
                            el.className
                                ? String(el.className)
                                : null,

                        text:
                            (el.innerText || "")
                                .trim()
                                .slice(0, 300),

                        before:
                            before,

                        after:
                            after,

                        cursor:
                            style.cursor,

                        x:
                            Math.round(rect.x),

                        y:
                            Math.round(rect.y),

                        width:
                            Math.round(rect.width),

                        height:
                            Math.round(rect.height),

                        attrs:
                            attrs,

                        html:
                            el.outerHTML.slice(
                                0,
                                1200
                            )
                    });
                }

                return {
                    calendarBottom:
                        Math.round(
                            calendarRect.bottom
                        ),

                    emailTop:
                        Math.round(
                            emailRect.top
                        ),

                    elements:
                        results
                };
            }
            """
        )

        if "error" in slot_candidates:
            print(
                "ERROR:",
                slot_candidates["error"]
            )

        else:
            print(
                "Calendar bottom:",
                slot_candidates[
                    "calendarBottom"
                ]
            )

            print(
                "Email top:",
                slot_candidates[
                    "emailTop"
                ]
            )

            elements = slot_candidates[
                "elements"
            ]

            print(
                "Candidate count:",
                len(elements)
            )

            for index, element in enumerate(
                elements,
                start=1,
            ):
                print(
                    f"\n----- CANDIDATE {index} -----"
                )

                print(
                    "TAG:",
                    element["tag"]
                )

                print(
                    "ID:",
                    element["id"]
                )

                print(
                    "CLASS:",
                    element["className"]
                )

                print(
                    "TEXT:",
                    repr(element["text"])
                )

                print(
                    "BEFORE:",
                    element["before"]
                )

                print(
                    "AFTER:",
                    element["after"]
                )

                print(
                    "CURSOR:",
                    element["cursor"]
                )

                print(
                    "POSITION:",
                    (
                        element["x"],
                        element["y"],
                        element["width"],
                        element["height"],
                    )
                )

                print(
                    "ATTRIBUTES:",
                    element["attrs"]
                )

                print(
                    "HTML:",
                    element["html"]
                )

        # --------------------------------------------------
        # CLICKABLE ELEMENTS
        # --------------------------------------------------

        print(
            "\n========== CLICKABLE ELEMENTS "
            "AROUND BOOKING WIDGET =========="
        )

        clickable = page.evaluate(
            """
            () => {
                const email =
                    document.querySelector(
                        "#email_1"
                    );

                if (!email) {
                    return [];
                }

                const emailTop =
                    email.getBoundingClientRect().top;

                const results = [];

                for (
                    const el of
                    document.querySelectorAll("*")
                ) {
                    const rect =
                        el.getBoundingClientRect();

                    const style =
                        getComputedStyle(el);

                    if (
                        rect.width <= 0 ||
                        rect.height <= 0
                    ) {
                        continue;
                    }

                    /*
                    Search roughly 250px above email,
                    where the date/slot widget exists.
                    */
                    if (
                        rect.top <
                            emailTop - 300 ||
                        rect.top >
                            emailTop
                    ) {
                        continue;
                    }

                    const hasClick =
                        typeof el.onclick ===
                            "function" ||
                        el.hasAttribute(
                            "onclick"
                        ) ||
                        style.cursor ===
                            "pointer";

                    if (!hasClick) {
                        continue;
                    }

                    const before =
                        getComputedStyle(
                            el,
                            "::before"
                        ).content;

                    const after =
                        getComputedStyle(
                            el,
                            "::after"
                        ).content;

                    results.push({
                        tag:
                            el.tagName,

                        id:
                            el.id || null,

                        className:
                            el.className
                                ? String(
                                    el.className
                                )
                                : null,

                        text:
                            (
                                el.innerText ||
                                ""
                            )
                            .trim()
                            .slice(
                                0,
                                200
                            ),

                        before:
                            before,

                        after:
                            after,

                        cursor:
                            style.cursor,

                        html:
                            el.outerHTML.slice(
                                0,
                                1000
                            )
                    });
                }

                return results;
            }
            """
        )

        print(
            "Clickable candidate count:",
            len(clickable)
        )

        for index, element in enumerate(
            clickable,
            start=1,
        ):
            print(
                f"\n----- CLICKABLE {index} -----"
            )

            print(
                "TAG:",
                element["tag"]
            )

            print(
                "ID:",
                element["id"]
            )

            print(
                "CLASS:",
                element["className"]
            )

            print(
                "TEXT:",
                repr(element["text"])
            )

            print(
                "BEFORE:",
                element["before"]
            )

            print(
                "AFTER:",
                element["after"]
            )

            print(
                "CURSOR:",
                element["cursor"]
            )

            print(
                "HTML:",
                element["html"]
            )

        print(
            "\n======================================"
        )

        print(
            "\nNo reservation has been submitted."
        )

        input(
            "\nBrowser is still open.\n"
            "Press Enter when finished..."
        )

        browser.close()


if __name__ == "__main__":
    main()