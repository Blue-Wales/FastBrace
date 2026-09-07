# User Management

FastBrace provides an out-of-the-box user management module covering the full set of features: user CRUD, password management, status control, and more.

## Core Concepts

- **User CRUD**: Create, edit, and delete users, plus paginated queries of the user list
- **Password management**: Users can change their own password and admins can reset passwords; passwords are stored as bcrypt hashes
- **Status control**: Enable/disable user accounts in batch
- **Avatar management**: Users can link an avatar file, uploaded through the file module

## File Locations

| File | Description |
|------|------|
| `api/user.py` | User management API routes |
| `api/request_body/user_request.py` | User request bodies (create/edit/password/status) |
| `api/response_model/user_res_model.py` | User response models |
| `application/user_app.py` | User application service layer |
| `domain/service/user_service.py` | User domain service |
| `domain/entity/user.py` | User entity |
| `domain/repo/user_repo.py` | User repository implementation |
| `infrastructure/models/user.py` | User database model (SQLAlchemy) |

## API Endpoints

| Method | Path | Description |
|------|------|------|
| POST | `/users` | Create a user (admin permission required) |
| GET | `/users` | Get the user list (paginated, filterable) |
| GET | `/users/me` | Get the currently logged-in user's info |
| GET | `/users/choices` | Get the list of user names (for dropdown selection) |
| GET | `/users/{user_id}` | Get user details |
| POST | `/users/{user_id}` | Edit a user |
| DELETE | `/users/{user_id}` | Delete a user (admin permission required) |
| POST | `/users/me/password` | Change the current user's password |
| POST | `/users/{user_id}/password` | Change a specific user's password |
| POST | `/users/batch/status` | Batch-update user status (admin permission required) |
