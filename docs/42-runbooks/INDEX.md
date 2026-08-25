# SS-EDS: Runbooks

## Purpose
Document operational runbooks for common tasks and incident response procedures for SkillSynth. Covers environment setup, troubleshooting, recovery, and maintenance operations.

## Responsibilities
- Provide step-by-step operational procedures
- Document incident response playbooks
- Cover common troubleshooting scenarios
- Maintain recovery procedures for worst-case scenarios

## Inputs
- Operational incidents
- Development team experience
- Deployment configurations

## Outputs
- Environment setup runbook
- Incident response playbooks
- Recovery procedures
- Maintenance checklists

## Dependencies
- 17-deployment (deployment procedures)
- 18-monitoring (alert response)
- 34-error-handling (error recovery)

## Sequence: Incident Response
```
Alert → Acknowledge → Assess Severity → Triage → Investigate → Fix → Verify → Post-Mortem
```

## Runbook: Fresh Development Setup
```bash
# 1. Backend setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit as needed

# 2. Database
python seed_all.py

# 3. Frontend setup
cd src/frontend
pnpm install
cp .env.local.example .env.local  # Edit as needed

# 4. Start services
python run.py  # Terminal 1: Backend :8000
pnpm dev       # Terminal 2: Frontend :3000
```

## Runbook: Database Reset
```bash
# 1. Delete existing DB
rm skillsynth.db

# 2. Re-seed
python seed_all.py

# 3. Verify
python run.py  # Check startup logs
```

## Runbook: Admin Account Recovery
```bash
# Method 1: Auto-create at startup
export ADMIN_EMAIL=admin@skillsynth.io
export ADMIN_PASSWORD=NewAdmin@123456
python run.py  # Admin created if not exists

# Method 2: Standalone script
python src/backend/create_admin.py
```

## ERD References
- No runbook-specific database tables

## Rules
1. Runbooks must be step-by-step and copy-paste ready
2. Include expected outputs for verification
3. Document rollback steps for each procedure
4. Runbooks should be tested quarterly
5. Incident response playbooks include severity definitions

## Examples
- "Backend won't start" runbook: check Python version, check requirements, check port, check env vars
- "Database corrupted" runbook: delete db file, re-seed, verify

## Edge Cases
- Runbook command fails due to environment differences → document variations
- Multiple runbooks applicable → priority order
- Runbook itself has a bug → fix and update

## Failure Cases
- Runbook not followed correctly → incorrect outcome
- Runbook outdated after system change → misleading instructions
- Runbook missing for critical operation → incident response delayed

## Recovery Procedures
1. Update runbook after any system change
2. Test runbook in staging before using in production
3. Review runbooks quarterly for accuracy

## Refactoring Strategy
- Convert runbooks to automated scripts where possible
- Add runbook verification automation
- Create runbook management system with version control
- Link runbooks to monitoring alerts for automatic response
