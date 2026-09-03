#!/usr/bin/env python3
"""Drive the wizard through its steps and drill the catalog for showcase screens.

Complements capture.py (which caught top-level pages). Runs on the student app.
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

STUDENT = "http://localhost:3000"
OUT = Path("brand/video/work/screens")
OUT.mkdir(parents=True, exist_ok=True)
VW = {"width": 1920, "height": 1080}


def goto(pg, url, settle=1.4):
    pg.goto(url, wait_until="domcontentloaded", timeout=45000)
    time.sleep(settle)


def snap(pg, name):
    out = OUT / f"{name}.png"
    try:
        pg.screenshot(path=str(out), full_page=False)
        print("  saved", name)
    except Exception as e:
        print("  FAIL", name, e)


def login(pg):
    goto(pg, f"{STUDENT}/login", settle=0.8)
    pg.locator('input[type="email"]').first.fill("demo@demo.com")
    pg.locator('input[type="password"]').first.fill("demo123")
    pg.locator('button[type="submit"]').first.click()
    time.sleep(2.5)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--force-device-scale-factor=1"],
        )
        pg = browser.new_page(viewport=VW)
        login(pg)

        # ---------------- wizard walkthrough ----------------
        print("wizard step0 (field)")
        goto(pg, f"{STUDENT}/wizard", settle=1.2)
        time.sleep(1.0)
        snap(pg, "wizard-job")  # current state = step 0 field

        # combobox: click input then first option
        try:
            cb = pg.locator('input[role="combobox"]').first
            cb.click(timeout=8000)
            time.sleep(0.6)
            first_opt = pg.locator('[role="option"]').first
            first_opt.click(timeout=8000)
            print("  sid: field selected =", cb.input_value())
            time.sleep(0.8)
            snap(pg, "wizard-field")
        except Exception as e:
            print("  (combobox field fail:", type(e).__name__, e, ")")

        # step1 role
        try:
            pg.locator('button[type="submit"]').last.click(timeout=8000)  # Next
            time.sleep(1.2)
            role_btn = pg.locator(".role").first
            role_btn.click(timeout=8000)
            print("  sid: role chosen:", role_btn.locator("strong").inner_text())
            time.sleep(0.6)
            snap(pg, "wizard-role")
        except Exception as e:
            print("  (role step fail:", type(e).__name__, ")")

        # step2 self-assessment (AI off => use self assessment link)
        try:
            pg.locator('button[type="submit"]').last.click(timeout=8000)
            time.sleep(1.2)
            self_link = pg.locator("button.link", has_text="self").first
            self_link.click(timeout=8000)
            time.sleep(1.2)
            snap(pg, "wizard-self")
        except Exception as e:
            print("  (self assess fail:", type(e).__name__, e, ")")

        # step3 preferences
        try:
            pg.locator('button[type="submit"]').last.click(timeout=8000)
            time.sleep(1.2)
            snap(pg, "wizard-preferences")
        except Exception as e:
            print("  (preferences fail:", type(e).__name__, ")")

        # step4 review
        try:
            pg.locator('button[type="submit"]').last.click(timeout=8000)
            time.sleep(1.6)
            snap(pg, "wizard-review")
        except Exception as e:
            print("  (review fail:", type(e).__name__, e, ")")

        # ---------------- catalog drill ----------------
        print("catalog category")
        goto(pg, f"{STUDENT}/catalog", settle=1.2)
        try:
            view_btn = pg.locator(".cat-foot button").first
            view_btn.click(timeout=8000)
            time.sleep(1.2)
            snap(pg, "catalog-category")
        except Exception as e:
            print("  (category fail:", type(e).__name__, ")")

        print("catalog skill detail")
        try:
            skill_btn = pg.locator(".skill-card").first
            skill_btn.click(timeout=8000)
            time.sleep(1.6)
            snap(pg, "catalog-skill")
        except Exception as e:
            print("  (skill fail:", type(e).__name__, ")")

        pg.close()
        browser.close()
    print("DONE")


if __name__ == "__main__":
    main()