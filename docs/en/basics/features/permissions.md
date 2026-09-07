# Permission System

FastBrace provides a fine-grained permission system based on **resources + operation levels**, supporting permission tree management, role-permission configuration, and frontend page access control.

## Core Concepts

- **Permission resources**: Permissions are defined along "module + operation" dimensions, such as "User Management - View" and "User Management - Edit"
- **Permission levels**: A three-level hierarchy — View (Level 1), Operate (Level 2), and Export (Level 3)
- **Permission tree**: Permission resources are organized as a tree, making it easy to tick permissions when creating roles
- **Role-permission binding**: Each role is associated with a set of permission configuration stored in JSON format
- **Frontend access control**: Fine-grained permission endpoints return the pages and operations the current user can access, for dynamic rendering on the frontend

## File Locations

| File | Description |
|------|------|
| `api/permission.py` | Permission management API routes |
| `api/request_body/permission_request.py` | Permission request bodies |
| `api/response_body/permission_response.py` | Permission response bodies |
| `domain/service/permission_service.py` | Permission domain service |
| `domain/entity/permission_resource.py` | Permission resource entity |
| `domain/repo/permission_resource_repo.py` | Permission resource repository |
| `infrastructure/models/permission_resources.py` | Permission resource database model |
| `infrastructure/core/permissions_limit.py` | Permission verification decorators |
| `db/create_permission_resources_table.sql` | SQL for creating the permission resource table |

## API Endpoints

| Method | Path | Description |
|------|------|------|
| GET | `/permissions/tree` | Get the permission tree (for role configuration) |
| GET | `/permissions/role/{role_id}` | Get the permission tree of a specific role |
| POST | `/permissions/role/save` | Save role permission configuration |
| GET | `/permissions/role/{role_id}/detailed` | Get a role's fine-grained permissions (for the frontend) |
| GET | `/permissions/user/detailed` | Get the current user's fine-grained permissions |
| POST | `/permissions/validate` | Validate whether a user has a specific permission |
| GET | `/permissions/system/info` | Get permission system info |

## Usage

### Endpoint-Level Permission Control

Use the `require_admin()` or `require_permission()` decorators in API routes:

```python
from infrastructure.core.permissions_limit import require_admin

@user_router.post("", dependencies=[Depends(require_admin())])
async def add_user(...):
    ...
```

### Initializing Permission Resources

Run the script to initialize permission resource data:

```bash
python scripts/permission_init.py
```

> For a detailed guide to the permission system, see [Advanced - Permission System](/en/advanced/permission).
