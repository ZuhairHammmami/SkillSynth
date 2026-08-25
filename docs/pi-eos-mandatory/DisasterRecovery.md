# Disaster Recovery

## Recovery Tiers
| Tier | RTO | RPO | Scenario |
|------|-----|-----|----------|
| 1 | <5 min | <1 min | Application crash, process restart |
| 2 | <15 min | <5 min | Database corruption, file deletion |
| 3 | <1 hour | <24 hour | Full instance loss, environment rebuild |

## Recovery Procedures

### Tier 1: Application Restart
```bash
# Backend crash
python run.py  # auto-reload in dev, gunicorn restart in prod

# Frontend crash
cd src/frontend && pnpm dev  # Next.js auto-restart
```

### Tier 2: Database Recovery
```bash
# SQLite (dev)
# 1. Check if skillsynth.db exists and is valid
sqlite3 skillsynth.db "PRAGMA integrity_check;"
# 2. Restore from backup
cp skillsynth.db.backup_v35 skillsynth.db
# 3. Re-seed if backup is stale
python seed_v2.py

# PostgreSQL (prod)
# 1. Check Supabase dashboard for health
# 2. Restore from latest backup in Supabase
# 3. Run Alembic migrations
alembic upgrade head
```

### Tier 3: Full Rebuild
```bash
git clone <repo>
cd SkillSynth
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd src/frontend && pnpm install
python seed_v2.py  # initial seed
alembic upgrade head  # if migrations exist
```

## Prevention
- WAL mode for SQLite (journaling)
- Regular DB backups via cron
- All critical config in environment variables (not code)
- Git for all code changes (rollback via git revert)
