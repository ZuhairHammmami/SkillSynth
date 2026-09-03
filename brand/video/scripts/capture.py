#!/usr/bin/env python3
"""Capture SkillSynth showcase screens at 1920x1080 via Playwright + system Chromium.

Student app on :3000 (bilingual RTL), admin app on :3001 (English).
Avoids wait_until="networkidle" (app holds an SSE connection open) - uses
domcontentloaded + settled waits. One bad shot does not kill the run.

Usage: source .venv/bin/activate && python3 capture.py <out_dir>
"""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

STUDENT = "http://localhost:3000"
ADMIN = "http://localhost:3001"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "screens")
OUT.mkdir(parents=True, exist_ok=True)

VW = {"width": 1920, "height": 1080}


def goto(pg, url, settle=1.4):
    pg.goto(url, wait_until="domcontentloaded", timeout=45000)
    time.sleep(settle)


def login(pg, base, email, password):
    goto(pg, f"{base}/login" if base == STUDENT else f"{base}/", settle=0.8)
    email_box = pg.locator('input[type="email"]').first
    pw_box = pg.locator('input[type="password"]').first
    email_box.fill(email)
    pw_box.fill(password)
    pg.locator('button[type="submit"]').first.click()
    time.sleep(2.5)
    if base == ADMIN:
        pg.wait_for_url("**/dashboard**", timeout=45000)
        time.sleep(1.5)


def snap(pg, name):
    out = OUT / f"{name}.png"
    try:
        pg.screenshot(path=str(out), full_page=False)
        print("  saved", name)
    except Exception as e:
        print("  FAIL", name, e)


def capture_range(pg, base, items):
    for name, path in items:
        print(name)
        try:
            goto(pg, f"{base}{path}", settle=1.3)
            snap(pg, name)
        except Exception as e:
            print("  FAIL", name, e)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--force-device-scale-factor=1"],
        )

        # ---------------- student (public + demo) ----------------
        pg = browser.new_page(viewport=VW)

        print("landing"); goto(pg, f"{STUDENT}/", settle=1.6); snap(pg, "landing")
        print("login"); goto(pg, f"{STUDENT}/login", settle=1.0); snap(pg, "login")
        print("register"); goto(pg, f"{STUDENT}/register", settle=1.0); snap(pg, "register")

        print("login demo")
        login(pg, STUDENT, "demo@demo.com", "demo123")
        snap(pg, "dashboard")

        capture_range(pg, STUDENT, [
            ("wizard-job", "/wizard"),
            ("catalog", "/catalog"),
            ("learn", "/learn"),
            ("analytics", "/analytics"),
            ("profile", "/profile"),
            ("settings", "/settings"),
        ])

        # skill detail (click first catalog card link if present)
        print("skill-detail")
        try:
            goto(pg, f"{STUDENT}/catalog", settle=1.0)
            link = pg.locator("a[href*='/catalog/'], a[href*='/skills/']").first
            link.click(timeout=8000)
            time.sleep(1.6)
            if "/catalog/" in pg.url or "/skills/" in pg.url:
                snap(pg, "skill-detail")
            else:
                print("  (no skill detail reached, url=", pg.url, ")")
        except Exception as e:
            print("  (skill-detail skipped:", type(e).__name__, ")")

        # wizard quiz/review (attempt first two actions)
        print("wizard-quiz/review")
        try:
            goto(pg, f"{STUDENT}/wizard", settle=1.0)
            pg.locator("button").first.click(timeout=6000)
            time.sleep(1.6)
            snap(pg, "wizard-quiz")
            pg.locator("button").first.click(timeout=6000)
            time.sleep(1.6)
            snap(pg, "wizard-review")
        except Exception as e:
            print("  (wizard interact skipped:", type(e).__name__, ")")

        pg.close()

        # ---------------- admin (:3001) ----------------
        pg = browser.new_page(viewport=VW)
        print("admin-login"); goto(pg, f"{ADMIN}/", settle=1.0); snap(pg, "admin-login")
        print("login admin")
        login(pg, ADMIN, "admin@skillsynth.io", "Admin@123456")
        snap(pg, "admin-dashboard")

        capture_range(pg, ADMIN, [
            ("admin-users", "/users"),
            ("admin-skills", "/skills"),
            ("admin-categories", "/categories"),
            ("admin-job-roles", "/job-roles"),
            ("admin-resources", "/resources"),
            ("admin-paths", "/paths"),
            ("admin-assessments", "/assessments"),
            ("admin-reports", "/reports"),
            ("admin-feature-flags", "/feature-flags"),
            ("admin-health", "/health"),
            ("admin-audit-logs", "/audit-logs"),
            ("admin-db-inspector", "/db-inspector"),
            ("admin-backups", "/backups"),
            ("admin-settings", "/settings"),
        ])

        pg.close()
        browser.close()
    print("DONE")


if __name__ == "__main__":
    main()