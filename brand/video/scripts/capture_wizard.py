#!/usr/bin/env python3
"""Drive the wizard through all 5 steps for showcase screens (field -> role -> self-assess -> preferences -> review)."""
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
    pg.screenshot(path=str(OUT / f"{name}.png"), full_page=False)
    print("  saved", name)


def login(pg):
    goto(pg, f"{STUDENT}/login", settle=0.8)
    pg.locator('input[type="email"]').first.fill("demo@demo.com")
    pg.locator('input[type="password"]').first.fill("demo123")
    pg.locator('button[type="submit"]').first.click()
    time.sleep(2.5)


NEXT = ".nav button.btn.primary"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--force-device-scale-factor=1"],
        )
        pg = browser.new_page(viewport=VW)
        login(pg)
        goto(pg, f"{STUDENT}/wizard", settle=1.2)
        time.sleep(1.0)
        snap(pg, "wizard-job")

        print("step0 -> field")
        cb = pg.locator('input[role="combobox"]').first
        cb.click(timeout=10000)
        time.sleep(0.7)
        pg.locator('[role="option"]').first.click(timeout=10000)
        time.sleep(0.7)
        print("  field:", cb.input_value())
        snap(pg, "wizard-field")

        print("step1 -> role")
        pg.locator(NEXT).click(timeout=10000)
        time.sleep(1.3)
        role = pg.locator(".role").first
        role.click(timeout=10000)
        print("  role:", role.locator("strong").inner_text())
        time.sleep(0.6)
        snap(pg, "wizard-role")

        print("step2 -> self assessment")
        pg.locator(NEXT).click(timeout=10000)
        time.sleep(1.5)
        sel = pg.get_by_role("button", name="self").first
        sel.click(timeout=10000)
        time.sleep(1.6)
        snap(pg, "wizard-self")

        print("step3 -> preferences")
        pg.locator(NEXT).click(timeout=10000)
        time.sleep(1.4)
        snap(pg, "wizard-preferences")

        print("step4 -> review")
        pg.locator(NEXT).click(timeout=10000)
        time.sleep(2.0)
        snap(pg, "wizard-review")

        pg.close()
        browser.close()
    print("DONE")


if __name__ == "__main__":
    main()