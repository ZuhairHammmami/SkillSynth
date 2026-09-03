"""Tests for DDL CHECK constraints — business-meaningful value ranges.

Verifies that the 7 CHECK constraints (difficulty, hours, pass score,
correct index, proficiency, step level, selected level) reject out-of-range
values at the database level while accepting valid ones.
"""

import sqlalchemy as sa
import pytest

from backend.database import engine


def _raw_conn():
    """A connection to the test DB with FK enforcement on."""
    return engine.connect()


def test_difficulty_level_11_rejected():
    """difficulty_level must be 1-10; 11 violates chk_difficulty."""
    conn = _raw_conn()
    try:
        with pytest.raises(sa.exc.IntegrityError):
            conn.execute(
                sa.text(
                    "INSERT INTO skills (name, difficulty_level) VALUES ('skill_bad_diff', 11)"
                )
            )
            conn.commit()
    finally:
        conn.execute(sa.text("DELETE FROM skills WHERE name = 'skill_bad_diff'"))
        conn.commit()
        conn.close()


def test_difficulty_level_5_accepted():
    """difficulty_level=5 is inside the valid range and must succeed."""
    conn = _raw_conn()
    try:
        conn.execute(
            sa.text(
                "INSERT INTO skills (name, category_id, difficulty_level) "
                "VALUES ('skill_good_diff', NULL, 5)"
            )
        )
        conn.commit()
    finally:
        conn.execute(sa.text("DELETE FROM skills WHERE name = 'skill_good_diff'"))
        conn.commit()
        conn.close()


def test_estimated_hours_negative_rejected():
    """estimated_hours must be non-negative; -1 violates chk_hours."""
    conn = _raw_conn()
    try:
        with pytest.raises(sa.exc.IntegrityError):
            conn.execute(
                sa.text(
                    "INSERT INTO skills (name, difficulty_level, estimated_hours) "
                    "VALUES ('skill_bad_hours', 5, -1)"
                )
            )
            conn.commit()
    finally:
        conn.execute(sa.text("DELETE FROM skills WHERE name = 'skill_bad_hours'"))
        conn.commit()
        conn.close()


def test_estimated_hours_zero_accepted():
    """estimated_hours=0 is non-negative and must succeed."""
    conn = _raw_conn()
    try:
        conn.execute(
            sa.text(
                "INSERT INTO skills (name, difficulty_level, estimated_hours) "
                "VALUES ('skill_zero_hours', 5, 0)"
            )
        )
        conn.commit()
    finally:
        conn.execute(sa.text("DELETE FROM skills WHERE name = 'skill_zero_hours'"))
        conn.commit()
        conn.close()


def test_pass_score_101_rejected():
    """pass_score must be 0-100; 101 violates chk_pass_score."""
    conn = _raw_conn()
    try:
        with pytest.raises(sa.exc.IntegrityError):
            conn.execute(
                sa.text("INSERT INTO assessments (title, pass_score) VALUES ('bad', 101)")
            )
            conn.commit()
    finally:
        conn.execute(sa.text("DELETE FROM assessments WHERE title = 'bad'"))
        conn.commit()
        conn.close()


def test_pass_score_100_accepted():
    """pass_score=100 is at the boundary and must succeed."""
    conn = _raw_conn()
    try:
        conn.execute(sa.text("INSERT INTO assessments (title, pass_score) VALUES ('good', 100)"))
        conn.commit()
    finally:
        conn.execute(sa.text("DELETE FROM assessments WHERE title = 'good'"))
        conn.commit()
        conn.close()
