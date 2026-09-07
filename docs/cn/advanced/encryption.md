# 加密通信

FastBrace 支持 **RSA-OAEP-SHA256** 非对称加密保护登录密码传输。前端使用公钥加密密码，后端使用私钥解密，确保密码不在网络中明文传输。

## 设计思想

### 为什么需要 RSA 加密？

传统的 HTTPS 可以保护传输层安全，但在以下场景中仍需要应用层加密：
- 反向代理（如 Nginx）终止 TLS 后，内部网络明文传输
- 前端日志或调试工具可能记录请求体
- 满足等保合规要求

### 加密流程

![RSA](https://picgocloud.com/m/fb7c6c5e-bc3d-4a63-bd9d-1a93b340f525.png)

**关键设计决策：**
- 公钥从私钥自动推导，无需单独配置公钥
- 支持通过配置动态开关加密（`rsa.enabled`），前端据此决定加密策略
- 使用 OAEP + SHA256 填充方案，安全性优于 PKCS1 v1.5



## 配置步骤

### 第一步：生成 RSA 密钥对

在项目根目录执行：

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

### 第二步：配置后端私钥

**生产环境（推荐）：通过环境变量注入**

```ini
RSA__ENABLED=true
RSA__PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAA...
-----END PRIVATE KEY-----"
```

> 环境变量使用 `__` 双下划线作为嵌套分隔符，由 Pydantic Settings 自动解析。

**开发环境：直接写入配置文件**

编辑 `infrastructure/config/settings.dev.yaml`：

```yaml
rsa:
  enabled: true
  key_size: 2048
  private_key: |
    -----BEGIN PRIVATE KEY-----
    MIIEvQIBADANBgkqhkiG9w0BAQEFAA...
    -----END PRIVATE KEY-----
```

> 私钥绝对不能提交到代码仓库，生产环境务必使用环境变量注入。

### 第三步：前端集成

**3.1 获取公钥**

```
GET /security/public-key
```

响应：

```json
{
  "data": {
    "encryption_enabled": true,
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjAN...",
    "algorithm": "RSA-OAEP-SHA256"
  }
}
```

**3.2 使用 jsencrypt 加密密码**

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

**3.3 发起登录请求**

```javascript
const formData = new FormData();
formData.append('username', username);
formData.append('encrypted_password', encryptedPassword);

const res = await fetch('/login', { method: 'POST', body: formData });
```

### 第四步：验证配置

```bash
curl http://localhost:8000/security/public-key
```

响应中 `encryption_enabled: true` 且 `public_key` 有值即为成功。

## 常见问题

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `RSA解密失败` | 私钥未配置或格式错误 | 检查环境变量 `RSA__PRIVATE_KEY` |
| `RSA加密已启用，请使用encrypted_password` | 前端发送了明文密码 | 改用 `encrypted_password` 字段 |
| 公钥接口 500 错误 | 私钥格式不正确 | 确保包含完整的 `BEGIN/END PRIVATE KEY` 头尾 |
