# Permission System

The FastBrace permission system is designed around a **"Module + Action Level"** model. It persists permission resources in the database, enforces endpoint-level access control through decorators, and ships an initialization script for one-shot deployment — a complete permission management solution from development to production.

## Design Philosophy

### Permission Model

The permission system uses a **two-level structure**:

```
Module                      Action
├── Dashboard               └── View
├── UserManage
│   ├── Account             ├── View / Edit / Export
│   ├── Role                ├── View / Edit / Export
│   └── Department          ├── View / Edit / Export
```

- **Module level**: corresponds to a business domain (e.g., user management, role management), defined by the `Permissions` enum
- **Action level**: the action types under each module; the `PermissionLevel` enum defines three permission levels
- **Permission storage**: a role's permissions are stored as JSON in the `roles.permissions` field, keyed by module code with an array of levels as the value

### Permission Verification Flow

```
Request → OAuth2 token parsing → fetch user permissions → require_permission() decorator check → allow / deny
```

The framework provides four permission verification approaches for different scenarios:

| Decorator | Purpose | Typical Scenario |
|-----------|---------|------------------|
| `require_permission()` | Function permission check | Regular endpoints (View/Edit/Export) |
| `require_role()` | Role check | Restrict access to specific roles |
| `require_admin()` | Admin check | System administration operations |
| `require_permission_expression()` | Expression-based permission check | Complex permission combinations |

## Core Code Locations

| File | Responsibility |
|------|----------------|
| `infrastructure/core/enum_var.py` | Permission module enum `Permissions` + permission level enum `PermissionLevel` |
| `infrastructure/core/permissions_limit.py` | Permission check decorators (`require_permission`, `require_admin`, etc.) |
| `infrastructure/models/permission_resources.py` | Permission resource ORM model |
| `domain/service/permission_service.py` | Permission domain service (permission tree building, verification logic) |
| `api/permission.py` | Permission management API endpoints |
| `scripts/permission_init.py` | **Permission resource initialization script** |
| `db/create_permission_resources_table.sql` | Permission resources table DDL |

## Configuration and Initialization

### Step 1: Define Permission Modules

Declare permission modules in `infrastructure/core/enum_var.py`:

```python
class Permissions(Enum):
    DASHBOARD = "Dashboard"
    USER_MANAGE = "UserManage"
    ACCOUNT = "UserManage.Account"
    ROLE = "UserManage.Role"
    DEPARTMENT = "UserManage.Department"

class PermissionLevel(BaseCodeLabelEnum):
    VIEW = (1, "查看")
    EDIT = (2, "操作")
    EXPORT = (3, "导出")
```

### Step 2: Run the Initialization Script

The framework provides the `scripts/permission_init.py` script, which automatically generates the resource tree from the permission constant configuration and writes it to the database:

```bash
# First-time initialization (skipped when data already exists)
python scripts/permission_init.py

# Force wipe and rebuild
python scripts/permission_init.py --force-recreate
```

Script execution flow:
1. Connects to the database and checks whether the permission resources table already contains data
2. Recursively builds the module → action → submodule permission resource tree from the `PERMISSION_MAPPING` constants
3. Bulk inserts into the `permission_resources` table
4. Automatically grants the super admin role all permissions

### Step 3: Apply Permission Checks to Endpoints

```python
from fastapi import APIRouter, Depends
from infrastructure.core.enum_var import Permissions, PermissionLevel
from infrastructure.core.permissions_limit import require_permission, require_admin

user_router = APIRouter()

# Requires the "UserManage - View" permission
@user_router.get(
    "",
    dependencies=[Depends(require_permission(
        permission_module=Permissions.ACCOUNT,
        required_permissions=[PermissionLevel.VIEW],
    ))],
)
async def get_users():
    ...

# Requires admin permission
@user_router.post(
    "",
    dependencies=[Depends(require_admin())],
)
async def create_user():
    ...
```

### Step 4: Verify the Permission Configuration

Verify that permissions are configured correctly through the API endpoints:

```bash
# Fetch the permission tree
curl -X GET "http://localhost:8000/permissions/tree" \
  -H "Authorization: Bearer <token>"

# Verify permissions for a specific module
curl -X POST "http://localhost:8000/permissions/validate" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_permissions": {...}, "module_code": "UserManage.Account", "required_level": 1}'
```

## Permission Data Storage Format

Role permissions are stored as JSON in the `roles.permissions` field:

```json
{
    "Dashboard": [1],
    "UserManage.Account": [1, 2, 3],
    "UserManage.Role": [1, 2]
}
```

Number meanings: `1` = View, `2` = Edit, `3` = Export.

## Adding a New Permission Module

1. Add the new module to the `Permissions` enum in `infrastructure/core/enum_var.py`
2. Add the corresponding `PERMISSION_MAPPING` entry to the permission constants configuration
3. Run `python scripts/permission_init.py --force-recreate` to rebuild the permission resources
4. Add the `@require_permission()` decorator to the target endpoint
