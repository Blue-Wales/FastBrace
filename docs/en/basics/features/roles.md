# Role Management

FastBrace ships with a role management system built on a **tree structure**, supporting hierarchical relationships between roles and many-to-many role-user associations.

## Core Concepts

- **Role tree**: Roles support parent-child hierarchy, stored with the Closure Table model, making it easy to query child roles at any depth
- **Role CRUD**: Create, edit, and delete roles, and get role details
- **Role-user association**: Add users to a role, remove users from a role, and query the list of users under a role
- **Role switching**: Users can select a role at login, or switch dynamically after logging in

## File Locations

| File | Description |
|------|------|
| `api/role.py` | Role management API routes |
| `api/request_body/role_request.py` | Role request bodies (create/edit/user association) |
| `api/response_model/role_res_model.py` | Role response models |
| `application/role_app.py` | Role application service layer |
| `domain/service/role_service.py` | Role domain service |
| `domain/entity/role.py` | Role entity |
| `domain/repo/role_repo.py` | Role repository implementation |
| `infrastructure/models/role.py` | Role database model |
| `db/create_roles_table.sql` | SQL for creating the role table |
| `db/create_role_closure_table.sql` | SQL for creating the role closure table |

## API Endpoints

| Method | Path | Description |
|------|------|------|
| POST | `/role/add` | Add a role (admin permission required) |
| GET | `/role/tree` | Get the role tree |
| POST | `/role/edit` | Edit a role (admin permission required) |
| POST | `/role/user_list` | Get the paginated list of users associated with a role |
| GET | `/role/info` | Get role info |
| DELETE | `/role/delete` | Delete a role (admin permission required) |
| POST | `/role/add_users` | Add users to a role (admin permission required) |
| DELETE | `/role/delete_users` | Remove users from a role (admin permission required) |
