# CRUD Input Validation & Skill Listing Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the skills page not showing newly created skills, and harden all admin CRUD operations to reject invalid/malicious input at the DTO layer — 17 validation gaps across 6 entity types.

**Architecture:** Two-pronged fix. (1) Frontend: ensure the skills page `$effect` re-fetches on every mount and SSE events invalidate skills cache. (2) Backend: wire existing-but-unused validators (`_self_or_clean_hex`, `_check_positive`) into DTOs, add `_sanitize()` to all text fields that currently lack it, and add missing validators to Update DTOs that their Create counterparts already have.

**Tech Stack:** Python 3 / Pydantic v2 (backend DTOs), Svelte 5 / SvelteKit (admin frontend)

**Spec:** N/A — this is a bugfix + hardening task based on codebase audit. Reference: `src/backend/dto/catalog.py`, `src/backend/dto/admin.py`, `src/admin-app/src/routes/(app)/skills/+page.svelte`

## Global Constraints

- No file > 300 lines; no function > 40 lines
- Every function carries a docstring stating its single purpose and its caller/callee relationships
- Backend Python imports use `from backend import X`
- Frontend uses pnpm, working dir is `cd src/admin-app`
- No comments unless asked; no emojis
- Follow existing code patterns exactly (validators return i18n dot-keys on frontend, raise ValueError on backend)
- All 305 existing tests must continue passing after each task

---

## Task 1: Fix Skills Page — New Skills Not Appearing

**Root cause analysis:**
1. `$effect(() => { load(); })` in `skills/+page.svelte` has no reactive dependencies — runs once on mount. SvelteKit client-side navigation should destroy/recreate the component, but the 30s query cache may serve stale data on fast re-navigation.
2. SSE bus (`stores/sse.ts`) only invalidates `PATHS` and `ASMT` cache keys — `skill_created`, `skill_updated`, `skill_deleted` events are NOT forwarded, so cross-tab/cross-user freshness is impossible.

**Files:**
- Modify: `src/admin-app/src/routes/(app)/skills/+page.svelte:62`
- Modify: `src/admin-app/src/routes/(app)/categories/+page.svelte:45`
- Modify: `src/admin-app/src/routes/(app)/resources/+page.svelte:59`
- Modify: `src/admin-app/src/routes/(app)/users/+page.svelte:53`
- Modify: `src/admin-app/src/routes/(app)/job-roles/+page.svelte` (find `$effect` line)
- Modify: `src/admin-app/src/routes/(app)/assessments/+page.svelte` (find `$effect` line)
- Modify: `src/admin-app/src/lib/stores/sse.ts:17-21`

**Interfaces:**
- Consumes: `query()`, `invalidate()` from `$lib/query`
- Produces: All CRUD pages refetch on every mount; SSE events invalidate entity caches

- [ ] **Step 1: Replace `$effect` with `onMount` on all CRUD pages**

Replace the `$effect(() => { load(); })` pattern with Svelte's `onMount` to guarantee `load()` runs on every component mount regardless of SvelteKit's effect scheduling.

On `skills/+page.svelte`, change:
```typescript
// BEFORE (line 62)
$effect(() => { load(); });

// AFTER
import { onMount } from 'svelte';
onMount(() => { load(); });
```

Repeat the same change on all 6 CRUD pages: `categories`, `resources`, `users`, `job-roles`, `assessments`.

- [ ] **Step 2: Add skills cache invalidation to SSE handler**

In `src/admin-app/src/lib/stores/sse.ts`, extend `onFrame()` to invalidate entity caches on mutation events:

```typescript
function onFrame(type: string, data: any): void {
  if (type === 'path_generated') invalidate(['PATHS']);
  if (type === 'assessment_completed') invalidate(['ASMT']);
  if (type === 'skill_created' || type === 'skill_updated' || type === 'skill_deleted') {
    invalidate(['SKILLS']);
    invalidate(['CATS_PICK']);
    invalidate(['SKILLS_PICK']);
  }
  if (type === 'category_created' || type === 'category_updated' || type === 'category_deleted') {
    invalidate(['CATS']);
    invalidate(['CATS_PICK']);
  }
  if (type === 'resource_created' || type === 'resource_updated' || type === 'resource_deleted') {
    invalidate(['RESOURCES']);
  }
  if (type === 'user_created' || type === 'user_updated' || type === 'user_deleted') {
    invalidate(['USERS']);
  }
  if (browser) window.dispatchEvent(new CustomEvent('sse:' + type, { detail: data }));
}
```

- [ ] **Step 3: Verify frontend builds and typechecks**

Run: `cd src/admin-app && pnpm check && pnpm build`
Expected: 0 errors, 0 warnings, clean build

- [ ] **Step 4: Commit**

```bash
git add src/admin-app/src/routes/(app)/skills/+page.svelte \
        src/admin-app/src/routes/(app)/categories/+page.svelte \
        src/admin-app/src/routes/(app)/resources/+page.svelte \
        src/admin-app/src/routes/(app)/users/+page.svelte \
        src/admin-app/src/routes/(app)/job-roles/+page.svelte \
        src/admin-app/src/routes/(app)/assessments/+page.svelte \
        src/admin-app/src/lib/stores/sse.ts
git commit -m "fix(admin): ensure CRUD pages refetch on mount + SSE invalidates entity caches"
```

---

## Task 2: Wire Existing Validators + Add Sanitizers to Skill DTOs

**Files:**
- Modify: `src/backend/dto/catalog.py:82-138` (SkillCreate, SkillUpdate)
- Modify: `src/admin-app/src/routes/(app)/skills/+page.svelte` (add icon validator)

**Interfaces:**
- Consumes: `_self_or_clean_hex()` (line 27), `_sanitize()` (line 16) — both already defined
- Produces: `SkillCreate.color` validated as hex; `SkillCreate/SkillUpdate.icon` max 100 chars + sanitized; `SkillCreate/SkillUpdate.description` sanitized

- [ ] **Step 1: Add `@field_validator("color")` to SkillCreate and SkillUpdate**

In `src/backend/dto/catalog.py`, add to `SkillCreate` (after line 103):

```python
@field_validator("color")
@classmethod
def validate_color(cls, v: Optional[str]) -> Optional[str]:
    """Validate hex color format when provided."""
    return _self_or_clean_hex(v)
```

Add to `SkillUpdate` (after line 138):

```python
@field_validator("color")
@classmethod
def validate_color(cls, v: Optional[str]) -> Optional[str]:
    """Validate hex color format when provided."""
    return _self_or_clean_hex(v)
```

- [ ] **Step 2: Add `icon` validation to SkillCreate and SkillUpdate**

Add `max_length=100` to the `icon` field on both DTOs, and add a sanitizer:

```python
# SkillCreate (line 93): change from
icon: Optional[str] = None
# to
icon: Optional[str] = Field(None, max_length=100)

# SkillUpdate (line 129): same change
icon: Optional[str] = Field(None, max_length=100)
```

Add `@field_validator("icon")` to both classes:

```python
@field_validator("icon")
@classmethod
def sanitize_icon(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from icon string."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None
```

- [ ] **Step 3: Add `@field_validator("description")` sanitizers to SkillCreate and SkillUpdate**

```python
# In SkillCreate (after the name validator):
@field_validator("description")
@classmethod
def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from description text."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None

# In SkillUpdate (after the name validator):
@field_validator("description")
@classmethod
def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from description text."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None
```

- [ ] **Step 4: Wire `_check_positive` into SkillCreate/SkillUpdate prerequisite_ids**

Add to `SkillCreate` (after existing validators):

```python
@field_validator("prerequisite_ids")
@classmethod
def validate_prereq_ids(cls, v: list[int]) -> list[int]:
    """Require positive integers for prerequisite IDs."""
    return _check_positive(v)
```

Add to `SkillUpdate`:

```python
@field_validator("prerequisite_ids")
@classmethod
def validate_prereq_ids(cls, v: Optional[list[int]]) -> Optional[list[int]]:
    """Require positive integers for prerequisite IDs."""
    return _check_positive(v) if v is not None else v
```

- [ ] **Step 5: Add frontend icon validator on skills page**

In `src/admin-app/src/routes/(app)/skills/+page.svelte`, add a new derived for icon validation:

```typescript
import { name, maxLength, range, nonNegative, positiveInt, hexColor } from '$lib/validation';
// Add maxLength import is already there

// Add after line 39 (colorErr):
const iconErr = $derived(maxLength(String(form.icon ?? ''), 100));
const iconKey = $derived((form.icon ?? '') ? iconErr : null);

// Update dialogValid (line 47):
const dialogValid = $derived(nameErr === null && descErr === null && diffErr === null && hoursErr === null && colorErr === null && iconErr === null && catErr === null);
```

Update the icon Field error binding (line 159):

```svelte
<Field label={t('admin.skills.icon')} error={iconKey ? t(iconKey, { field: t('admin.skills.icon'), max: 100 }) : formErrors.icon}>
```

- [ ] **Step 6: Run tests**

Run: `PYTHONPATH=src python -m pytest tests/test_catalog.py tests/test_catalog_integrity.py tests/test_validation_errors.py -v`
Expected: all pass (may need to update existing tests that send `difficulty_level: 7` which is outside DTO range 1-5 — see note)

Note: `test_put_skill_happy` (test_catalog.py:105) sends `difficulty_level: 7` which violates the DTO's `ge=1, le=5`. This is a pre-existing bug in the test. Fix by changing to a value in [1,5]:

```python
# test_catalog.py line 105: change "difficulty_level": 7 to "difficulty_level": 3
```

- [ ] **Step 7: Commit**

```bash
git add src/backend/dto/catalog.py \
        src/admin-app/src/routes/(app)/skills/+page.svelte \
        tests/test_catalog.py
git commit -m "fix(backend): wire color/icon/description validators + prerequisite_ids check on Skill DTOs"
```

---

## Task 3: Add Sanitizers to Category, Resource, and Job Role DTOs

**Files:**
- Modify: `src/backend/dto/catalog.py` (CategoryCreate, CategoryUpdate, ResourceCreate, ResourceUpdate, JobRoleCreate, JobRoleUpdate)

**Interfaces:**
- Consumes: `_sanitize()` (line 16), `_check_positive()` (line 39)
- Produces: All text fields sanitized; ResourceUpdate gets title+URL validators; JobRoleUpdate gets skill_ids validator

- [ ] **Step 1: Add description sanitizer to CategoryCreate and CategoryUpdate**

```python
# In CategoryCreate (after line 58):
@field_validator("description")
@classmethod
def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from description text."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None

# In CategoryUpdate (after line 79):
@field_validator("description")
@classmethod
def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from description text."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None
```

- [ ] **Step 2: Fix ResourceUpdate — add missing title sanitizer and URL validator**

`ResourceUpdate` (lines 175-185) is missing the validators that `ResourceCreate` has. Add:

```python
class ResourceUpdate(BaseModel):
    """PUT /admin/resources/{id} body; None fields left untouched."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = Field(None, max_length=2000)
    type: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    is_free: Optional[bool] = None
    is_official: Optional[bool] = None
    author_or_platform: Optional[str] = Field(None, max_length=200)
    skill_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        """Strip markup when a new value is supplied."""
        return _sanitize(v) if v is not None else v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Require http(s) scheme on resource URLs."""
        if v is None:
            return None
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v
```

- [ ] **Step 3: Add type and language sanitizers to ResourceCreate and ResourceUpdate**

```python
# In ResourceCreate (after the url validator):
@field_validator("type")
@classmethod
def sanitize_type(cls, v: str) -> str:
    """Strip and lowercase resource type."""
    return v.strip().lower()

@field_validator("language")
@classmethod
def sanitize_language(cls, v: Optional[str]) -> Optional[str]:
    """Strip and lowercase language code."""
    if v is None:
        return None
    return v.strip().lower()

@field_validator("author_or_platform")
@classmethod
def sanitize_author(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from author field."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None
```

Same validators on `ResourceUpdate`.

- [ ] **Step 4: Add description and career_field sanitizers to JobRoleCreate and JobRoleUpdate**

```python
# In JobRoleCreate (after the skill_ids validator):
@field_validator("description")
@classmethod
def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from description text."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None

@field_validator("career_field")
@classmethod
def sanitize_career_field(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from career field."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None
```

Same validators on `JobRoleUpdate`.

- [ ] **Step 5: Add `validate_skill_ids` to JobRoleUpdate**

```python
# In JobRoleUpdate (after the title validator):
@field_validator("skill_ids")
@classmethod
def validate_skill_ids(cls, v: Optional[list]) -> Optional[list]:
    """Require positive-int skill ids (dicts or ints)."""
    if v is not None:
        for item in v:
            sid = item.get("skill_id") if isinstance(item, dict) else item
            if sid is not None and (not isinstance(sid, int) or sid < 1):
                raise ValueError("Skill IDs must be positive integers")
    return v
```

- [ ] **Step 6: Run tests**

Run: `PYTHONPATH=src python -m pytest tests/test_catalog.py tests/test_catalog_integrity.py tests/test_catalog_router.py tests/test_catalog_service.py -v`
Expected: all pass

- [ ] **Step 7: Commit**

```bash
git add src/backend/dto/catalog.py
git commit -m "fix(backend): sanitize all text fields + wire missing validators on Category/Resource/JobRole DTOs"
```

---

## Task 4: Secure Admin User and Assessment DTOs

**Files:**
- Modify: `src/backend/dto/admin.py` (AdminCreateUser, AdminUserUpdate, AssessmentCreate, AssessmentUpdate, QuestionCreate, QuestionUpdate)

**Interfaces:**
- Consumes: `_sanitize()` (line 20 of admin.py), `PasswordValidator.sanitize_name()` from `dto/auth.py`
- Produces: `full_name` sanitized; `description` sanitized; question `options` sanitized and length-capped

- [ ] **Step 1: Add full_name sanitizer to AdminCreateUser and AdminUserUpdate**

The public registration (`RegisterInput`) and self-update (`ProfileUpdate`) already use `PasswordValidator.sanitize_name()`. Apply the same to admin DTOs:

```python
# In AdminCreateUser (after line 40):
@field_validator("full_name")
@classmethod
def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from full name."""
    if v is None:
        return None
    return PasswordValidator.sanitize_name(v)

# In AdminUserUpdate (after line 55):
@field_validator("full_name")
@classmethod
def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from full name."""
    if v is None:
        return None
    return PasswordValidator.sanitize_name(v)
```

- [ ] **Step 2: Add description sanitizer to AssessmentCreate and AssessmentUpdate**

```python
# In AssessmentCreate (after the title validator):
@field_validator("description")
@classmethod
def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from description text."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None

# In AssessmentUpdate (after the title validator):
@field_validator("description")
@classmethod
def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
    """Strip markup from description text."""
    if v is None:
        return None
    v = v.strip()
    return _sanitize(v) if v else None
```

- [ ] **Step 3: Sanitize and length-cap question options on QuestionCreate and QuestionUpdate**

```python
# In QuestionCreate (after the prompt validator):
@field_validator("options")
@classmethod
def sanitize_options(cls, v: List[str]) -> List[str]:
    """Strip, sanitize, and enforce max length on each option string."""
    if not v or len(v) < 2:
        raise ValueError("At least 2 options are required")
    cleaned = []
    for opt in v:
        opt = opt.strip()
        if not opt:
            raise ValueError("Options must not be empty strings")
        if len(opt) > 500:
            raise ValueError("Each option must be 500 characters or fewer")
        cleaned.append(_sanitize(opt))
    return cleaned

# In QuestionUpdate (after the prompt validator):
@field_validator("options")
@classmethod
def sanitize_options(cls, v: Optional[List[str]]) -> Optional[List[str]]:
    """Strip, sanitize, and enforce max length on each option string."""
    if v is None:
        return None
    if len(v) < 2:
        raise ValueError("At least 2 options are required")
    cleaned = []
    for opt in v:
        opt = opt.strip()
        if not opt:
            raise ValueError("Options must not be empty strings")
        if len(opt) > 500:
            raise ValueError("Each option must be 500 characters or fewer")
        cleaned.append(_sanitize(opt))
    return cleaned
```

- [ ] **Step 4: Run tests**

Run: `PYTHONPATH=src python -m pytest tests/test_evaluations_admin.py tests/test_validation_errors.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/backend/dto/admin.py
git commit -m "fix(backend): sanitize admin user full_name + assessment descriptions + question options"
```

---

## Task 5: Add Comprehensive Validation Tests

**Files:**
- Modify: `tests/test_validation_errors.py`
- Create: `tests/test_dto_validation.py`

**Interfaces:**
- Consumes: All DTOs from Task 2-4
- Produces: 422 responses for all invalid inputs; green test suite

- [ ] **Step 1: Write tests for Skill DTO validation**

```python
"""DTO validation tests — ensures all admin CRUD DTOs reject invalid input with 422."""

import uuid

def _fresh(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestSkillDtoValidation:
    """SkillCreate/SkillUpdate validation rules."""

    def test_skill_name_required(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills", json={}, headers=admin_headers)
        assert r.status_code == 422

    def test_skill_name_too_long(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": "x" * 101}, headers=admin_headers)
        assert r.status_code == 422

    def test_skill_name_markup_stripped(self, api_client, admin_headers):
        name = _fresh("SafeSkill")
        r = api_client.post("/api/admin/skills",
                            json={"name": f"<b>{name}</b>"}, headers=admin_headers)
        assert r.status_code == 200
        assert "<" not in r.json()["name"]
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_description_too_long(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "description": "x" * 2001},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_description_sanitized(self, api_client, admin_headers):
        name = _fresh("S")
        r = api_client.post("/api/admin/skills",
                            json={"name": name, "description": "<script>alert(1)</script>ok"},
                            headers=admin_headers)
        assert r.status_code == 200
        assert "<script>" not in r.json()["description"]
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_difficulty_level_range(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "difficulty_level": 0},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_difficulty_level_over_max(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "difficulty_level": 6},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_color_invalid_hex(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "color": "not-a-color"},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_color_valid_hex(self, api_client, admin_headers):
        name = _fresh("S")
        r = api_client.post("/api/admin/skills",
                            json={"name": name, "color": "#ff00aa"},
                            headers=admin_headers)
        assert r.status_code == 200
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_color_3_digit_hex(self, api_client, admin_headers):
        name = _fresh("S")
        r = api_client.post("/api/admin/skills",
                            json={"name": name, "color": "#abc"},
                            headers=admin_headers)
        assert r.status_code == 200
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_icon_too_long(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "icon": "x" * 101},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_icon_sanitized(self, api_client, admin_headers):
        name = _fresh("S")
        r = api_client.post("/api/admin/skills",
                            json={"name": name, "icon": "<img onerror=alert(1)>"},
                            headers=admin_headers)
        assert r.status_code == 200
        assert "<" not in r.json()["icon"]
        api_client.delete(f"/api/admin/skills/{r.json()['id']}", headers=admin_headers)

    def test_skill_estimated_hours_negative(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "estimated_hours": -1},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_prerequisite_ids_must_be_positive(self, api_client, admin_headers):
        r = api_client.post("/api/admin/skills",
                            json={"name": _fresh("S"), "prerequisite_ids": [0]},
                            headers=admin_headers)
        assert r.status_code == 422

    def test_skill_update_color_invalid(self, api_client, admin_headers):
        created = api_client.post("/api/admin/skills",
                                  json={"name": _fresh("S")},
                                  headers=admin_headers).json()
        r = api_client.put(f"/api/admin/skills/{created['id']}",
                           json={"color": "bad"}, headers=admin_headers)
        assert r.status_code == 422
        api_client.delete(f"/api/admin/skills/{created['id']}", headers=admin_headers)

    def test_skill_update_description_sanitized(self, api_client, admin_headers):
        created = api_client.post("/api/admin/skills",
                                  json={"name": _fresh("S")},
                                  headers=admin_headers).json()
        r = api_client.put(f"/api/admin/skills/{created['id']}",
                           json={"description": "<b>bold</b> text"},
                           headers=admin_headers)
        assert r.status_code == 200
        assert "<b>" not in r.json()["description"]
        api_client.delete(f"/api/admin/skills/{created['id']}", headers=admin_headers)
```

- [ ] **Step 2: Write tests for Category, Resource, Job Role DTO validation**

```python
class TestCategoryDtoValidation:
    def test_category_description_sanitized(self, api_client, admin_headers):
        name = _fresh("Cat")
        r = api_client.post("/api/admin/categories",
                            json={"name": name, "description": "<script>x</script>"},
                            headers=admin_headers)
        assert r.status_code == 200
        assert "<script>" not in r.json()["description"]
        api_client.delete(f"/api/admin/categories/{r.json()['id']}", headers=admin_headers)


class TestResourceDtoValidation:
    def test_resource_update_title_sanitized(self, api_client, admin_headers):
        created = api_client.post("/api/admin/resources", json={
            "title": _fresh("R"), "url": "https://example.com", "type": "article",
        }, headers=admin_headers).json()
        r = api_client.put(f"/api/admin/resources/{created['id']}",
                           json={"title": "<img onerror=alert(1)>"},
                           headers=admin_headers)
        assert r.status_code == 200
        assert "<" not in r.json()["title"]
        api_client.delete(f"/api/admin/resources/{created['id']}", headers=admin_headers)

    def test_resource_update_url_invalid_scheme(self, api_client, admin_headers):
        created = api_client.post("/api/admin/resources", json={
            "title": _fresh("R"), "url": "https://example.com", "type": "article",
        }, headers=admin_headers).json()
        r = api_client.put(f"/api/admin/resources/{created['id']}",
                           json={"url": "javascript:alert(1)"},
                           headers=admin_headers)
        assert r.status_code == 422
        api_client.delete(f"/api/admin/resources/{created['id']}", headers=admin_headers)

    def test_resource_type_sanitized_lowercase(self, api_client, admin_headers):
        name = _fresh("R")
        r = api_client.post("/api/admin/resources", json={
            "title": name, "url": "https://example.com", "type": "ARTICLE",
        }, headers=admin_headers)
        assert r.status_code == 200
        assert r.json()["type"] == "article"
        api_client.delete(f"/api/admin/resources/{r.json()['id']}", headers=admin_headers)


class TestJobRoleDtoValidation:
    def test_job_role_description_sanitized(self, api_client, admin_headers):
        title = _fresh("Role")
        r = api_client.post("/api/admin/job-roles",
                            json={"title": title, "description": "<b>bold</b>"},
                            headers=admin_headers)
        assert r.status_code == 200
        assert "<b>" not in r.json()["description"]
        api_client.delete(f"/api/admin/job-roles/{r.json()['id']}?force=true",
                          headers=admin_headers)

    def test_job_role_update_skill_ids_must_be_positive(self, api_client, admin_headers):
        created = api_client.post("/api/admin/job-roles",
                                  json={"title": _fresh("Role")},
                                  headers=admin_headers).json()
        r = api_client.put(f"/api/admin/job-roles/{created['id']}",
                           json={"skill_ids": [0]},
                           headers=admin_headers)
        assert r.status_code == 422
        api_client.delete(f"/api/admin/job-roles/{created['id']}?force=true",
                          headers=admin_headers)
```

- [ ] **Step 3: Write tests for Admin User and Assessment DTO validation**

```python
class TestAdminUserDtoValidation:
    def test_admin_user_full_name_sanitized(self, api_client, admin_headers):
        email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        r = api_client.post("/api/admin/users", json={
            "email": email, "password": "Strong@123",
            "full_name": "<script>alert(1)</script>",
        }, headers=admin_headers)
        assert r.status_code == 200
        assert "<script>" not in r.json()["full_name"]
        api_client.delete(f"/api/admin/users/{r.json()['id']}", headers=admin_headers)

    def test_admin_user_update_full_name_sanitized(self, api_client, admin_headers):
        email = f"test_{uuid.uuid4().hex[:6]}@example.com"
        created = api_client.post("/api/admin/users", json={
            "email": email, "password": "Strong@123",
        }, headers=admin_headers).json()
        r = api_client.put(f"/api/admin/users/{created['id']}",
                           json={"full_name": "<b>X</b>"},
                           headers=admin_headers)
        assert r.status_code == 200
        assert "<b>" not in r.json()["full_name"]
        api_client.delete(f"/api/admin/users/{created['id']}", headers=admin_headers)


class TestQuestionDtoValidation:
    def test_question_options_empty_string_rejected(self, api_client, admin_headers):
        # Create assessment first
        r = api_client.post("/api/admin/assessments", json={
            "title": _fresh("Assess"), "skill_id": None,
        }, headers=admin_headers)
        assert r.status_code == 200
        aid = r.json()["id"]
        qr = api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q?", "options": ["", "B"], "correct_index": 1,
        }, headers=admin_headers)
        assert qr.status_code == 422
        api_client.delete(f"/api/admin/assessments/{aid}", headers=admin_headers)

    def test_question_options_too_long(self, api_client, admin_headers):
        r = api_client.post("/api/admin/assessments", json={
            "title": _fresh("Assess"), "skill_id": None,
        }, headers=admin_headers)
        aid = r.json()["id"]
        qr = api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q?", "options": ["x" * 501, "B"], "correct_index": 1,
        }, headers=admin_headers)
        assert qr.status_code == 422
        api_client.delete(f"/api/admin/assessments/{aid}", headers=admin_headers)

    def test_question_options_sanitized(self, api_client, admin_headers):
        r = api_client.post("/api/admin/assessments", json={
            "title": _fresh("Assess"), "skill_id": None,
        }, headers=admin_headers)
        aid = r.json()["id"]
        qr = api_client.post(f"/api/admin/assessments/{aid}/questions", json={
            "prompt": "Q?",
            "options": ["<b>bold</b>", "plain"],
            "correct_index": 0,
        }, headers=admin_headers)
        assert qr.status_code == 200
        assert "<b>" not in qr.json()["options"][0]
        api_client.delete(f"/api/admin/assessments/{aid}", headers=admin_headers)
```

- [ ] **Step 4: Run all tests**

Run: `PYTHONPATH=src python -m pytest tests/ -v`
Expected: all pass (305+ tests)

- [ ] **Step 5: Commit**

```bash
git add tests/test_dto_validation.py tests/test_validation_errors.py
git commit -m "test(backend): comprehensive DTO validation tests for all admin CRUD entities"
```

---

## Task 6: Final Verification

- [ ] **Step 1: Run full test suite**

Run: `PYTHONPATH=src python -m pytest tests/ -q`
Expected: 305+ tests pass

- [ ] **Step 2: Run frontend checks**

Run: `cd src/admin-app && pnpm check && pnpm build`
Expected: 0 errors, 0 warnings

- [ ] **Step 3: Run backend type checks (if configured)**

Run: `PYTHONPATH=src python -c "from backend.dto.catalog import SkillCreate, SkillUpdate, CategoryCreate, CategoryUpdate, ResourceCreate, ResourceUpdate, JobRoleCreate, JobRoleUpdate; from backend.dto.admin import AdminCreateUser, AdminUserUpdate, AssessmentCreate, AssessmentUpdate, QuestionCreate, QuestionUpdate; print('All DTOs import OK')"`
Expected: `All DTOs import OK`

- [ ] **Step 4: Manual smoke test**

1. Start backend: `source .venv/bin/activate && PYTHONPATH=src python run.py`
2. Start admin app: `cd src/admin-app && pnpm dev`
3. Login as admin
4. Create a skill with `color: "not-hex"` → expect 422
5. Create a skill with valid data → expect success, skill appears in list
6. Edit a skill, set `icon: "<script>"` → expect sanitized on save
7. Create a resource, set `url: "ftp://..."` → expect 422
8. Create a user, set `full_name: "<b>X</b>"` → expect sanitized
9. Navigate away from skills page and back → skill still listed (no stale cache)

---

## Summary of Changes

| File | Entity | Change |
|------|--------|--------|
| `src/backend/dto/catalog.py` | Skills | Wire `_self_or_clean_hex` for color; add icon max_length+sanitize; add description sanitize; wire `_check_positive` for prerequisite_ids |
| `src/backend/dto/catalog.py` | Categories | Add description sanitize to Create+Update |
| `src/backend/dto/catalog.py` | Resources | Add title+URL validators to Update; add type+language+author sanitize to both |
| `src/backend/dto/catalog.py` | Job Roles | Add description+career_field sanitize; add skill_ids validator to Update |
| `src/backend/dto/admin.py` | Users | Add full_name sanitize to AdminCreateUser+AdminUserUpdate |
| `src/backend/dto/admin.py` | Assessments | Add description sanitize to Create+Update |
| `src/backend/dto/admin.py` | Questions | Add options sanitize+length-cap to Create+Update |
| `src/admin-app/src/routes/(app)/skills/+page.svelte` | — | Replace `$effect` with `onMount`; add icon validator |
| `src/admin-app/src/routes/(app)/*/+page.svelte` | — | Replace `$effect` with `onMount` on all 6 CRUD pages |
| `src/admin-app/src/lib/stores/sse.ts` | — | Add entity cache invalidation for mutation events |
| `tests/test_dto_validation.py` | — | New: ~30 validation tests |
