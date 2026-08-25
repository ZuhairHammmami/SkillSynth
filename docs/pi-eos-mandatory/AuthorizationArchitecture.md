# Authorization Architecture

## Role Hierarchy
```
super_admin — full system access
    │
    ├── admin — user management, content management, analytics
    │
    ├── editor — content management (skills, categories, resources, paths)
    │
    ├── content_manager — resource management only
    │
    ├── student — learning paths, assessments, own profile only
    │
    └── viewer — read-only access to specific resources
```

## Guard Implementation
```python
# Router-level guard (applies to ALL endpoints in router)
router = APIRouter(dependencies=[Depends(get_current_admin_user)])

# Endpoint-level guard
@router.get("/api/auth/me")
def read_current_user(current_user: Profile = Depends(get_current_user)):
    ...

# Permission-level guard
@router.post("/api/admin/users")
def create_user(..., current_user: Profile = Depends(require_permission("manage_users"))):
    ...
```

## Protected Routes
All admin routes (`/api/admin/*`) → `get_current_admin_user`
All student routes (`/api/learning/*`, `/api/paths/*`, etc.) → `get_current_user`
Auth routes (`/api/auth/token`, `/api/auth/register`) → public

## Frontend Guards
- **Middleware**: JWT cookie check on learner + admin routes → redirect to `/login`
- **Admin Guard**: `AdminGuard.tsx` component checks `is_admin` → redirect to `/dashboard`
- **Auth Routes**: Redirect to `/dashboard` if already authenticated
