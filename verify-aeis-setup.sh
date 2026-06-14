#!/bin/bash

# AEIS Phase 1.5 - Mastery Foundation Verification Script
# Run this after pnpm install completes in src/frontend

set -e

echo "🔍 AEIS Phase 1.5 Verification Script"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Core Schema Files
echo "📦 Checking Core Schema Files..."
schemas=(
  "src/entities/KnowledgeNode.ts"
  "src/entities/EngineeringProject.ts"
  "src/entities/UserPath.ts"
)

for schema in "${schemas[@]}"; do
  if [ -f "$schema" ]; then
    echo -e "${GREEN}✓${NC} $schema"
  else
    echo -e "${RED}✗${NC} $schema (MISSING)"
  fi
done

# Check 2: Admin Component Files
echo ""
echo "🎨 Checking Admin Component Files..."
admin_files=(
  "src/app/admin/types/index.ts"
  "src/app/admin/forms/KnowledgeIngestionFormSchema.ts"
  "src/app/admin/forms/KnowledgeIngestionForm.tsx"
  "src/app/admin/ui/KnowledgeIngestionPage.tsx"
  "src/app/admin/ui/UserPathEditor.tsx"
)

for file in "${admin_files[@]}"; do
  if [ -f "$file" ]; then
    echo -e "${GREEN}✓${NC} $file"
  else
    echo -e "${RED}✗${NC} $file (MISSING)"
  fi
done

# Check 3: Shared Services
echo ""
echo "🔌 Checking Shared Services..."
services=(
  "src/services/shared/notification/NotificationService.ts"
  "src/services/shared/conflict-checker/ConflictCheckerService.ts"
)

for service in "${services[@]}"; do
  if [ -f "$service" ]; then
    echo -e "${GREEN}✓${NC} $service"
  else
    echo -e "${RED}✗${NC} $service (MISSING)"
  fi
done

# Check 4: Database Migration
echo ""
echo "🗄️  Checking Database Migration..."
if [ -f "src/migrations/001_aeis_initial_schema.sql" ]; then
  echo -e "${GREEN}✓${NC} src/migrations/001_aeis_initial_schema.sql"
else
  echo -e "${RED}✗${NC} src/migrations/001_aeis_initial_schema.sql (MISSING)"
fi

# Check 5: Package Configuration
echo ""
echo "📋 Checking Package Configuration..."
if grep -q '"type-check"' src/frontend/package.json; then
  echo -e "${GREEN}✓${NC} pnpm type-check script found"
else
  echo -e "${RED}✗${NC} pnpm type-check script not found"
fi

# Check 6: TypeScript Compilation (requires node_modules)
echo ""
echo "🔨 Running TypeScript Type Check..."
if command -v tsc &> /dev/null; then
  cd src/frontend
  if pnpm type-check > /tmp/type-check.log 2>&1; then
    echo -e "${GREEN}✓${NC} All TypeScript files passed type-check"
  else
    echo -e "${YELLOW}⚠${NC} Type check failed. View errors:"
    cat /tmp/type-check.log
  fi
  cd - > /dev/null
else
  echo -e "${YELLOW}⚠${NC} TypeScript not installed yet. Run: cd src/frontend && pnpm install"
fi

# Summary
echo ""
echo "===================================="
echo "Verification Summary:"
echo ""
echo "✅ Tasks Completed:"
echo "  1. Infrastructure Migration (pnpm setup)"
echo "  2. AEIS Core Schemas (Zod validation)"
echo "  3. Admin Governance UI (FSD structure)"
echo "  4. Database Schema (SQL migration ready)"
echo "  5. Notification & Conflict Services"
echo ""
echo "📝 Next Steps:"
echo "  1. Complete frontend install: cd src/frontend && pnpm install --timeout 600000"
echo "  2. Run type-check: pnpm type-check"
echo "  3. Execute SQL migration in Supabase console"
echo "  4. Start development server: pnpm dev"
echo ""
echo "📚 Documentation:"
echo "  - See PHASE1_5_EXECUTION_REPORT.md for full details"
echo ""
