"""Schema integrity tests — 15 tables, FK gate, unique constraints, counts."""

import os
import sqlite3

import pytest

TEST_DB = os.environ.get("SKILLSYNTH_TEST_DB_PATH")

EXPECTED_TABLES = {
    "activity_log", "assessment_questions", "assessment_results", "assessments",
    "categories", "job_role_skills", "job_roles", "path_steps", "paths",
    "resources", "skill_prerequisites", "skills", "step_progress",
    "user_skills", "users",
}


@pytest.fixture
def conn():
    connection = sqlite3.connect(TEST_DB)
    connection.execute("PRAGMA foreign_keys=ON")
    yield connection
    connection.close()


def _unique_columns(conn, table):
    """Set of column tuples enforced UNIQUE (autoindex origin 'u')."""
    unique = set()
    for row in conn.execute(f'PRAGMA index_list("{table}")'):
        name, origin = row[1], row[3]
        if origin == "u":
            cols = tuple(r[2] for r in conn.execute(f'PRAGMA index_info("{name}")'))
            unique.add(cols)
    return unique


class TestSchema:

    def test_15_tables_exist(self, conn):
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        assert {r[0] for r in rows} == EXPECTED_TABLES

    def test_no_alembic_version(self, conn):
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE name='alembic_version'"
        ).fetchone()
        assert row is None

    def test_foreign_key_check_clean(self, conn):
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        assert violations == []

    def test_unique_constraints(self, conn):
        assert ("email",) in _unique_columns(conn, "users")
        assert ("name",) in _unique_columns(conn, "categories")
        assert ("name",) in _unique_columns(conn, "skills")
        assert ("title",) in _unique_columns(conn, "job_roles")

    def test_stable_catalog_counts(self, conn):
        expected = {
            "categories": 16, "skills": 152, "job_roles": 25,
            "job_role_skills": 301, "resources": 144,
            "assessments": 152, "assessment_questions": 613,
            "skill_prerequisites": 269,
        }
        for table, count in expected.items():
            actual = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            assert actual == count, f"{table}: expected {count}, got {actual}"

    def test_seed_users_present(self, conn):
        emails = {r[0] for r in conn.execute("SELECT email FROM users")}
        assert {
            "admin@skillsynth.io", "veteran@skillsynth.io", "demo@demo.com",
            "editor@skillsynth.io", "student2@skillsynth.io",
        } <= emails

    def test_admin_is_admin(self, conn):
        row = conn.execute(
            "SELECT is_admin FROM users WHERE email='admin@skillsynth.io'"
        ).fetchone()
        assert row is not None and row[0] == 1
