# Login & Authentication

FastBrace ships with a complete authentication and login system built on **OAuth2 + JWT**, supporting RSA-encrypted password transmission and multi-role selection.

## Core Concepts

- **OAuth2 password flow**: Authenticates with username/password, and the server issues a JWT token
- **RSA encryption**: The frontend encrypts the password with an RSA public key and the backend decrypts it with the private key, preventing man-in-the-middle interception
- **Multi-role switching**: A role can be selected at login; after logging in, roles can be switched dynamically and the token refreshed
- **Token refresh**: Silently renews the access token via refresh_token

## File Locations

| File | Description |
|------|------|
| `api/login.py` | Login and authentication API routes |
| `api/request_body/user_request.py` | Login request body definitions |
| `infrastructure/utils/oauth2_tools.py` | OAuth2 / JWT utilities |
| `infrastructure/utils/rsa_utils.py` | RSA encryption/decryption utilities |
| `domain/service/user_service.py` | User domain service (includes login logic) |

## API Endpoints

| Method | Path | Description |
|------|------|------|
| POST | `/login` | Username/password login (form-data) |
| POST | `/switch-role` | Switch user role |
| GET | `/users/{username}/roles` | Get the user's role list |
| POST | `/refresh-token` | Refresh token |
| POST | `/logout` | Log out |
| GET | `/current-role` | Get current role info |
