# Integrating vben-vue-admin

FastBrace is positioned as a **backend service framework that can integrate with any frontend**. This article uses the open source frontend solution [vben-vue-admin](https://github.com/vbenjs/vue-vben-admin) (Vue 3 + Ant Design Vue + Vite) as an example to walk through the complete frontend–backend integration: login authentication, RSA password encryption, permission integration, and deployment.

## Overall Architecture

```text
Browser
  └── vben-vue-admin (frontend, Vite DevServer / Nginx)
        └── HTTP API (REST + JSON, Bearer Token)
              └── FastBrace (backend, Uvicorn)
                    ├── MySQL (business data)
                    └── Redis (cache / login state)
```

The frontend and backend are fully decoupled: during development, API calls are forwarded through the Vite proxy; in production, Nginx provides unified reverse proxying, avoiding cross-origin issues.

## Prerequisites

| Dependency | Version | Notes |
| -------- | ------------------------ | ----------------------------- |
| Node.js  | 18+ (20+ recommended)    | Frontend build environment    |
| pnpm     | 8+                       | Package manager recommended by vben |
| Backend environment | See [Quick Start](/en/intro/getting-started) | MySQL / Redis / uv |

## Step 1: Start FastBrace

```bash
# 1. Initialize the database (run the table-creation SQL under the db/ directory)
# 2. Start the backend service
python main.py server api
```

After startup, visit `http://127.0.0.1:8000/docs` to confirm the Swagger documentation is available.

> The backend CORS middleware defaults to `allow_origins=["*"]`, so local integration won't be blocked by cross-origin policies; in production, tighten it to specific domains or serve everything behind a same-domain Nginx reverse proxy (see Deployment below).

## Step 2: Configure the Frontend API Address

Clone and start vben-vue-admin:

```bash
git clone https://github.com/vbenjs/vue-vben-admin.git
cd vue-vben-admin
pnpm install
pnpm serve
```

Edit `.env.development` to point the API address at FastBrace (using the vben 2.x directory layout as an example):

```ini
# .env.development
VITE_GLOB_API_URL=/api
```

Then configure the proxy in `vite.config.ts` (or `build/vite/proxy.ts`) to forward `/api` to the backend and strip the prefix:

```ts
proxy: {
  '/api': {
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
    ws: false,
  },
},
```

> The configuration file location varies slightly across vben versions (2.x uses `build/vite/proxy.ts`; 5.x is a monorepo layout), so refer to the official docs; the core idea is always the same: "frontend requests `/api/**` → the proxy forwards them to the FastBrace root path".

## Step 3: Integrate Login Authentication

FastBrace issues JWTs using the **standard OAuth2 password flow**:

```text
POST /login        Content-Type: multipart/form-data
  username=xxx
  password=xxx     # Optional: RSA-encrypted ciphertext
  role_id=1        # Optional: role selection for multi-role users

Response:
{
  "access_token": "...",
  "refresh_token": "...",
  "code": 200
}
```

Frontend adaptation points:

1. **Login request**: vben's login API sends a JSON body by default, so change it to `form-data` submission in `src/api/sys/user.ts`, or use axios with `URLSearchParams` directly;
2. **Token handling**: subsequent requests add `Authorization: Bearer <access_token>` to the request header (vben already uses the Bearer scheme by default);
3. **Token refresh**: after `access_token` expires, call `POST /refresh-token` (passing `refresh_token` as `form-data`) to obtain a new token and update local storage;
4. **Multi-role switching**: FastBrace provides a `/switch-role` endpoint; you can add a "switch role" entry on the vben home page so that one account can switch among multiple roles.

After a successful login, the frontend calls `GET /users/me` to fetch the current user's profile and role information and populate vben's user state; on logout it calls `POST /logout` to revoke the token.

### Optional: Enable RSA Password Encryption

If RSA is configured on the backend (see [Encrypted Communication](/en/advanced/encryption)), the login flow is:

```text
1. GET /security/public-key   →  Fetch the public_key and fingerprint
2. The frontend encrypts the password with jsencrypt using the public key (RSA-OAEP-SHA256)
3. POST /login submits the ciphertext
```

FastBrace provides an out-of-the-box frontend encryption integration (see [Encrypted Communication](/en/advanced/encryption#step-3-frontend-integration)). You can use jsencrypt to encrypt the password directly in vben's login module; when the encryption switch is off, it automatically falls back to plaintext submission.

## Step 4: Integrate Permissions and Menus

vben supports two menu modes; choose based on your team's preference:

| Mode         | Menu source                    | Best for                       |
| ------------ | ------------------------------ | ------------------------------ |
| Frontend mode | vben's local route table       | Quick start, fixed menus       |
| Backend mode | Fetch the menu tree from the API after login | Menus that change dynamically with roles (recommended) |

When using the backend mode, simply map FastBrace's permission endpoints to vben's expected menu endpoint:

- FastBrace: `GET /permissions/tree` (permission tree), `GET /permissions/role/{role_id}` (role permission tree), `GET /permissions/user/detailed` (current user's fine-grained permissions);
- Have the backend return menu JSON compatible with vben's `getMenuList` structure (`meta.title`, `path`, `icon`, etc.), or do a one-time field conversion on the vben side.

See [Permission System](/en/advanced/permission) for API-level permission control — the backend validates via permission decorators, while the frontend uses vben's `RoleEnum` / button permission directives to control button visibility, with both ends sharing the same set of permission codes.

## Step 5: Business Module Integration

Once login works, build business modules following a "one backend module + one frontend page" approach:

1. Backend: generate module APIs following the [Architecture Guide](/en/advanced/architecture/api-layer) or [Skill](/en/advanced/engineering/skill);
2. Frontend: wrap requests per module under vben's `src/api/`, and reuse its table and form components in pages;
3. Integration: verify in parallel via Swagger (`/docs`) and the frontend pages, or let the AI verify automatically through MCP (see [MCP](/en/advanced/engineering/mcp)).

Common capabilities such as file upload and Excel import/export are already built into the backend; the frontend can integrate them as ordinary form flows.

## Step 6: Deployment

For production, a same-domain Nginx reverse proxy is recommended to avoid cross-origin and Cookie issues:

```nginx
server {
    listen 80;
    server_name admin.example.com;

    # Frontend static assets (vben build output)
    location / {
        root /var/www/vben-dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API reverse proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

For containerized backend deployment, see the [Deployment Guide](/en/advanced/engineering/deployment-guide); for the automated release flow, see the [CI/CD Pipeline Guide](/en/advanced/engineering/cicd-pipeline).

## FAQ

### 1. Login returns 422

The FastBrace login endpoint expects `form-data` (per the OAuth2 spec); submitting JSON will fail parameter validation. Make sure the request header is `multipart/form-data`.

### 2. APIs return 401

Check that requests carry `Authorization: Bearer <access_token>`; refresh the token first if it has expired. During development, requests also often hit the frontend's own port because the Vite proxy isn't taking effect.

### 3. RSA decryption fails

A backend error saying "RSA decryption failed" means the submitted value isn't valid ciphertext: make sure `/security/public-key` was called first and that the public key of the **current backend instance** is being used (after restarting the backend and rotating the key pair, cached old public keys become invalid).

### 4. Permission buttons not showing

Permission codes in the backend permission tree must exactly match the role/button codes configured in vben on the frontend — pay attention to case and underscores.

## Next Steps

- Details of the backend permission model: [Permission System](/en/advanced/permission)
- Speed up frontend–backend integration with AI: [Skill](/en/advanced/engineering/skill), [MCP](/en/advanced/engineering/mcp)
