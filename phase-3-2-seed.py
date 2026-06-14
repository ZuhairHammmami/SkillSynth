#!/usr/bin/env python3
"""
Phase 3.2: Database Population Script
Connects to Supabase and seeds the concepts table with Frontend Engineering Path data
"""

import os
import sys
import json
import uuid
from pathlib import Path

# Add src directory to path for imports
PROJECT_ROOT = Path(__file__).parent
SYS_PATH_ADDITIONS = [
    str(PROJECT_ROOT / 'src'),
    str(PROJECT_ROOT),
]
for path in SYS_PATH_ADDITIONS:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import necessary modules
try:
    from sqlalchemy import create_engine, text, inspect
    from sqlalchemy.pool import StaticPool
    print("✅ SQLAlchemy imported successfully")
except ImportError as e:
    print(f"❌ Failed to import SQLAlchemy: {e}")
    sys.exit(1)

# Load environment from .env file
env_file = PROJECT_ROOT / '.env'
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"')

DATABASE_URL = os.getenv("DATABASE_URL")
MODE = os.getenv("MODE", "dev")

print(f"🔧 Configuration: MODE={MODE}")

if not DATABASE_URL:
    print("❌ DATABASE_URL not set in .env")
    sys.exit(1)

if "postgresql" not in DATABASE_URL:
    print("❌ DATABASE_URL is not a PostgreSQL connection")
    sys.exit(1)

print(f"🔗 Connecting to Supabase...")

# Create engine with SSL
try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        connect_args={"timeout": 10}
    )
    print("✅ Engine created")
except Exception as e:
    print(f"❌ Failed to create engine: {e}")
    sys.exit(1)

# Test connection
try:
    with engine.connect() as conn:
        print("✅ Connected to database")
        
        # Check if concepts table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Database Status:")
        print(f"   Available tables: {len(tables)}")
        
        if 'concepts' in tables:
            print("   ✅ concepts table exists")
            result = conn.execute(text("SELECT COUNT(*) as count FROM concepts;"))
            count = result.scalar()
            print(f"      Current records: {count}")
        else:
            print("   ❌ concepts table NOT found")
            print("\n📝 Applying migration...")
            
            # Read and execute migration
            migration_file = PROJECT_ROOT / 'src' / 'migrations' / '001_aeis_initial_schema.sql'
            if not migration_file.exists():
                print(f"❌ Migration file not found: {migration_file}")
                sys.exit(1)
            
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            # Split by semicolon and execute
            for statement in migration_sql.split(';'):
                statement = statement.strip()
                if statement:
                    conn.execute(text(statement))
            
            conn.commit()
            print("   ✅ Migration applied")
        
except Exception as e:
    print(f"❌ Connection error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Seed data
SEED_DATA = {
    "nodes": [
        {
            "label": "JavaScript Basics",
            "confidenceScore": 0.95,
            "sourceType": "academic",
            "sourceUrl": "https://javascript.info/",
            "reliabilityScore": 0.95,
            "prerequisites": []
        },
        {
            "label": "React Fundamentals",
            "confidenceScore": 0.88,
            "sourceType": "market",
            "sourceUrl": "https://react.dev/learn",
            "reliabilityScore": 0.92,
            "prerequisites": [0]  # Depends on Node 1
        },
        {
            "label": "State Management (Zustand/Redux)",
            "confidenceScore": 0.82,
            "sourceType": "market",
            "sourceUrl": "https://redux.js.org/",
            "reliabilityScore": 0.88,
            "prerequisites": [1]  # Depends on Node 2
        },
        {
            "label": "Advanced Patterns (HOC/Compound)",
            "confidenceScore": 0.75,
            "sourceType": "academic",
            "sourceUrl": "https://react.dev/learn/passing-props-to-a-component",
            "reliabilityScore": 0.85,
            "prerequisites": [1, 2]  # Depends on Node 2 and Node 3
        }
    ]
}

# Insert data
print("\n📥 Seeding Frontend Engineering Path...")

try:
    with engine.begin() as conn:
        # Clear existing data for clean seed
        print("   Clearing existing concepts...")
        conn.execute(text("DELETE FROM concept_prerequisites;"))
        conn.execute(text("DELETE FROM concepts;"))
        
        node_ids = []
        
        # Insert nodes
        for i, node in enumerate(SEED_DATA["nodes"]):
            result = conn.execute(
                text("""
                    INSERT INTO concepts (label, confidence_score, source_type, source_url, reliability_score)
                    VALUES (:label, :confidence_score, :source_type, :source_url, :reliability_score)
                    RETURNING id;
                """),
                {
                    "label": node["label"],
                    "confidence_score": node["confidenceScore"],
                    "source_type": node["sourceType"],
                    "source_url": node["sourceUrl"],
                    "reliability_score": node["reliabilityScore"]
                }
            )
            node_id = result.scalar()
            node_ids.append(node_id)
            print(f"   ✅ Node {i + 1}: \"{node['label']}\" (Confidence: {node['confidenceScore']})")
        
        # Insert prerequisites
        print("\n🔗 Adding prerequisite relationships...")
        for i, node in enumerate(SEED_DATA["nodes"]):
            for prereq_idx in node["prerequisites"]:
                conn.execute(
                    text("""
                        INSERT INTO concept_prerequisites (concept_id, prerequisite_id)
                        VALUES (:concept_id, :prerequisite_id);
                    """),
                    {
                        "concept_id": node_ids[i],
                        "prerequisite_id": node_ids[prereq_idx]
                    }
                )
                print(f"   ✅ {node['label']} ← {SEED_DATA['nodes'][prereq_idx]['label']}")
        
        print("\n✅ Seed data inserted successfully")
        
except Exception as e:
    print(f"❌ Error during seeding: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Verify
print("\n📊 Verification:")
try:
    with engine.connect() as conn:
        # Count concepts
        result = conn.execute(text("SELECT COUNT(*) as count FROM concepts;"))
        count = result.scalar()
        print(f"   Total concepts: {count}")
        
        # Count prerequisites
        result = conn.execute(text("SELECT COUNT(*) as count FROM concept_prerequisites;"))
        prereq_count = result.scalar()
        print(f"   Total prerequisites: {prereq_count}")
        
        # Show inserted data
        print("\n🎯 Inserted Nodes:")
        result = conn.execute(text("""
            SELECT id, label, confidence_score, source_type 
            FROM concepts 
            ORDER BY created_at;
        """))
        
        for row in result.fetchall():
            node_id = str(row[0])[:8]
            label = row[1]
            confidence = row[2]
            source = row[3]
            print(f"   - {label} (ID: {node_id}..., Confidence: {confidence}, Source: {source})")
        
except Exception as e:
    print(f"❌ Error during verification: {e}")
    sys.exit(1)

print("\n✅ Phase 3.2 Task 1 Complete: Database Population Verified")
