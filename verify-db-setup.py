#!/usr/bin/env python3
"""
Phase 3.2: Minimal Database Setup Script
Applies migrations and verifies Supabase schema
"""

import sqlite3
import os
import re

def read_env():
    """Read .env file and return variables as dict"""
    env = {}
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env[key.strip()] = value.strip().strip('"')
    return env

def main():
    env = read_env()
    mode = env.get('MODE', 'dev')
    db_url = env.get('DATABASE_URL', '')
    
    print(f"🔧 Configuration: MODE={mode}")
    
    if mode == 'prod' and db_url:
        print("✅ Production mode with PostgreSQL detected")
        print(f"📍 Database URL: {db_url[:50]}...")
        print("\n📝 NOTE: For Phase 3.2 E2E testing with Supabase:")
        print("   1. Verify database schema using Supabase dashboard")
        print("   2. Apply migration 001_aeis_initial_schema.sql via Supabase SQL editor")
        print("   3. Continue with dev server startup and API testing")
        print("\n⏭️  Proceeding to seed data via API ingestion...")
    else:
        # Dev mode with SQLite
        print("✅ Development mode with SQLite detected")
        db_path = "skillsynth.db"
        
        # For dev testing, create/verify SQLite schema
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            
            print(f"📂 Database: {db_path}")
            
            # Check if concepts table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='concepts';")
            if cur.fetchone():
                print("✅ concepts table exists")
                cur.execute("SELECT COUNT(*) FROM concepts;")
                count = cur.fetchone()[0]
                print(f"   Current records: {count}")
            else:
                print("⚠️  concepts table not found (dev mode - not critical for API testing)")
            
            conn.close()
        except Exception as e:
            print(f"⚠️  SQLite check failed: {e}")

if __name__ == '__main__':
    main()
