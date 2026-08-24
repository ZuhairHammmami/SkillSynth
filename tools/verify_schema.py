#!/usr/bin/env python3
"""verify_schema.py — Compare canonical DDL (003_reduced_schema.sql) against ORM metadata.

Builds two temp SQLite databases:
  (a) from src/migrations/003_reduced_schema.sql via executescript
  (b) from backend.entities via Base.metadata.create_all

Compares table sets, columns (name/type-affinity/notnull/default), PK columns,
FK tuples including ON DELETE action, explicit index names + column lists, and
UNIQUE-constraint column tuples per table. Prints "SCHEMA MATCH" and exits 0
on success; prints aligned diffs and exits 1 otherwise.
"""

import os
import sqlite3
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

from sqlalchemy import create_engine  # noqa: E402
from backend.database import Base  # noqa: E402
import backend.entities  # noqa: E402,F401

DDL_PATH = os.path.join(ROOT, "src", "migrations", "003_reduced_schema.sql")


def type_affinity(decl):
    """Map a declared SQL type to its SQLite affinity class (per the SQLite
    affinity rules); shared by both comparison sides so it never biases."""
    t = (decl or "").upper()
    if "INT" in t:
        return "INTEGER"
    if "CHAR" in t or "CLOB" in t or "TEXT" in t:
        return "TEXT"
    if not t or "BLOB" in t:
        return "BLOB"
    if "REAL" in t or "FLOA" in t or "DOUB" in t:
        return "REAL"
    return "NUMERIC"


def load_ddl_tables():
    """Build side A: an in-memory SQLite DB from the canonical DDL file."""
    with open(DDL_PATH, "r", encoding="utf-8") as f:
        script = f.read()
    conn = sqlite3.connect(":memory:")
    conn.executescript(script)
    return conn


def load_orm_tables():
    """Build side B: an in-memory SQLite DB from ORM create_all, so the gate
    fails whenever entities drift from the reviewed DDL."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    return engine.raw_connection()


def get_tables(conn):
    """Set of user-table names in a connection (sqlite_% internals excluded)."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {r[0] for r in rows}


def get_columns(conn, table):
    """{column: (affinity, notnull, default_str)} per PRAGMA table_info."""
    out = {}
    for _cid, name, ctype, notnull, dflt, _pk in conn.execute(f'PRAGMA table_info("{table}")'):
        out[name] = (type_affinity(ctype), bool(notnull), None if dflt is None else str(dflt))
    return out


def get_pk(conn, table):
    """Ordered PRIMARY KEY column names — order matters for composite keys."""
    cols = [(pk, name) for _c, name, _t, _nn, _d, pk in conn.execute(f'PRAGMA table_info("{table}")') if pk]
    return [name for _pk, name in sorted(cols)]


def get_fks(conn, table):
    """{(table, column, ref_table, ref_col, on_delete)} per FK.

    The ON DELETE action is part of the tuple so an ORM ondelete edit that is
    not mirrored in the canonical DDL (or vice versa) fails the gate.
    """
    fks = set()
    for row in conn.execute(f'PRAGMA foreign_key_list("{table}")'):
        ref_table, from_col, to_col, on_delete = row[2], row[3], row[4], row[6]
        fks.add((table, from_col, ref_table, to_col, on_delete))
    return fks


def get_indexes(conn, table):
    """{explicit_index_name: ordered_column_tuple} for developer-created
    indexes (origin 'c'); autoindexes carry no reviewable name and are
    covered semantically by get_uniques/get_pk instead."""
    out = {}
    for row in conn.execute(f'PRAGMA index_list("{table}")'):
        name, origin = row[1], row[3]
        if origin == 'c':
            cols = tuple(r[2] for r in conn.execute(f'PRAGMA index_info("{name}")'))
            out[name] = cols
    return out


def get_uniques(conn, table):
    """Set of column tuples enforced UNIQUE by constraint (autoindex origin
    'u') — closes the old gap where sqlite_autoindex_* names were skipped,
    letting UNIQUE constraints go uncompared."""

    out = set()
    for row in conn.execute(f'PRAGMA index_list("{table}")'):
        name, origin = row[1], row[3]
        if origin == 'u':
            cols = tuple(r[2] for r in conn.execute(f'PRAGMA index_info("{name}")'))
            out.add(cols)
    return out


def main():
    """Build both sides, diff every facet, print verdict; exit 0 on match."""
    ddl = load_ddl_tables()
    orm = load_orm_tables()

    failures = []
    tables_ddl, tables_orm = get_tables(ddl), get_tables(orm)

    if tables_ddl != tables_orm:
        failures.append(("table sets",
                         f"only-in-DDL={sorted(tables_ddl - tables_orm)}",
                         f"only-in-ORM={sorted(tables_orm - tables_ddl)}"))

    for table in sorted(tables_ddl & tables_orm):
        cols_ddl, cols_orm = get_columns(ddl, table), get_columns(orm, table)
        if cols_ddl != cols_orm:
            only_ddl = {k: v for k, v in cols_ddl.items() if k not in cols_orm}
            only_orm = {k: v for k, v in cols_orm.items() if k not in cols_ddl}
            changed = {
                k: (cols_ddl[k], cols_orm[k])
                for k in cols_ddl.keys() & cols_orm.keys() if cols_ddl[k] != cols_orm[k]
            }
            failures.append((f"{table}.columns",
                             f"ddl-only={only_ddl} changed={changed}",
                             f"orm-only={only_orm}"))
        pk_ddl, pk_orm = get_pk(ddl, table), get_pk(orm, table)
        if pk_ddl != pk_orm:
            failures.append((f"{table}.primary_key", f"ddl={pk_ddl}", f"orm={pk_orm}"))
        fk_ddl, fk_orm = get_fks(ddl, table), get_fks(orm, table)
        if fk_ddl != fk_orm:
            failures.append((f"{table}.foreign_keys",
                             f"ddl-only={sorted(fk_ddl - fk_orm)}",
                             f"orm-only={sorted(fk_orm - fk_ddl)}"))
        ix_ddl, ix_orm = get_indexes(ddl, table), get_indexes(orm, table)
        if ix_ddl != ix_orm:
            failures.append((f"{table}.indexes",
                             f"ddl-only={sorted(ix_ddl - ix_orm)}",
                             f"orm-only={sorted(ix_orm - ix_ddl)}"))
        uq_ddl, uq_orm = get_uniques(ddl, table), get_uniques(orm, table)
        if uq_ddl != uq_orm:
            failures.append((f"{table}.unique_constraints",
                             f"ddl-only={sorted(uq_ddl - uq_orm)}",
                             f"orm-only={sorted(uq_orm - uq_ddl)}"))

    ddl.close()
    orm.close()

    if failures:
        print("SCHEMA MISMATCH")
        width = max(len(name) for name, *_ in failures)
        for name, left, right in failures:
            print(f"\n  [{name}]".ljust(width + 4))
            print(f"    DDL: {left}")
            print(f"    ORM: {right}")
        print(f"\n{len(failures)} mismatch(es)")
        return 1

    print(f"SCHEMA MATCH ({len(tables_ddl)} tables compared)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
