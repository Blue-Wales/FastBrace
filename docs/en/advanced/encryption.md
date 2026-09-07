# Encrypted Communication

FastBrace supports **RSA-OAEP-SHA256** asymmetric encryption to protect login password transmission. The frontend encrypts the password with the public key and the backend decrypts it with the private key, ensuring passwords never travel the network in plaintext.

## Design Philosophy

### Why RSA Encryption?

Traditional HTTPS protects the transport layer, but application-layer encryption is still needed in the following scenarios:
- After a reverse proxy (e.g., Nginx) terminates TLS, traffic travels in plaintext inside the internal network
- Frontend logs or debugging tools may record request bodies
- Compliance with MLPS (Multi-Level Protection Scheme) requirements

### Encryption Flow

![rsa-flow](https://picgocloud.com/m/866da8df-ce1e-463c-b28a-a49f26d05573.png)

**Key design decisions:**
- The public key is derived automatically from the private key — no separate public key configuration needed
- Encryption can be toggled dynamically via configuration (`rsa.enabled`); the frontend decides its strategy accordingly
- Uses the OAEP + SHA256 padding scheme, which is more secure than PKCS1 v1.5

## Configuration Steps

### Step 1: Generate an RSA Key Pair

Run in the project root:

```bash
python -c "
from infrastructure.utils.rsa_utils import RSAUtils
priv, pub = RSAUtils.generate_key_pair(2048)
print('===== 私钥 =====')
print(priv)
print('===== 公钥 =====')
print(pub)
"
```

### Step 2: Configure the Backend Private Key

**Production (recommended): inject via environment variables**

```ini
RSA__ENABLED=true
RSA__PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAA...
-----END PRIVATE KEY-----"
```

> Environment variables use the `__` double underscore as the nesting separator, parsed automatically by Pydantic Settings.

**Development: write directly to the configuration file**

Edit `infrastructure/config/settings.dev.yaml`:

```yaml
rsa:
  enabled: true
  key_size: 2048
  private_key: |
    -----BEGIN PRIVATE KEY-----
    MIIEvQIBADANBgkqhkiG9w0BAQEFAA...
    -----END PRIVATE KEY-----
```

> Never commit the private key to the code repository; always inject it via environment variables in production.

### Step 3: Frontend Integration

**3.1 Fetch the public key**

```
GET /security/public-key
```

Response:

```json
{
  "data": {
    "encryption_enabled": true,
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjAN...",
    "algorithm": "RSA-OAEP-SHA256"
  }
}
```

**3.2 Encrypt the password with jsencrypt**

```bash
npm install jsencrypt
```

```javascript
import JSEncrypt from 'jsencrypt';

async function encryptPassword(plainPassword) {
  const res = await fetch('/security/public-key');
  const { data } = await res.json();
  if (!data.encryption_enabled) return { password: plainPassword };

  const encryptor = new JSEncrypt();
  encryptor.setPublicKey(data.public_key);
  const encrypted = encryptor.encrypt(plainPassword);
  return { encrypted_password: encrypted };
}
```

**3.3 Send the login request**

```javascript
const formData = new FormData();
formData.append('username', username);
formData.append('encrypted_password', encryptedPassword);

const res = await fetch('/login', { method: 'POST', body: formData });
```

### Step 4: Verify the Configuration

```bash
curl http://localhost:8000/security/public-key
```

Success means `encryption_enabled: true` and a non-empty `public_key` in the response.

## Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `RSA decryption failed` | Private key not configured or malformed | Check the `RSA__PRIVATE_KEY` environment variable |
| `RSA encryption is enabled, please use encrypted_password` | Frontend sent a plaintext password | Use the `encrypted_password` field instead |
| Public key endpoint returns 500 | Incorrect private key format | Make sure the full `BEGIN/END PRIVATE KEY` header and footer are present |
